import socket

def connect_to_main_server(ip,port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

