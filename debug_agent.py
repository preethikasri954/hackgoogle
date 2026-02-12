from guardian.agent import SecurityAgent
import sys

# Mock Payload for PR #1
payload = {
  "action": "opened",
  "number": 3,
  "pull_request": {
    "html_url": "http://localhost:3000/guardian_admin/vulnerable-repo/pulls/3",
    "head": {
      "ref": "vulnerable-feature"
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

print("Starting Debug Run...")
try:
    agent = SecurityAgent()
    agent.process_pr(payload)
    print("Debug Run Complete.")
except Exception as e:
    import traceback
    traceback.print_exc()
