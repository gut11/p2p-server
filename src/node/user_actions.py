import secrets
import string

from node.utils import generate_random_password, is_valid_md5

def print_menu_wait_input(menu_name, options):
    while True:
        print(f"{menu_name} Options:")
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

