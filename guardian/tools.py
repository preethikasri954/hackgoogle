import os
import time
from .git_ops import GitOps
from .analyzer import Analyzer
from .llm_client import LLMClient
from .gitea_client import GiteaClient
import git

from typing import Any

# Initialize components
git_ops = GitOps()
bandit_analyzer = Analyzer()
llm = LLMClient()
gitea_client = GiteaClient()

def analyze_pr_vulnerabilities(repo_url: str, repo_name: str, pr_number: int, branch_name: str) -> dict:
    """
    Clones the repository for a specific PR and branch, and runs security analysis using Bandit.
    
    Args:
        repo_url: The clone URL of the repository.
        repo_name: The name of the repository.
        pr_number: The pull request ID.
        branch_name: The branch to analyze.
        
    Returns:
        A dictionary containing the list of security issues and the path to the cloned repository.
    """
    repo_dir = f"{repo_name}_pr{pr_number}_{int(time.time())}"
    repo, repo_path = git_ops.clone_repo(repo_url, repo_dir)
    git_ops.checkout_branch(repo, branch_name)
    
    issues = bandit_analyzer.run_bandit(repo_path)
    return {
        "status": "success",
        "issues": issues,
        "repo_path": repo_path,
        "branch_name": branch_name
    }

def fix_code_vulnerability(filename: str, line_number: int, issue_text: str, repo_path: str) -> dict:
    """
    Generates and applies a surgical security fix using SEARCH/REPLACE blocks.
    
    Args:
        filename: Path to the vulnerable file relative to repo root.
        line_number: The line number where the issue was detected.
        issue_text: Description of the vulnerability.
        repo_path: The absolute path to the local repository.
        
    Returns:
        A dictionary with the fix status.
    """
    target_file = os.path.join(repo_path, filename) if not os.path.isabs(filename) else filename
    
    if not os.path.exists(target_file):
        return {"status": "error", "message": f"File not found: {filename}"}

    with open(target_file, 'r') as f:
        content = f.read()

    print(f" [ADK Tool] Fixing '{issue_text}' in {filename} (line {line_number})...")
    
    # Construct a focused report for the LLM
    vulnerability_report = f"Vulnerability: {issue_text}\nLocation: {filename} (near line {line_number})"
    
    # Request surgical blocks from LLM
    blocks_text = llm.generate_fix(vulnerability_report, content)
    
    # Parse and apply blocks
    new_content = _apply_search_replace_blocks(content, blocks_text)
    
    if new_content == content:
        print(f" [ADK Tool] No changes applied to {filename}. Block might not have matched.")
        return {"status": "warning", "message": "No changes applied. Possible block match failure."}

    # Calculate diff for logging
    import difflib
    diff = difflib.unified_diff(
        content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f'a/{filename}',
        tofile=f'b/{filename}'
    )
    diff_text = "".join(diff)
    if diff_text:
        print(f" [ADK Tool] Diff for {filename}:\n{diff_text}")

    with open(target_file, 'w') as f:
        f.write(new_content)
        
    return {"status": "success", "filename": filename, "fixed_file_abs": target_file}

def _apply_search_replace_blocks(content: str, blocks_text: str) -> str:
    """
    Surgically applies SEARCH/REPLACE blocks to the content.
    """
    import re
    # Pattern to match SEARCH/REPLACE blocks
    pattern = r"<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE"
    blocks = re.findall(pattern, blocks_text, re.DOTALL)
    
    result_content = content
    for search, replace in blocks:
        # We use re.escape for the search text but we need to handle the fact that
        # the model might vary slightly in whitespace if we are not careful.
        # However, for surgical precision, exact match is preferred.
        if search in result_content:
            result_content = result_content.replace(search, replace)
        else:
            # Try a slightly more relaxed match by stripping trailing whitespace per line
            search_lines = [l.rstrip() for l in search.splitlines()]
            # This is complex to implement robustly without a library, 
            # so for now we'll stick to exact match and suggest the model be precise.
            print(f" [ADK Tool] Warning: SEARCH block not found in file content. Exact match required.")
            
    return result_content

def commit_and_push_fixes(repo_path: str, branch_name: str, fixed_files: str) -> dict:
    """
    Commits the applied fixes and pushes them to the remote repository.
    
    Args:
        repo_path: The absolute path to the local repository.
        branch_name: The branch name to push to.
        fixed_files: Comma-separated list of file paths relative to the repository root.
        
    Returns:
        A dictionary with the submission status.
    """
    # Parse the comma-separated string into a list
    files_list = [f.strip() for f in fixed_files.split(",") if f.strip()]
    print(f" [ADK Tool] Committing and pushing fixes for: {files_list}")
    
    if not files_list:
        return {"status": "error", "message": "No files provided in the string."}

    try:
        repo = git.Repo(repo_path)
        git_ops.commit_and_push(repo, files_list, "chore: Security fixes by Guardian Agent (ADK)", branch_name)
        return {"status": "success", "message": f"Pushed {len(files_list)} files."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def comment_on_pr(repo_owner: str, repo_name: str, pr_number: int, message: str) -> dict:
    """
    Posts a comment to the specified Pull Request on Gitea.
    """
    gitea_client.post_comment(repo_owner, repo_name, pr_number, message)
    return {"status": "success"}
