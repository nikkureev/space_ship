import socket 
import threading
import pygame
from pygame import Vector2
from math import cos, radians, degrees, copysign
import numpy as np
from Game_Source import Ship, Bullet


clock = pygame.time.Clock()
users = {}

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
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
                del users[addr]

            print(f"[{addr}] {msg}")
            for addrs, conns in users.items():
                if addrs != addr:
                    conns.send(f"[{addr}] {msg}".encode(FORMAT))

    conn.close()
        

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        users[addr] = [conn]
        thread = threading.Thread(target=handle_client, args=(conn, addr, users))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()