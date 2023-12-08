import socket

def start_node_server(host="127.0.0.1", port=6000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(10)

    print(f"Server listening on {host}:{port}")

    while True:
        print("Waiting for a connection...")
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        data = client_socket.recv(1024).decode("utf-8")
        print(f"Received data: {data}")

        response = "Hello, World!"
        client_socket.send(response.encode("utf-8"))

        client_socket.close()
        print("Connection closed\n")
