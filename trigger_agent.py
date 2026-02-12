import asyncio
import os
from guardian.adk_agent import run_guardian_on_pr
from dotenv import load_dotenv

load_dotenv()

async def manual_trigger():
    repo_url = "http://localhost:3000/guardian_admin/vulnerable-repo.git"
    repo_owner = "guardian_admin"
    repo_name = "vulnerable-repo"
    pr_number = 36
    branch_name = "feat/vulnerability-1770875668" # Corrected based on simulation timestamp
    
    print(f"Manually triggering Guardian for PR #{pr_number}...")
    await run_guardian_on_pr(repo_url, repo_owner, repo_name, pr_number, branch_name)

if __name__ == "__main__":
    asyncio.run(manual_trigger())
