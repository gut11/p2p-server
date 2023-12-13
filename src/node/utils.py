import hashlib
import os
import time
import secrets
import re
import string

def generate_file_list(dir):
    files_list = os.listdir(dir)
    files_list.sort()
    files_hash_list = []
    files_name_list = create_file_names_list(files_list,dir)
    for file in files_list:
        file_path = os.path.join(dir, file)
        if os.path.isfile(file_path):
            file_bytes = open(file_path, 'rb')
            file_hash = calculate_md5(file_bytes)
            files_hash_list.append(file_hash)
    return merge_hash_file_lists(files_hash_list, files_name_list)

def merge_hash_file_lists(file_hashes,file_names):
    return ';'.join(f"{hash},{name}" for hash, name in zip(file_hashes, file_names))

def create_file_names_list(file_list,dir):
    files_list = []
    for file_name in file_list:
        file_path = os.path.join(dir, file_name)
        if os.path.isfile(file_path):
            files_list.append(file_name)
    return files_list

def generate_random_password(length=32, forbidden_characters={";", ",", " "}):
    # Define the set of allowed characters
    allowed_characters = set(string.ascii_letters + string.digits + string.punctuation)

    # Remove forbidden characters from the allowed set
    allowed_characters -= set(forbidden_characters)

    # Generate the password using only allowed characters
    password = ''.join(secrets.choice(list(allowed_characters)) for _ in range(length))
    return password

def find_file_position_by_hash(hash_to_find, file_list):
    count = 0
    for file_info in file_list:
        if file_info['md5'] == hash_to_find:
            return count
        count += 1

    return -1

def find_file_data_by_hash(md5_string, available_files):
    for file_info in available_files:
        if file_info["md5"] == md5_string:
            return file_info
    return None

def parse_file_info_string(file_info_string):
    file_info_list = file_info_string.split(';')

    file_dict_list = []
    for file_info in file_info_list:
        md5, file_name = file_info.split(',')
        file_dict = {'md5': md5, 'file_name': file_name}
        file_dict_list.append(file_dict)

    return file_dict_list

def create_download_dir(download_dir):
    dir_path = download_dir
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Directory '{dir_path}' created.")
    else:
        print(f"Directory '{dir_path}' already exists.")

def calculate_md5(file, chunk_size=(64 * 1024)):
    md5_hash = hashlib.md5()
    chunk = file.read(chunk_size)
    while chunk:
        md5_hash.update(chunk)
        chunk = file.read(chunk_size)
    return md5_hash.hexdigest()

def is_valid_md5(hash_string):
    md5_pattern = re.compile(r"^[a-fA-F0-9]{32}$")
    return bool(md5_pattern.match(hash_string))

def get_file_size(file_path):
    try:
        size = os.path.getsize(file_path)
        return size
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def process_file_info(response):
    files = response.split(';')

    file_list = []
    for file_info in files:
        parts = file_info.split(',')

        if len(parts) == 3:
            md5 = parts[0]
            name = parts[1]
            address = parts[2].split(":")

            file_list.append({'md5': md5, 'name': name, 'address': address})
        else:
            return None
    return file_list


def monitor_directory(directory_path, callback_function, *callback_params):
    previous_files = set(os.listdir(directory_path))

    while True:
        current_files = set(os.listdir(directory_path))

        added_files = current_files - previous_files
        removed_files = previous_files - current_files

        if added_files or removed_files:
            print("Change in the shared files dir. Updating file list on the server!")
            callback_function(*callback_params)

        previous_files = current_files
        time.sleep(1)

