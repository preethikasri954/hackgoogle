import os
import time
import requests
import subprocess
import sys

# Configuration
GITEA_URL = "http://localhost:3000"
ADMIN_USER = "guardian_admin"
ADMIN_PASS = "password123"
ADMIN_EMAIL = "admin@example.com"
REPO_NAME = "vulnerable-repo"
WEBHOOK_URL = "http://host.docker.internal:5000/webhook" # Access host from container? No, Gitea calls this.
# Note: If Gitea is in docker, and Agent is on host, Gitea needs to reach host.
# 'host.docker.internal' works on Windows/Mac. On Linux might need extra config.
# For now assuming Windows/Mac given the user OS.

def run_docker_cmd(cmd):
    full_cmd = f"docker exec -u 1000 gitea gitea {cmd}"
    print(f"Running: {full_cmd}")
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0 and "already exists" not in result.stderr:
        print(f"Error: {result.stderr}")
        return None
    return result.stdout.strip()

def check_gitea_up():
    print("Waiting for Gitea to be up...")
    for _ in range(30):
        try:
            requests.get(GITEA_URL)
            print("Gitea is up!")
            return True
        except requests.ConnectionError:
            time.sleep(2)
            print(".", end="", flush=True)
    return False

def create_admin():
    print("Creating admin user...")
    cmd = f"admin user create --username {ADMIN_USER} --password {ADMIN_PASS} --email {ADMIN_EMAIL} --admin"
    run_docker_cmd(cmd)

def create_token():
    print("Creating access token...")
    # Check if token exists or just create a new one?
    # gitea admin user generate-access-token doesn't seem to exist in all versions or CLI might differ.
    # Actually, better to use the API with Basic Auth (user/pass) to generate token or just use Basic Auth for the client.
    # Let's try to return the Basic Auth credentials for now or use the UI to generate.
    # OR, use the 'admin user' command if available. 
    # specific command: gitea admin user generate-access-token --username ... --token-name ...
    cmd = f"admin user generate-access-token --username {ADMIN_USER} --token-name guardian-token --scopes repo"
    output = run_docker_cmd(cmd)
    if output:
        # Parse output for token
        for line in output.split('\n'):
            if "Access token was successfully created" in line:
                 # usually the next line or part of it contains the token.
                 # Actually the CLI output format might be tricky.
                 pass
    return None

def setup_repo_and_webhook():
    # Use Basic Auth for simplicity since we have the password
    auth = (ADMIN_USER, ADMIN_PASS)
    
    # 1. Create Repo
    print(f"Creating repo '{REPO_NAME}'...")
    resp = requests.post(f"{GITEA_URL}/api/v1/user/repos", 
                         auth=auth, 
                         json={"name": REPO_NAME, "auto_init": True})
    if resp.status_code == 201:
        print("Repo created.")
    elif resp.status_code == 409:
        print("Repo already exists.")
    else:
        print(f"Failed to create repo: {resp.text}")
        return

    # 2. Create Webhook
    print(f"Setting up webhook pointing to {WEBHOOK_URL}...")
    # List hooks to see if exists
    hooks_resp = requests.get(f"{GITEA_URL}/api/v1/repos/{ADMIN_USER}/{REPO_NAME}/hooks", auth=auth)
    if hooks_resp.status_code == 200:
        for hook in hooks_resp.json():
            if hook['config']['url'] == WEBHOOK_URL:
                print(f"Deleting existing webhook {hook['id']} to update settings...")
                requests.delete(f"{GITEA_URL}/api/v1/repos/{ADMIN_USER}/{REPO_NAME}/hooks/{hook['id']}", auth=auth)

    hook_data = {
        "type": "gitea",
        "config": {
            "url": WEBHOOK_URL,
            "content_type": "json"
        },
        "events": ["push", "pull_request", "pull_request_sync", "issue_comment"],
        "active": True
    }
    # Update existing hook or create new one
    resp = requests.post(f"{GITEA_URL}/api/v1/repos/{ADMIN_USER}/{REPO_NAME}/hooks", 
                         auth=auth, 
                         json=hook_data)
    if resp.status_code == 201:
        print("Webhook created.")
    else:
        print(f"Failed to create webhook: {resp.text}")

if __name__ == "__main__":
    if check_gitea_up():
        create_admin()
        setup_repo_and_webhook()
        print("\nSetup complete!")
        print(f"Credentials: {ADMIN_USER} / {ADMIN_PASS}")
    else:
        print("Gitea did not start in time.")
