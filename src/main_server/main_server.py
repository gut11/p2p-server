import socket
import threading
import queue


def start_main_server(host="127.0.0.1", port=6000):
    messages = queue.Queue()
    clients = {}  
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host,port))
    t1 = threading.Thread(target=receive, args=(server,messages)).start()
    t2 = threading.Thread(target=process_messages, args=(server,messages)).start()

def receive(server,messages):
    while True:
        try:
            message, addr = server.recvfrom(1024)
            messages.put((message, addr))
        except Exception as e:
            print(f"Error receiving message: {e}")

def handle_registration(server,message, addr):
    response = "OK <N>_REGISTERED_FILES"  
    server.sendto(response.encode(), addr)

def handle_update(server,message, addr):
    response = "OK <N>_REGISTERED_FILES"
    server.sendto(response.encode(), addr)

def handle_listing(server,message, addr):
    response = "MD51,NOME1,IP1:PORTA1;MD52,NOME2,IP2:PORTA2"  
    server.sendto(response.encode(), addr)

def handle_disconnect(server,message, addr):
    response = "OK CLIENT_FINISHED" 
    server.sendto(response.encode(), addr)

def process_messages(server,messages):
    while True:
        while not messages.empty():
            message, addr = messages.get()
            decoded_message = message.decode()

            if decoded_message.startswith("REG"):
                handle_registration(server,decoded_message, addr)
            elif decoded_message.startswith("UPD"):
                handle_update(server, decoded_message, addr)
            elif decoded_message.startswith("LST"):
                handle_listing(server, decoded_message, addr)
            elif decoded_message.startswith("END"):
                handle_disconnect(server, decoded_message, addr)
            else:
                response = "ERR INVALID_MESSAGE_FORMAT"
                server.sendto(response.encode(), addr)



