import requests
import json

WEBHOOK_URL = "http://localhost:5000/webhook"

# Payload mimicking Gitea JSON for PR opened
payload = {
  "action": "opened",
  "number": 1,
  "pull_request": {
    "html_url": "http://localhost:3000/guardian_admin/vulnerable-repo/pulls/1",
    "state": "open",
    "head": {
      "ref": "feat/add-vulnerable-feature",
      "sha": "fake_sha_for_trigger"
    }
  },
  "repository": {
    "name": "vulnerable-repo",
    "owner": {
      "username": "guardian_admin"
    },
    "clone_url": "http://localhost:3000/guardian_admin/vulnerable-repo.git"
  }
}

headers = {
    "Content-Type": "application/json",
    "X-Gitea-Event": "pull_request"
}

print(f"Triggering Webhook at {WEBHOOK_URL}...")
try:
    resp = requests.post(WEBHOOK_URL, json=payload, headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
except Exception as e:
    print(f"Failed: {e}")
