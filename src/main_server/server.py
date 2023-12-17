import socket

def parse_hash_file_format(files_string):
    files = files_string.split(";")
    result = []

    for file_info in files:
        hash_value, name = file_info.split(",")
        result.append({"md5": hash_value, "name": name})

    return result

def split_registration_info(message):
    parts = message.split(" ")

    if len(parts) == 4:
        return parts[1], parts[2], parts[3]
    else:
        return None

def split_req_info(message):
    parts = message.split(" ")

    if len(parts) != 0:
        return parts
    else:
        return None

def identify_message_type(message):
    parts = message.split(" ", 1)

    if len(parts) > 0:
        message_type = parts[0]
        if message_type in ["REG", "UPD", "LST", "END"]:
            return message_type
    return "UNKNOWN"

def send_error_response(client_address):
    response = {"type": "ERR", "message": "INVALID_MESSAGE_FORMAT"}
    send_message(client_address, response)

def handle_registration(client_address, message, clients):
    result = split_registration_info(message)
    password = None
    port = None
    files = None

    if result is not None:
        password, port, files = result

    files_list = parse_hash_file_format(files)

    if password and port and files:
        clients[client_address] = {
            "password": password,
            "port": port,
            "files": files_list,
        }
        send_registration_response(client_address, len(files_list))
    else:
        send_error_response(client_address)

def process_files(files):
    md5_files = []
    for file_info in files.split(";"):
        md5, name = file_info.split(",")
        md5_files.append({"md5": md5, "name": name})
    return md5_files

def handle_update(client_address, message, clients):
    result = split_req_info(message)
    password = None
    port = None
    files = None

    if result is not None and len(result) >= 3:
        _, password, port, files, *_= result

    if client_address in clients and password and port:
        if check_password(clients[client_address]["password"], password):
            files_list = parse_hash_file_format(files)

            clients[client_address] = {
                "password": password,
                "port": port,
                "files": files_list,
            }
            send_registration_response(client_address, len(files_list))
        else: 
            send_password_error_response(client_address)
    else:
        send_error_response(client_address)


def send_password_error_response(client_address):
    response = "ERR IP_REGISTERED_WITH_DIFFERENT_PASSWORD"
    send_message(client_address, response)

def handle_list_request(client_address, clients):
    print(clients)
    if client_address in clients:
        files_list = generate_files_list(clients)
        response = files_list
        send_message(client_address, response)
    else:
        send_error_response(client_address)

def generate_files_list(clients):
    files_list = []
    for address, client_infos in clients.items():
        files = client_infos.get("files", [])

        for file in files:
            md5, name = file.values()
            file_entry = f"{md5},{name}"
            clients_list = ";".join([f"{address[0]}:{clients[address]['port']}"])
            files_list.append(f"{file_entry},{clients_list}")

    return ";".join(files_list)

def handle_disconnect(client_address, message, clients):

    split = split_req_info(message)
    password = None
    port = None


    if split != None and len(split) >= 2:
        _, password, port, *_ = split
    else:
        send_error_response(client_address)
    
    if client_address in clients and password and port:
        if check_password(clients[client_address]["password"], password):
            if clients[client_address]["password"] == password:
                del clients[client_address]
                send_disconnect_response(client_address)
            else:
                send_password_error_response(client_address)


def send_disconnect_response(client_address):
    response = "OK CLIENT_FINISHED"
    send_message(client_address, response)

def send_registration_response(client_address, num_registered_files):
    response = "OK " f"{num_registered_files}_REGISTERED_FILES"
    send_message(client_address, response)

def send_message(client_address, message):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        client_socket.sendto(message.encode(), client_address)

def check_password(req_password, ip_password):
    if req_password == ip_password:
        return True
    else:
        return False


def start_server(host="", port=54494):
    clients = {}
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((host, port))
        print(f"Server listening on {host}:{port}")

        while True:
            data, client_address = server_socket.recvfrom(1024)
            message = data.decode()
            req_type = identify_message_type(message)

            if req_type == "REG":
                handle_registration(client_address, message, clients)
            elif req_type == "UPD":
                handle_update(client_address, message, clients)
            elif req_type == "LST":
                handle_list_request(client_address, clients)
            elif req_type == "END":
                handle_disconnect(client_address, message, clients)
            else:
                send_error_response(client_address)

# Start the server
start_server()
