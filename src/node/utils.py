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
            file_bytes = open(file, 'rb')
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

def generate_random_password(length=32):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def calculate_md5(file, chunk_size=(64 * 1024)):
    md5_hash = hashlib.md5()
    chunk = file.read(chunk_size)
    while chunk:
        chunk = file.read(chunk_size)
        md5_hash.update(chunk)
    return md5_hash.hexdigest()
