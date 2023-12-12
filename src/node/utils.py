import hashlib
import os
import secrets
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
        chunk = file.read(chunk_size)
        md5_hash.update(chunk)
    return md5_hash.hexdigest()

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
