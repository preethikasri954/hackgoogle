import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

GITEA_URL = os.getenv("GITEA_URL", "http://localhost:3000")
GITEA_USER = os.getenv("GITEA_USER", "guardian_admin")
GITEA_PASS = os.getenv("GITEA_PASS", "password123")

def check_results():
    # 1. Get latest PR
    url = f"{GITEA_URL}/api/v1/repos/{GITEA_USER}/vulnerable-repo/pulls?state=all&sort=recentupdate"
    resp = requests.get(url, auth=(GITEA_USER, GITEA_PASS))
    if resp.status_code != 200:
        print(f"Error fetching PRs: {resp.status_code}")
        return

    pulls = resp.json()
    if not pulls:
        print("No PRs found.")
        return

    latest_pr = pulls[0]
    pr_num = latest_pr['number']
    print(f"Latest PR: #{pr_num} - {latest_pr['title']} ({latest_pr['state']})")

    # 2. Get comments
    url = f"{GITEA_URL}/api/v1/repos/{GITEA_USER}/vulnerable-repo/issues/{pr_num}/comments"
    resp = requests.get(url, auth=(GITEA_USER, GITEA_PASS))
    comments = resp.json()
    print(f"Comments: {len(comments)}")
    for c in comments:
        if "Guardian Agent" in c['body']:
            print(f"--- Guardian Comment ---\n{c['body'][:200]}...\n")

    # 3. Get files/diff
    url = f"{GITEA_URL}/api/v1/repos/{GITEA_USER}/vulnerable-repo/pulls/{pr_num}.diff"
    resp = requests.get(url, auth=(GITEA_USER, GITEA_PASS))
    print(f"--- PR Diff ---\n{resp.text[:500]}...\n")

if __name__ == "__main__":
    check_results()
