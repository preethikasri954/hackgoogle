import git
import os
import shutil
import requests
import time

# Config
GITEA_URL = "http://localhost:3000"
REPO_URL = "http://localhost:3000/guardian_admin/vulnerable-repo.git"
USER = "guardian_admin"
PASS = "password123"
ts = int(time.time())
CLONE_DIR = f"./temp_dev_repo_{ts}"
BRANCH_NAME = f"feat/vulnerability-{ts}"

def simulate():
    if os.path.exists(CLONE_DIR):
        def on_rm_error(func, path, exc_info):
            import stat
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(CLONE_DIR, onerror=on_rm_error)

    # 1. Clone
    print(f"Cloning {REPO_URL} into {CLONE_DIR}...")
    # Passing auth in URL for gitpython
    auth_url = REPO_URL.replace("http://", f"http://{USER}:{PASS}@")
    repo = git.Repo.clone_from(auth_url, CLONE_DIR)

    # 2. Configure User
    repo.config_writer().set_value("user", "name", USER).release()
    repo.config_writer().set_value("user", "email", "admin@example.com").release()

    # 3. Create Branch
    print(f"Creating branch {BRANCH_NAME}...")
    new_branch = repo.create_head(BRANCH_NAME)
    new_branch.checkout()

    # 4. Add Vulnerable File
    src_file = "examples/vulnerable3.py"
    dst_file = os.path.join(CLONE_DIR, "vulnerable3.py")
    if not os.path.exists(src_file):
        print(f"Error: {src_file} does not exist.")
        return
    
    shutil.copy(src_file, dst_file)
    repo.index.add(["vulnerable3.py"])
    repo.index.commit(f"feat: Add user data feature ({ts})")

    # 5. Push
    print(f"Pushing {BRANCH_NAME}...")
    origin = repo.remote(name='origin')
    origin.push(BRANCH_NAME)

    # 6. Open PR via API
    print("Opening Pull Request...")
    auth = (USER, PASS)
    data = {
        "head": BRANCH_NAME,
        "base": "main",
        "title": f"Security Test {ts}",
        "body": "This PR adds a vulnerable file for testing the Guardian Agent."
    }
    resp = requests.post(f"{GITEA_URL}/api/v1/repos/{USER}/vulnerable-repo/pulls", 
                         json=data, auth=auth)
    
    if resp.status_code == 201:
        print(f"PR Created: {resp.json()['html_url']}")
        print("Simulation Complete! Agent should pick this up.")
    else:
        print(f"Failed to create PR: {resp.text}")

if __name__ == "__main__":
    simulate()
