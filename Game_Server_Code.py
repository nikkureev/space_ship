import socket 
import threading
import pygame
import math
from Game_Source import Ship, Bullet
import pickle
import random


pygame.init()
game_size = ((200, 1720), (200, 1720))
clock = pygame.time.Clock()
players = {}

HEADER = 64
PORT = 8888
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def handle_client(conn, addr, users, number):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        clock.tick(60)
        dt = clock.get_time() / 100

        # try:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = pickle.loads(conn.recv(msg_length))
            if msg['DISCONNECT'] == True:
                connected = False
                del users[addr]

            ship = players[number]['Ship']
            bullets = players[number]['Bullets']
            if msg['Left mouse key pressed'] == True:
                if ship.shoot_timer == ship.shoot_allow:
                    bullets.append(Bullet(round(ship.position[0] + ship.width // 2),
                                          round(ship.position[1] + ship.length // 2),
                                          4,
                                          (255, 0, 0),
                                          ship.angle,
                                          ship.bullet_speed, pos=msg['Mouse position']))
                    ship.shoot_timer = 0

            if msg['UP/W pressed'] == True:
                if ship.speed < ship.max_velocity:
                    ship.acceleration = ship.brake_deceleration
                else:
                    ship.acceleration = 0

            elif msg['DOWN/S pressed'] == True:
                if ship.speed > 0:
                    ship.acceleration = -ship.brake_deceleration
                else:
                    ship.acceleration = 0

            else:
                if abs(ship.speed) > ship.free_deceleration:
                    ship.acceleration = -math.copysign(ship.free_deceleration, ship.speed)
                else:
                    if dt != 0:
                        ship.acceleration = -ship.speed / dt
            ship.acceleration = max(-ship.max_acceleration, min(ship.acceleration, ship.max_acceleration))

            if msg['RIGHT/D pressed'] == True:
                ship.steering -= 30

            elif msg['LEFT/A pressed'] == True:
                ship.steering += 30

            else:
                ship.steering = 0

            ship.steering = max(-ship.max_steering, min(ship.steering, ship.max_steering))
            
            if ship.shoot_timer < ship.shoot_allow:
                ship.shoot_timer += 1

            ship.update(dt)

            if game_size[0][1] >= ship.new_position[0] >= game_size[0][0] and game_size[1][1] >= ship.new_position[1] >= game_size[1][0]:
                ship.position = ship.new_position

            for bullet in bullets:
                for player_number, player_items in players.items():
                    if bullet.y < player_items['Ship'].hitbox[1] + player_items['Ship'].hitbox[3] and bullet.y > player_items['Ship'].hitbox[1]:
                        if bullet.x > player_items['Ship'].hitbox[0] and bullet.x < player_items['Ship'].hitbox[0] + player_items['Ship'].hitbox[2]:
                            player_items['Ship'].hit(player_items['Ship'].damage)
                            bullets.pop(bullets.index(bullet))

                    if game_size[0][1] > bullet.x > game_size[0][0] and game_size[1][1] > bullet.y > game_size[1][0]:
                        bullet.x += bullet.x_ch
                        bullet.y += bullet.y_ch

                    else:
                        try:
                            bullets.pop(bullets.index(bullet))
                        except:
                            None
            
            for number, items in players.items():
                conn.send(f"{number}".encode(FORMAT))
                data = pickle.dumps(players)
                conn.send(data)
        # except:
        #     connected = False
        #     del players[addr]
        #     print(f"[DISCONNECT] {addr}")
    conn.close()
        

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        number = random.randint(100, 1000)
        conn, addr = server.accept()
        players[number] = {'Ship': Ship(300, 300),
                           'Bullets': []}
        player_thread = threading.Thread(target=handle_client, args=(conn, addr, players, number))
        player_thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()