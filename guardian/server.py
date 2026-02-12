from flask import Flask, request, jsonify
import os
import threading
import asyncio
import sys

app = Flask(__name__)

def run_agent_in_thread(data):
    """Bridge for running the async ADK agent from a sync thread."""
    from .adk_agent import run_guardian_on_pr
    
    repo_url = data['repository']['clone_url']
    # Use local URL if it's localhost (for our dev env)
    if "localhost" in repo_url or "127.0.0.1" in repo_url:
         # Internal docker network vs host machine
         pass
    
    repo_owner = data['repository']['owner']['username']
    repo_name = data['repository']['name']
    pr_number = data['number']
    branch_name = data['pull_request']['head']['ref']
    
    try:
        asyncio.run(run_guardian_on_pr(repo_url, repo_owner, repo_name, pr_number, branch_name))
    except Exception as e:
        print(f" [ADK Agent] Error during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()

@app.route('/webhook', methods=['POST'])
def webhook():
    event_type = request.headers.get('X-Gitea-Event')
    data = request.json
    action = data.get('action') if data else "no_data"
    
    print(f" [WEBHOOK DEBUG] Received '{event_type}' event with action '{action}'")
    sys.stdout.flush()
    
    if event_type == 'pull_request':
        
        if action in ['opened', 'reopened', 'synchronized']:
            print(f" [WEBHOOK] Triggering ADK Agent for PR #{data.get('number')}...")
            sys.stdout.flush()
            # Run ADK agent in background
            thread = threading.Thread(target=run_agent_in_thread, args=(data,))
            thread.start()
            
            return jsonify({'status': 'processing', 'message': 'Guardian ADK Agent started'}), 202
    
    print(f" [WEBHOOK] Ignored event: {event_type}")
    sys.stdout.flush()
    return jsonify({'status': 'ignored'}), 200

def run_server():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    run_server()
