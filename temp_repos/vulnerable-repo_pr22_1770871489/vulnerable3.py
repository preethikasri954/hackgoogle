To address the Bandit B603 issue (`subprocess call - check for execution of untrusted input`) on line 27, where `subprocess.run(["echo", user_input], check=True)` is used, we need to understand the intent. The `echo` command's sole purpose is to print its arguments to standard output. When a simpler, safer, and built-in Python function can achieve the same result, it is always preferred to avoid external process execution, especially with untrusted input.

The existing code already correctly uses a list for `subprocess.run` to prevent command injection (which was a fix for B404 and `os.system` vulnerability). However, Bandit's B603 can sometimes indicate a broader concern about executing *any* external command with untrusted input, even when handled technically correctly, if a safer alternative exists.

By replacing the `subprocess.run(["echo", user_input], check=True)` call with a direct `print(user_input)`, we eliminate the need for an external process entirely. This completely mitigates any potential security risks associated with `subprocess` for this specific functionality, fulfilling the Bandit report's requirement in the most robust way.

Additionally, since `subprocess` and `shutil` are no longer needed after this change, their imports will be removed for code cleanliness.


import sqlite3
import os
import json
# Removed: import subprocess (no longer needed for run_system_command)
# Removed: import shutil (shutil.which is no longer needed)

def get_user_data(username):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    # FIX: Use parameterized queries to prevent SQL injection
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))

    results = cursor.fetchall()
    conn.close()
    return results

# FIX: Use os.environ.get for secrets instead of hardcoding
API_KEY = os.environ.get("API_KEY") # Ensure API_KEY is set in your environment variables

def run_system_command(user_input):
    print("Running command...")
    # FIX for Bandit B603: Replaced external 'echo' call with Python's print().
    # The 'echo' command merely prints its arguments to standard output.
    # Directly using Python's print() function is safer and more efficient,
    # completely eliminating the need for an external subprocess call and
    # any associated risks with untrusted input, as highlighted by Bandit.
    
    # This also implicitly resolves previous Bandit B404 (command injection)
    # and B607 (partial executable path) issues by avoiding subprocess altogether for this functionality.
    print(user_input)

    # Original vulnerable line (os.system("echo " + user_input)) and
    # the subsequent fix attempt using subprocess.run([...]) are now replaced.
    # While subprocess.run with a list is generally the correct way to avoid
    # command injection when external commands *must* be run, for a simple
    # 'echo' equivalent, Python's native print() is always preferred for
    # maximum security and simplicity.

def load_user_config(config_data):
    # FIX for Bandit B301: Use json for deserialization instead of pickle due to security risks with untrusted input
    # The original vulnerability was using 'pickle.loads', which can lead to arbitrary code execution.
    # By using 'json.loads', we mitigate this risk as JSON is a safer format for data exchange.
    try:
        return json.loads(config_data)
    except json.JSONDecodeError:
        print("Error: Invalid JSON data provided for user config. Could not load.")
        return None # Return None or raise a more specific error

def main():
    # Setup for demonstration: Ensure database and a user exist
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('testuser', 'securepass'))
        conn.commit()
    except sqlite3.IntegrityError:
        # User already exists
        pass
    conn.close()

    username = input("Enter username to query (try 'testuser'): ")
    print("User data:", get_user_data(username))

    cmd_input = input("Enter command input (e.g., 'hello world'): ")
    run_system_command(cmd_input)

    # Example: {"theme": "dark", "notifications": true}
    config_input = input("Enter JSON config data (e.g., '{\"theme\": \"dark\"}'): ")
    print("Loaded config:", load_user_config(config_input))

if __name__ == "__main__":
    main()