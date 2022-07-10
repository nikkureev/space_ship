import socket
import threading
import pickle 


HEADER = 64
PORT = 8888
FORMAT = 'utf-8'
SERVER = "192.168.0.100"
ADDR = (SERVER, PORT)
DISCONNECT_MESSAGE = "!DISCONNECT"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def handle_server():
    connected = True
    while connected:   
        data = [1, 2, 3]
        data_pocket = pickle.dumps(data)
        client.send(data_pocket)
    
        incomming_data = pickle.loads(client.recv(2048))
        if incomming_data == DISCONNECT_MESSAGE:
            print('[DISCONNECT]')
            connected = False
        
        print(incomming_data)


thread_serever = threading.Thread(target=handle_server)
thread_serever.start()
