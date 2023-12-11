import socket
import json
import hashlib

class P2PServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
        self.shared_files = {}

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            server_socket.bind((self.host, self.port))
            print(f"Server listening on {self.host}:{self.port}")

            while True:
                data, client_address = server_socket.recvfrom(1024)
                message = json.loads(data.decode())

                if 'type' not in message:
                    self.send_error_response(client_address)
                    continue

                message_type = message['type']

                if message_type == 'REG':
                    self.handle_registration(client_address, message)
                elif message_type == 'UPD':
                    self.handle_update(client_address, message)
                elif message_type == 'LST':
                    self.handle_list_request(client_address)
                elif message_type == 'END':
                    self.handle_disconnect(client_address)
                else:
                    self.send_error_response(client_address)

    def send_error_response(self, client_address):
        response = {'type': 'ERR', 'message': 'INVALID_MESSAGE_FORMAT'}
        self.send_message(client_address, response)

    def handle_registration(self, client_address, message):
        password = message.get('password')
        port = message.get('port')
        files = message.get('files')

        if password and port and files:
            md5_files = self.process_files(files)
            self.clients[client_address] = {'password': password, 'port': port, 'files': md5_files}
            self.update_shared_files()
            self.send_registration_response(client_address, len(md5_files))
        else:
            self.send_error_response(client_address)

    def process_files(self, files):
        md5_files = []
        for file_info in files.split(';'):
            md5, name = file_info.split(',')
            md5_files.append({'md5': md5, 'name': name})
        return md5_files

    def handle_update(self, client_address, message):
        password = message.get('password')
        client_files = message.get('files')
        port = message.get('port')

        if client_address in self.clients and password and port and client_files is not None:
            if self.clients[client_address]['password'] == password:
                md5_files = self.process_files(client_files)
                self.clients[client_address]['port'] = port
                self.clients[client_address]['files'] = md5_files
                self.update_shared_files()
                self.send_registration_response(client_address, len(md5_files))
            else:
                self.send_password_error_response(client_address)
        else:
            self.send_error_response(client_address)

    def send_password_error_response(self, client_address):
        response = {'type': 'ERR', 'message': 'IP_REGISTERED_WITH_DIFFERENT_PASSWORD'}
        self.send_message(client_address, response)

    def handle_list_request(self, client_address):
        if client_address in self.clients:
            files_list = self.generate_files_list()
            response = {'type': 'LST', 'files': files_list}
            self.send_message(client_address, response)
        else:
            self.send_error_response(client_address)

    def generate_files_list(self):
        files_list = []
        for md5, file_info in self.shared_files.items():
            file_entry = f"{md5},{file_info['name']}"
            clients_list = ';'.join([f"{client['client']}:{client['port']}" for client in file_info['clients']])
            files_list.append(f"{file_entry},{clients_list}")

        return ';'.join(files_list)

    def handle_disconnect(self, client_address, message):
        password = message.get('password')
        port = message.get('port')

        if client_address in self.clients and password and port:
            if self.clients[client_address]['password'] == password:
                del self.clients[client_address]
                self.update_shared_files()
                self.send_disconnect_response(client_address)
            else:
                self.send_password_error_response(client_address)
        else:
            self.send_error_response(client_address)

    def send_disconnect_response(self, client_address):
        response = {'type': 'OK', 'message': 'CLIENT_FINISHED'}
        self.send_message(client_address, response)

    def update_shared_files(self):
        self.shared_files = {}
        for client_address, client_info in self.clients.items():
            for file_info in client_info['files']:
                md5 = file_info['md5']
                name = file_info['name']
                if md5 not in self.shared_files:
                    self.shared_files[md5] = []
                self.shared_files[md5].append({'name': name, 'client': client_info['password']})

    def send_registration_response(self, client_address, num_registered_files):
        response = {'type': 'OK', 'message': f'{num_registered_files}_REGISTERED_FILES'}
        self.send_message(client_address, response)

    def send_success_response(self, client_address):
        response = {'type': 'OK'}
        self.send_message(client_address, response)

    def send_message(self, client_address, message):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.sendto(json.dumps(message).encode(), client_address)
