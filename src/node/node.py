import socket
import threading
import os
import time
from node.user_actions import print_menu_wait_input

from node.utils import (
    create_download_dir,
    find_file_data_by_hash,
    find_file_position_by_hash,
    generate_file_list,
    generate_random_password,
    get_file_size,
    is_valid_md5,
    monitor_directory,
    parse_file_info_string,
    process_file_info,
)


def create_udp_socket():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return udp_socket


def send_udp_message(socket, message, server_address):
    timeout = 5
    max_retries = 4
    socket.settimeout(timeout)
    last_exception = None
    message_byte = message.encode()
    for retry in range(max_retries):
        if retry > 0:
            print(f"Retrying... (Retry {retry}/{max_retries - 1})")
        try:
            socket.sendto(message_byte, server_address)
            response, _ = socket.recvfrom(1024)
            return response
        except socket.timeout as e:
            if retry != max_retries - 1:
                print(f"Server timeout error:{e} \n")
            last_exception = e
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            last_exception = e
    if last_exception is not None:
        raise last_exception


def send_tcp_message(socket, message, server_address):
    timeout = 5
    max_retries = 4
    socket.settimeout(timeout)
    last_exception = None

    for retry in range(max_retries):
        if retry > 0:
            print(f"Retrying... (Retry {retry}/{max_retries - 1})")
        try:
            socket.connect(server_address)
            socket.sendall(message.encode("utf-8"))
            response = socket.recv(1024)
            return response
        except socket.timeout as e:
            if retry != max_retries - 1:
                print(f"Server timeout error: {e}\n")
            last_exception = e
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            last_exception = e

    if last_exception is not None:
        raise last_exception


def register_on_server(socket, server_address, dir, client_info):
    file_list_string = generate_file_list(dir)
    client_info["file_list"] = parse_file_info_string(file_list_string)
    client_info["password"] = generate_random_password()


    registration_message = (
        f'REG {client_info["password"]} {client_info["port"]} {file_list_string}'
    )
    try:
        response = send_udp_message(socket, registration_message, server_address)
        print("Registration on the server completed!")
    except Exception as e:
        print(
            f"An error occurred while trying to register the client on the server: {e}"
        )
        raise e


def send_file_list_req(socket, server_address, client_info):
    try:
        response = send_udp_message(socket, "LST ", server_address)
        if response is not None:
            file_list = process_file_info(response.decode())

            if file_list is not None:
                print("File list")
                for file_info in file_list:
                    print(
                        f'MD5: {file_info["md5"]}, Nome: {file_info["name"]}, IPs e Portas: {file_info["address"]}'
                    )
                client_info["available_files"] = file_list
            else:
                print("file list req error")
    except Exception as e:
        print(f"Error sending the request for the list of files: {e}")


def get_file(node_address, file_name, file_hash, download_dir):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    file_path = download_dir + "/" + file_name
    message = "GET " + file_hash

    try:
        response = send_tcp_message(tcp_socket, message, node_address)
        if response is not None:
            response_string = response.decode()
            if is_file_available(response):
                (
                    response_status,
                    response_file_hash,
                    file_size_and_file_bytes,
                    *_
                ) = response_string.split(" ", 3)
                file_size = file_size_and_file_bytes.split(" ", 1)[0]
                position_where_file_starts = find_byte_file_start(response)
                file_first_bytes = response[position_where_file_starts:]
                download_file(
                    tcp_socket, file_name, file_path, file_size, file_first_bytes
                )
    except Exception as e:
        print(f"An error occurred while trying get file from another node: {e}")
        raise e


def find_byte_file_start(byte_response):
    space_count = 0
    position = None

    for i, byte in enumerate(byte_response):
        if byte == 32:
            space_count += 1
            if space_count == 3:
                position = i + 1
                break

    return position


def is_file_available(response):
    response_string = response.decode()
    if response_string.startswith("OK"):
        return True
    else:
        return False


def download_file(socket, file_name, file_path, file_size, first_bytes):
    BUFFER_SIZE = 4096

    file = open(file_path, "wb")
    file.write(first_bytes)
    print(f"Receiving file of size {file_size} bytes")

    received_size = len(first_bytes)

    while True:
        data = socket.recv(BUFFER_SIZE)
        if not data:
            break
        file.write(data)
        received_size += len(data)

        print(f"Received: {received_size} bytes / {file_size} bytes")

    print(f"File {file_name} received successfully")


def handle_req(socket, client_info):
    req = socket.recv(1024).decode("utf-8")
    file_list = client_info["file_list"]
    file_dir = client_info["file_dir"]
    if req.startswith("GET"):
        parts = req.split(" ")
        if len(parts) >= 2:
            hash_to_find = parts[1]
            file_position = find_file_position_by_hash(hash_to_find, file_list)
            if file_position != -1:
                send_file(socket, file_list[file_position], file_dir)
            else:
                handle_bad_request(socket, "File not found")
        else:
            handle_bad_request(socket, "Request bad formatted")
    else:
        handle_bad_request(socket, "Request bad formatted")


def handle_bad_request(socket, message):
    response = "ERR " + message
    socket.send(response)
    socket.close()


def send_file(socket, file_info, file_dir):
    BUFFER_SIZE = 4096
    file_md5 = file_info["md5"]
    file_name = file_info["file_name"]
    file_path = file_dir + "/" + file_name
    file_size = str(get_file_size(file_path))

    message = "OK " + file_md5 + " " + file_size + " "

    try:
        socket.send(message.encode())
        with open(file_path, "rb") as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    break
                socket.sendall(data)
    except FileNotFoundError:
        socket.send("File not found".encode())
        raise FileNotFoundError
    except Exception as e:
        socket.send(str(e).encode())
        raise e
    finally:
        socket.close()


def update_files_on_server(socket, server_address, dir, client_info):
    file_list_string = generate_file_list(dir)
    client_info["file_list"] = parse_file_info_string(file_list_string)
    req = (
        "UPD " + client_info["password"] + " " + str(client_info["port"]) + " " + file_list_string
    )
    send_udp_message(socket, req, server_address)


def end_connection(socket, server_address, client_info):
    req = "END " + str(client_info["password"]) + " " + str(client_info["port"])
    send_udp_message(socket, req, server_address)
    socket.close()


def start_tcp_server(server_ready, client_info):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((client_info["host"], 0))
    _, client_info["port"] = server_socket.getsockname()
    server_socket.listen(4096)
    
    print(f'Server listening on {client_info["host"]}:{client_info["port"]}')

    server_ready.set()

    while True:
        print("Waiting for a file request...")
        client_socket, client_address = server_socket.accept()
        answer_node_req_thread = threading.Thread(
            target=handle_req, args=(client_socket, client_info)
        ).start()


def start_node_server(host="127.0.0.1", file_dir="./files"):
    server_address = (host, 54494)
    download_dir = "./p2p-downloads"
    user_input = 0
    menu_options = ["List files", "Get file", "Exit"]
    client_info = {
        "password": None,
        "file_list": "",
        "file_dir": file_dir,
        "available_files": [
            {
                "md5": "34213f31234abc3213",
                "name": "random_name",
                "address": ("127.0.0.1", 4000),
            }
        ],
        "host": host,
        "port": -1,
    }
    create_download_dir(download_dir)
    server_ready_event = threading.Event()
    tcp_socket_thread = threading.Thread(
        target=start_tcp_server, args=(server_ready_event, client_info)
    )
    tcp_socket_thread.start()
    udp_socket = create_udp_socket()
    server_ready_event.wait()
    register_on_server(udp_socket, server_address, client_info["file_dir"], client_info)
    send_file_list_req(udp_socket, server_address, client_info)
    watch_dir_thread = threading.Thread(
        target=monitor_directory, args=(file_dir, update_files_on_server, udp_socket, server_address, file_dir, client_info)
    )
    watch_dir_thread.start()

    while True:
        user_input = print_menu_wait_input("Main Menu", menu_options)
        if user_input == 1:
            send_file_list_req(udp_socket, server_address, client_info)
            print("List of files:")
        if user_input == 2:
            while True:
                file_hash = input("File Hash: ")
                if is_valid_md5(file_hash):
                    file_data = find_file_data_by_hash(
                        file_hash, client_info["available_files"]
                    )
                    if file_data is not None:
                        file_hash = file_data["md5"]
                        file_name = file_data["name"]
                        node_address = file_data["address"]
                        node_address[1] = int(node_address[1])
                        node_address = tuple(node_address)
                        get_file(node_address, file_name, file_hash, download_dir)
                        break
                else:
                    if len(file_hash) == 1:
                        try:
                            file_hash_number = int(file_hash)
                            if file_hash_number == 0:
                                break
                        except ValueError:
                            print("Hash errado, digite novamente:")
                    else:
                        print("Hash errado, digite novamente:")
        if user_input == 3:
            end_connection(udp_socket, server_address, client_info)
            print("VLW,FLW")
            os._exit(0)
