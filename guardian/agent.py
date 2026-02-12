import os
import time
import subprocess
from .git_ops import GitOps
from .analyzer import Analyzer
from .llm_client import LLMClient
from .gitea_client import GiteaClient

class SecurityAgent:
    def __init__(self):
        self.git_ops = GitOps()
        self.analyzer = Analyzer()
        self.llm = LLMClient()
        self.gitea = GiteaClient()

    def process_pr(self, pr_data):
        """
        Main workflow triggered by PR webhook.
        """
        repo_url = pr_data['repository']['clone_url']
        repo_name = pr_data['repository']['name']
        repo_owner_name = pr_data['repository']['owner']['username']
        pr_number = pr_data['number']
        branch_name = pr_data['pull_request']['head']['ref']
        
        print(f"Processing PR #{pr_number} in {repo_name}...")

        # 1. Clone Repo into unique directory to avoid lock issues on Windows
        repo_dir = f"{repo_name}_pr{pr_number}_{int(time.time())}"
        repo, repo_path = self.git_ops.clone_repo(repo_url, repo_dir)
        self.git_ops.checkout_branch(repo, branch_name)

        # 2. Analyze (Bandit)
        issues = self.analyzer.run_bandit(repo_path)
        
        if isinstance(issues, dict) and "error" in issues:
            print(f"Analysis failed: {issues['error']}")
            return

        if not issues:
            print("No security issues found.")
            return

        print(f"Found {len(issues)} issues. Starting fix cycle...")
        self.gitea.post_comment(repo_owner_name, repo_name, pr_number, 
                                f"🛡️ **Guardian Agent** found {len(issues)} security issues. Attempting fixes...")

        fixed_files = []
        
        # 3. Fix Cycle
        try:
            for issue in issues:
                filename = issue['filename']
                # Bandit returns distinct paths. usually relative to CWD if run with relative path.
                
                target_file = filename
                if not os.path.exists(target_file):
                    # Fallback: try joining
                    target_file = os.path.join(repo_path, filename)
                
                if not os.path.exists(target_file):
                    print(f"File not found: {target_file} (Original: {filename})")
                    continue

                with open(target_file, 'r') as f:
                    content = f.read()

                print(f"Fixing {issue['issue_text']} in {filename}...")
                
                # Call LLM
                fix_prompt = f"Fix the following security issue detected by Bandit:\n{issue}\nCode:\n"
                fixed_code = self.llm.generate_fix(fix_prompt, content)
                
                # Apply Fix
                with open(target_file, 'w') as f:
                    f.write(fixed_code)
                
                # 4. Verify (Basic Syntax Check)
                if self._validate_syntax(target_file):
                    print(f"Fix for {filename} validated successfully.")
                    # Git expects path relative to repo root
                    rel_path = os.path.relpath(target_file, repo_path)
                    if rel_path not in fixed_files:
                        fixed_files.append(rel_path)
                else:
                    print(f"Fix for {filename} failed validation. Reverting...")
                    with open(target_file, 'w') as f:
                        f.write(content) # Revert

            # 5. Push Changes (Outside loop, once all files processed)
            if fixed_files:
                self.git_ops.commit_and_push(repo, fixed_files, "chore: Security fixes by Guardian Agent", branch_name)
                self.gitea.post_comment(repo_owner_name, repo_name, pr_number, 
                                        f"✅ Applied fixes to: {', '.join(fixed_files)}")

        except Exception as e:
            import traceback
            error_msg = f"Agent Crash: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            self.gitea.post_comment(repo_owner_name, repo_name, pr_number, f"❌ Agent Crashed:\n```\n{error_msg}\n```")

    def _validate_syntax(self, filepath):
        """
        Checks if the file is valid python syntax.
        """
        try:
            subprocess.run(["python", "-m", "py_compile", filepath], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
