import secrets
import string

def print_menu():
    print("Available commands:")
    print("1. List files")
    print("2. Get file")
    print("3. Exit")

def wait_for_user_action():
    print_menu();
    user_input = input("Enter command: ");

def generate_random_password(length=32):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password
