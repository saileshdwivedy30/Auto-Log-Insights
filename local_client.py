import os
import requests
import sys
import json
import getpass
import termios
import tty

TOKEN_FILE = "/Users/saileshdwivedy/Downloads/jwt_token.txt"
BASE_URL = "http://34.42.117.89:5000"
LOG_FILE_PATH = "/Users/saileshdwivedy/Downloads/test-log.txt"

def input_with_stars(prompt=""):
    """
    Custom function to capture password input and display stars (*) for each character.
    """
    print(prompt, end="", flush=True)
    password = ""
    try:
        # Save terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(fd)
        while True:
            char = sys.stdin.read(1)
            if char == "\n" or char == "\r":  # Enter key
                print("")
                break
            elif char == "\x7f":  # Backspace key
                if len(password) > 0:
                    password = password[:-1]
                    sys.stdout.write("\b \b")  # Remove last star
                    sys.stdout.flush()
            else:
                password += char
                sys.stdout.write("*")  # Print a star
                sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  # Restore terminal settings
    return password

def register_user():
    username = input("Enter username for registration: ")
    password = input_with_stars("Enter password for registration: ")
    register_endpoint = f"{BASE_URL}/register"
    payload = {"username": username, "password": password}
    response = requests.post(register_endpoint, json=payload)
    if response.status_code in [200, 201]:  # Handle both 200 and 201 as success
        print(f"Registration successful: {response.json()}")
        choice = input("Do you want to login now? (yes/no): ").strip().lower()
        if choice == "yes":
            login_user(username, password)  # Use the same username and password to log in
    else:
        print(f"Registration failed: {response.status_code}, {response.text}")

def login_user(existing_username=None, existing_password=None):
    if existing_username and existing_password:
        username = existing_username
        password = existing_password
    else:
        username = input("Enter username for login: ")
        password = input_with_stars("Enter password for login: ")

    login_endpoint = f"{BASE_URL}/login"
    payload = {"username": username, "password": password}
    response = requests.post(login_endpoint, json=payload)
    if response.status_code == 200:
        token = response.json().get("token")
        print(f"Login successful. Token saved.")
        with open(TOKEN_FILE, "w") as f:
            f.write(token)
        choice = input("Do you want to upload a file now? (yes/no): ").strip().lower()
        if choice == "yes":
            upload_file()
    else:
        print(f"Login failed: {response.status_code}, {response.text}")

def upload_file():
    if not os.path.exists(TOKEN_FILE):
        print(f"No token found. Please login first.")
        return

    with open(TOKEN_FILE, "r") as f:
        token = f.read().strip()

    if not os.path.exists(LOG_FILE_PATH):
        print(f"Log file not found at {LOG_FILE_PATH}. Please check the path.")
        return

    upload_endpoint = f"{BASE_URL}/upload"
    headers = {"Authorization": f"Bearer {token}"}
    files = {"logfile": open(LOG_FILE_PATH, "rb")}
    response = requests.post(upload_endpoint, headers=headers, files=files)
    if response.status_code == 200:
        print(f"File upload successful: {response.json()}")
    else:
        print(f"File upload failed: {response.status_code}, {response.text}")

def main():
    print("Welcome! Please choose an option:")
    print("1. Register")
    print("2. Login")
    print("3. Upload File")

    choice = input("Enter your choice (1/2/3): ")
    if choice == "1":
        register_user()
    elif choice == "2":
        login_user()
    elif choice == "3":
        upload_file()
    else:
        print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
