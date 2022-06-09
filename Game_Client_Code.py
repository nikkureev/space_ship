import socket
import threading

HEADER = 64
PORT = 8888
FORMAT = 'utf-8'
SERVER = "192.168.0.100"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send():
    while True:   
        msg = input()
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)


def recieve():
    print(client.recv(2048).decode(FORMAT))

while True:
    thread_send = threading.Thread(target=send)
    thread_send.start()
    thread_recieve = threading.Thread(target=recieve)
    thread_recieve.start()