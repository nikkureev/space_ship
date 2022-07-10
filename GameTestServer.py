import socket 
import threading
import pickle


HEADER = 64
PORT = 8888
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def handle_client(conn, addr, users):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        incomming_data = pickle.loads(conn.recv(2048))
        if incomming_data == DISCONNECT_MESSAGE:
            connected = False
            del users[addr]
        
        print(incomming_data)

        outgoing_data = [4, 5, 6]
        for conns in users.values():
            outgoing_pocket = pickle.dumps(outgoing_data)
            conns.send(outgoing_pocket)

    conn.close()
        

def start():
    server.listen()
    users = {}
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        users[addr] = conn
        thread = threading.Thread(target=handle_client, args=(conn, addr, users))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()
