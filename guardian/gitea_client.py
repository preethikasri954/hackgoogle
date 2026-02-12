import requests
import os

class GiteaClient:
    def __init__(self, base_url=None, token=None, username=None, password=None):
        self.base_url = base_url or os.getenv("GITEA_URL", "http://localhost:3000")
        self.token = token or os.getenv("GITEA_TOKEN")
        self.username = username or os.getenv("GITEA_USER")
        self.password = password or os.getenv("GITEA_PASS")
        
        self.headers = {"Content-Type": "application/json"}
        self.auth = None
        
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        elif self.username and self.password:
            self.auth = (self.username, self.password)

    def post_comment(self, repo_owner, repo_name, pr_index, body):
        url = f"{self.base_url}/api/v1/repos/{repo_owner}/{repo_name}/issues/{pr_index}/comments"
        print(f"Posting comment to {url}")
        resp = requests.post(url, json={"body": body}, headers=self.headers, auth=self.auth)
        if resp.status_code != 201:
            print(f"Failed to post comment: {resp.text}")
        return resp.json()

    def create_pr(self, repo_owner, repo_name, head, base, title, body):
        url = f"{self.base_url}/api/v1/repos/{repo_owner}/{repo_name}/pulls"
        data = {
            "head": head,
            "base": base,
            "title": title,
            "body": body
        }
        resp = requests.post(url, json=data, headers=self.headers, auth=self.auth)
        return resp.json()
