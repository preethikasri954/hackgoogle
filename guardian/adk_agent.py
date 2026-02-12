import os
import asyncio
import time
from google.adk import Agent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

from .tools import (
    analyze_pr_vulnerabilities,
    fix_code_vulnerability,
    commit_and_push_fixes,
    comment_on_pr
)

# Instruction for the Security Guardian Agent
SECURITY_INSTRUCTIONS = """
You are the "🛡️ Guardian Agent", an AI-powered security expert.
Your goal is to protect repositories by surgically fixing security vulnerabilities identified in Pull Requests.

Workflow:
1. Call 'analyze_pr_vulnerabilities' to find issues in the PR.
2. If vulnerabilities are found, for EACH issue in the 'issues' list:
   - Call 'fix_code_vulnerability' with the EXACT filename, line_number, and issue_text from that specific issue.
   - Do NOT combine fixes or hallucinate issues not found by the analysis tool.
3. Once all fixes are applied, call 'commit_and_push_fixes' with the 'fixed_files' (comma-separated string).
4. Finally, call 'comment_on_pr' to report progress.

Guidelines:
- Always aim for high-quality, surgical, and secure code.
- Only fix what is identified by the analysis tool.
- Be concise.
"""

# Define the Security Guardian Agent
guardian_agent = Agent(
    name="GuardianAgent",
    description="Analyzes and fixes security vulnerabilities in Pull Requests.",
    instruction=SECURITY_INSTRUCTIONS,
    tools=[
        analyze_pr_vulnerabilities,
        fix_code_vulnerability,
        commit_and_push_fixes,
        comment_on_pr
    ],
    model="gemini-2.5-flash"
)

# Global runner initialization
session_service = InMemorySessionService()
runner = Runner(
    app_name="GuardianApp",
    agent=guardian_agent,
    session_service=session_service,
    auto_create_session=True
)

async def run_guardian_on_pr(repo_url: str, repo_owner: str, repo_name: str, pr_number: int, branch_name: str):
    """
    Executes the ADK Agent to process a specific Pull Request.
    """
    print(f" [ADK Agent] Starting security run for PR #{pr_number} in {repo_name}...")
    
    # We provide the initial signal to the agent
    prompt = f"Process PR #{pr_number} in repo '{repo_name}' (owned by {repo_owner}). Clone URL: {repo_url}. Branch: {branch_name}."
    
    # Run the agent using the Runner
    try:
        async for event in runner.run_async(
            user_id="guardian_system",
            session_id=f"pr_{pr_number}_{int(time.time())}",
            new_message=types.Content(parts=[types.Part(text=prompt)])
        ):
            if event.content:
                # Safely extract text from the content parts
                parts = getattr(event.content, 'parts', [])
                msg_parts = []
                for p in parts:
                    text = getattr(p, 'text', None)
                    if text:
                        msg_parts.append(text)
                msg = "".join(msg_parts)
                
                # Fallback to string representation if no text parts found
                if not msg and event.content:
                    # Avoid logging empty things or just the content object address
                    pass
                
                if msg:
                    print(f" [ADK Agent] {event.author}: {msg.strip()}")
            
            # Log tool calls for transparency
            if event.get_function_calls():
                for fc in event.get_function_calls():
                    print(f" [ADK Agent] Executing tool: {fc.name}")
                    
    except Exception as e:
        print(f" [ADK Agent] Runtime error: {e}")
        import traceback
        traceback.print_exc()
