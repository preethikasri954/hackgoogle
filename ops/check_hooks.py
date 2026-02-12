import requests

GITEA_URL = "http://localhost:3000"
ADMIN_USER = "guardian_admin"
ADMIN_PASS = "password123"
REPO_NAME = "vulnerable-repo"

auth = (ADMIN_USER, ADMIN_PASS)

def check_hooks():
    url = f"{GITEA_URL}/api/v1/repos/{ADMIN_USER}/{REPO_NAME}/hooks"
    print(f"Checking hooks for {ADMIN_USER}/{REPO_NAME}...")
    resp = requests.get(url, auth=auth)
    if resp.status_code == 200:
        hooks = resp.json()
        if not hooks:
            print("No hooks found!")
        for hook in hooks:
            print(f"Hook ID: {hook['id']}")
            print(f"  URL: {hook['config']['url']}")
            print(f"  Events: {hook['events']}")
            print(f"  Active: {hook['active']}")
    else:
        print(f"Failed to get hooks: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    check_hooks()
