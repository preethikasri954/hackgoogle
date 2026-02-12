import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self, api_key=None, model_name="gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        if not self.api_key:
            print("WARNING: GEMINI_API_KEY not set. Using Mock LLM mode.")
            self.model = None
            self.fallback_model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                # Try to list models to confirm API key and see what's available
                available_models = []
                try:
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            available_models.append(m.name)
                except Exception as e:
                    print(f" [LLM] Warning: Could not list models: {e}")

                if available_models:
                    print(f" [LLM] Available models: {available_models}")
                    # If requested model not in list, find a suitable one
                    current_model_path = f"models/{model_name}"
                    if current_model_path not in available_models and f"models/{model_name}-latest" not in available_models:
                        # Fallback to flash if available
                        flash_models = [m for m in available_models if 'flash' in m]
                        if flash_models:
                            self.model_name = flash_models[0].split('/')[-1]
                            print(f" [LLM] Requested model {model_name} not found. Using {self.model_name}")

                self.model = genai.GenerativeModel(self.model_name)
                self.fallback_model = genai.GenerativeModel("gemini-2.5-flash")
            except Exception as e:
                 print(f" [LLM] Initialization error: {e}")
                 self.model = None

    def generate_fix(self, vulnerability_report, code_content):
        print(f" [LLM] Sending prompt to {self.model_name}...")
        try:
            if not self.model:
                raise ValueError("Model not initialized")
                
            prompt = f"""
            You are a Senior Security Engineer.
            
            Vulnerability Report:
            {vulnerability_report}
            
            Vulnerable Code:
            ```python
            {code_content}
            ```
            
            Task:
            1. Analyze the vulnerabilities accurately.
            2. Propose a SURGICAL fix using SEARCH/REPLACE blocks.
            3. PRESERVE as much of the original code, comments, and structure as possible.
            
            Format your response as one or more SEARCH/REPLACE blocks:
            <<<<<<< SEARCH
            [exact original code to be replaced]
            =======
            [the newly fixed code]
            >>>>>>> REPLACE

            Rules:
            - The SEARCH section must EXACTLY match the original code, including whitespace and indentation.
            - Return ONLY the blocks. No explanations.
            - Use 'os.environ.get' for secrets.
            - Use 'subprocess.run' with lists for system commands.
            """
            
            response = self.model.generate_content(prompt)
            print(" [LLM] Response received.")
            return response.text.strip()
        except Exception as e:
            print(f" [LLM] Error with {self.model_name}: {e}")
            return self._mock_fix(vulnerability_report, code_content)

    def _mock_fix(self, vulnerability_report, code_content):
        print(" [Mock LLM] Generating fix for SQL Injection, Command Injection, Secrets, Deserialization...")
        return """
import sqlite3
import os
import subprocess
import json

def get_user_data(username):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # FIXED: SQL Injection
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    
    results = cursor.fetchall()
    conn.close()
    return results

# FIXED: Hardcoded Secret
API_KEY = os.getenv("API_KEY", "default-secret-key")

def run_system_command(user_input):
    # FIXED: Command Injection (Use subprocess with list)
    print("Running command...")
    # Safe echo
    subprocess.run(["echo", user_input])

def load_user_config(config_data):
    # FIXED: Insecure Deserialization (Use JSON)
    return json.loads(config_data)

def main():
    username = input("Enter username: ")
    print(get_user_data(username))
    
    cmd_input = input("Enter command input: ")
    run_system_command(cmd_input)

if __name__ == "__main__":
    main()
"""

    def analyze_security(self, code_content):
        """
        Secondary check if Bandit misses something (optional).
        """
        return "Analysis not implemented yet (relying on Bandit)."
