import secrets
import string

from node.utils import generate_random_password

def print_main_menu():
    print("Available commands:")
    print("1. List files")
    print("2. Get file")
    print("3. Exit")

def create_user_password(client_info):
    password_menu_options = ["Choose password (Type every time)", "Generate password (No need for typing the password)"]
    user_option = print_menu_wait_input("Password", password_menu_options)
    if user_option == 1:
        return input("Type your password: ")
    if user_option == 2:
        client_info.auto_pass = True
        return generate_random_password()

def print_menu_wait_input(menu_name, options):
    while True:
        print(f"{menu_name} options:")
        for i, option in enumerate(options, start=1):
            print(f"{i}. {option}")
        try:
            user_input = int(input(f"Enter {menu_name.lower()} option: "))
            if 1 <= user_input <= len(options):
                return user_input
            else:
                print(f"Invalid {menu_name.lower()} option. Please enter a number between 1 and {len(options)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

