import os
import shutil
import time
from guardian.git_ops import GitOps
from guardian.gitea_client import GiteaClient

# Configuration
REPO_URL = "http://guardian_admin:password123@localhost:3000/guardian_admin/vulnerable-repo.git"
REPO_NAME = "temp_dev_repo_v2"
BRANCH_NAME = "feat/advanced-vulnerabilities-v3"
FILE_NAME = "vulnerable.py"

# New Vulnerable Code (matches examples/vulnerable.py)
VULNERABLE_CODE = """import sqlite3
import os

def get_user_data(username):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # VULNERABLE: SQL Injection
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    
    results = cursor.fetchall()
    conn.close()
    return results


# VULNERABLE: Hardcoded Secret
API_KEY = "12345-abcde-secret-key"

def run_system_command(user_input):
    # VULNERABLE: Command Injection
    print("Running command...")
    os.system("echo " + user_input)

def load_user_config(config_data):
    import pickle
    # VULNERABLE: Insecure Deserialization
    return pickle.loads(config_data)

def main():
    username = input("Enter username: ")
    print(get_user_data(username))
    
    cmd_input = input("Enter command input: ")
    run_system_command(cmd_input)

if __name__ == "__main__":
    main()
"""

def simulate_dev():
    print("--- Simulating Developer Workflow (Phase 2) ---")
    
    git_ops = GitOps(work_dir="./temp_dev_env_v2")
    gitea = GiteaClient()
    
    # 1. Clone
    print("1. Cloning repo...")
    # Clean up previous if exists
    if os.path.exists("./temp_dev_env_v2"):
         # Hack for windows read-only files
        def on_rm_error(func, path, exc_info):
            import stat
            os.chmod(path, stat.S_IWRITE)
            os.unlink(path)
        shutil.rmtree("./temp_dev_env_v2", onerror=on_rm_error)

    repo, repo_path = git_ops.clone_repo(REPO_URL, REPO_NAME)
    
    # 2. Create Branch
    print(f"2. Creating branch '{BRANCH_NAME}'...")
    repo.git.checkout("-b", BRANCH_NAME)
    
    # 3. Add Vulnerable Code
    print(f"3. Adding vulnerable code to {FILE_NAME}...")
    file_path = os.path.join(repo_path, FILE_NAME)
    with open(file_path, "w") as f:
        f.write(VULNERABLE_CODE)
        
    # 4. Commit and Push
    print("4. Committing and Pushing...")
    git_ops.commit_and_push(repo, [FILE_NAME], "feat: Add critical vulnerabilities", BRANCH_NAME)
    
    # 5. Open PR
    print("5. Opening Pull Request...")
    pr = gitea.create_pr(
        repo_owner="guardian_admin",
        repo_name="vulnerable-repo",
        head=BRANCH_NAME,
        base="main",
        title="feat: Add advanced features (Vulnerable)",
        body="Adding features with multiple security issues for testing."
    )
    
    print(f"✅ PR Created: #{pr['number']}")
    return pr['number']

if __name__ == "__main__":
    simulate_dev()
