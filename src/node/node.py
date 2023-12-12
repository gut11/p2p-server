import socket
import threading

from node.user_actions import create_user_password

from node.utils import generate_file_list


def create_udp_socket():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return udp_socket


def send_udp_message(socket, message, server_address):
    timeout = 5
    max_retries = 4
    socket.settimeout(timeout)
    last_exception = None
    for retry in range(max_retries):
        if retry > 0:
            print(f"Retrying... (Retry {retry}/{max_retries - 1})")
        try:
            socket.sendto(message.encode("utf-8"), server_address)
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


def register_on_server(socket, server_address, dir, client_info):
    client_info["password"] = create_user_password(client_info)
    client_info["file_list"] = generate_file_list(dir)
    registration_message = f'REG {client_info["password"]} {client_info["port"]} {client_info["file_list"]}'
    try:
        response = send_udp_message(socket, registration_message, server_address)
        print("Registration on the server completed!")
        print(f"Server response: {response}")
    except Exception as e:
        print(
            f"An error occurred while trying to register the client on the server: {e}"
        )
        raise e


def send_file_list_req(socket, server_address):
    try:
        response = send_udp_message(socket, "LST ", server_address)
        print("File list fetch completed!")
        print(f"Server response: {response}")
    except Exception as e:
        print(f"An error occurred while trying to get file list on the server: {e}")
        raise e


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
        print(f"Accepted connection from {client_address}")

        data = client_socket.recv(1024).decode("utf-8")
        print(f"Received data: {data}")

        response = "Hello, World!"
        client_socket.send(response.encode("utf-8"))

        client_socket.close()
        print("Connection closed\n")


def start_node_server(host="127.0.0.1", file_dir="./files"):
    server_address = (host, 8000)
    client_info = {
        "password": None,
        "file_list": "",
        "file_dir": file_dir,
        "auto_pass": False,
        "host": host,
        "port": -1,
    }
    print(client_info)
    server_ready_event = threading.Event()
    tcp_socket_thread = threading.Thread(
        target=start_tcp_server, args=(server_ready_event, client_info)
    ).start()
    udp_socket = create_udp_socket()
    server_ready_event.wait()
    register_on_server(udp_socket, server_address, client_info["file_dir"], client_info)
    send_file_list_req(udp_socket, server_address)
