
import sqlite3
import os

def get_user_data(username):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    
    results = cursor.fetchall()
    conn.close()
    return results

def main():
    username = input("Enter username: ")
    print(get_user_data(username))

if __name__ == "__main__":
    main()
