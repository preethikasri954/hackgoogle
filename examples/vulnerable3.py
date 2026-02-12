import sqlite3
import os

def get_user_data(username):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    
    results = cursor.fetchall()
    conn.close()
    return results


API_KEY = "12345-abcde-secret-key"

def run_system_command(user_input):
    print("Running command...")
    os.system("echo " + user_input)

def load_user_config(config_data):
    import pickle
    return pickle.loads(config_data)

def main():
    username = input("Enter username: ")
    print(get_user_data(username))
    
    cmd_input = input("Enter command input: ")
    run_system_command(cmd_input)

if __name__ == "__main__":
    main()
