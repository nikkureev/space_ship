import pygame
from math import sin, radians, degrees, copysign
from pygame import Vector2
import os
import math
import numpy as np


pygame.init()
screen_size_player = (500, 500)
screen_size_observer = (1000, 1000)

screen = pygame.display.set_mode(screen_size_observer)
clock = pygame.time.Clock()

bg = pygame.image.load('C:/MY_GAMES/space_bg1.jpg')
ship_image = pygame.image.load('C:/MY_GAMES/spaceship1.png')
destr_image = pygame.image.load('C:/MY_GAMES/spaceship1.png')

class Ship():

    def __init__(self, mark, x, y, angle=0.0, length=5, width=15, max_steering=3, max_acceleration=5.0, turning_velocity=20):
        self.position = Vector2(x, y)
        self.velocity = Vector2(0.0, 0.0)

        self.mark = mark
        self.angle = angle
        self.thrust = angle
        self.length = length
        self.width = width
        self.max_steering = max_steering
        self.max_acceleration = max_acceleration
        self.turning_velocity = turning_velocity

        self.speed = 0.0
        self.max_velocity = 30
        self.free_deceleration = 2
        self.brake_deceleration = 10
        self.multiplier = 2
        self.health = 100
        self.start_health = 100
        
        self.health_bar = (self.position.x - 12.5, self.position.y - 35, 30, 7)
        self.hitbox = (self.position.x - 25, self.position.y - 25, 50, 50)
        self.health_color = ((0, 255, 0), (255, 255, 0), (255, 0, 0))
        self.health_rate = 'High'

        self.damage = 5
        self.shoot_allow = 15
        self.shoot_timer = 0
        self.reload_bar = (self.position.x - 12.5, self.position.y + 30, 30, 4)
        self.bullet_speed = 14

        self.acceleration = 0.0
        self.steering = 0.0

    def update(self, dt):
        self.speed += self.acceleration * dt
        speed_component_x = self.speed * math.cos(radians(self.thrust))
        speed_component_y = self.speed * math.sin(radians(self.thrust))

        if self.steering:
            turning_angle = radians(degrees((self.speed + self.length) / math.sqrt(self.steering ** 2 + (self.speed + self.length) ** 2))) * dt
            if self.steering > 0:
                self.angle -= turning_angle * 10
            else:
                self.angle += turning_angle * 10

        if np.abs(self.angle) - np.abs(self.thrust) < 1:
            self.thrust = self.angle
        else:
            if self.angle >= self.thrust:
                self.thrust += (np.abs(self.angle) - np.abs(self.thrust)) / ((self.speed + 1) / 5) ** self.multiplier
            elif self.angle <= self.thrust:
                self.thrust -= (np.abs(self.angle) - np.abs(self.thrust)) / ((self.speed + 1) / 5) ** self.multiplier

        self.old_position = self.position
        new_position = self.position + (speed_component_x * dt, speed_component_y * dt)
        if 1000 >= new_position[0] >= 0 and 1000 >= new_position[1] >= 0:
            self.position = new_position

        if 35 < self.health < 70:
            self.health_rate = 'Medium'
        elif 0 < self.health <= 35:
            self.health_rate = 'Low'
        elif self.health == 0:
            self.health_rate = 'Destroyed'

        healthy = 30 * self.health / self.start_health
        self.health_bar = (self.position.x - 12.5, self.position.y - 35, healthy, 7)
        preparing = 30 * self.shoot_timer / self.shoot_allow
        self.reload_bar = (self.position.x - 12.5, self.position.y + 30, preparing, 4)
        self.hitbox = (self.position.x - 25, self.position.y - 25, 50, 50)

    def hit(self, damage):
        self.health -= damage

    def update_coordinates(self):
        return (self.position.x, self.position.y)


class Bullet:

    def __init__(self, x, y, radius, color, angle, bsp, pos, owner):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.angle = angle
        self.pos = pos
        self.owner = owner

        if pos:
            self.adj = 0
            if self.x - self.pos[0] < 0:
                self.adj = 180
            try:
                self.k = (self.y - self.pos[1]) / (self.x - self.pos[0])
                self.deg = math.degrees(math.atan(self.k))
            except ZeroDivisionError:
                if self.y - self.pos[1] < 0:
                    self.adj = 90
                    self.deg = 0
                else:
                    self.adj = 270
                    self.deg = 0

            self.x_ch = float(math.cos(math.radians(self.deg - self.adj + 180)) * bsp)
            self.y_ch = float(math.sin(math.radians(self.deg - self.adj + 180)) * bsp)

        else:
            self.x_ch = float(math.cos(radians(self.angle)) * bsp)
            self.y_ch = float(math.sin(radians(self.angle)) * bsp)

    def bullet_draw(self, field):
        pygame.draw.circle(field, self.color, (int(self.x), int(self.y)), self.radius)


def ship_draw(board, img):
    rotated = pygame.transform.rotate(img, -board.angle)
    rect = rotated.get_rect()
    screen.blit(rotated, board.position - (rect.width / 2, rect.height / 2))
    if board.health_rate == 'High':
        pygame.draw.rect(screen, board.health_color[0], board.health_bar)
    elif board.health_rate == 'Medium':
        pygame.draw.rect(screen, board.health_color[1], board.health_bar)
    else:
        pygame.draw.rect(screen, board.health_color[2], board.health_bar)
    pygame.draw.rect(screen, (0, 0, 255), board.reload_bar)


def redrawGameWindow(ship_list, bullet_list):
    screen.blit(bg, (0, 0))
 
    for board in ship_list:
        if board.health_rate == 'Destroyed':
            ship_draw(board, destr_image)
            ship_list.pop(ship_list.index(board))
        else:
            ship_draw(board, ship_image)

    for fires in bullet_list:
        fires.bullet_draw(screen)
    pygame.display.flip()

    pygame.display.update()


acceleration_slide = 0
speed_slide = 0

player = Ship('player', 0, 0)
enemy = Ship('enemy', 250, 250)
boards = [player, enemy]
bullets = []

run = True
while run:
    screen.fill((0, 0, 0))
    clock.tick(60)
    dt = clock.get_time() / 100

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEMOTION:
            pos = event.pos

    for fires in bullets:
        for board in boards:
            if fires.owner != board.mark:
                if fires.y < board.hitbox[1] + board.hitbox[3] and fires.y > board.hitbox[1]:
                    if fires.x > board.hitbox[0] and fires.x < board.hitbox[0] + board.hitbox[2]:
                        board.hit(board.damage)
                        bullets.pop(bullets.index(fires))
            if screen_size_observer[0] > fires.x > 0 and screen_size_observer[1] > fires.y > 0:
                fires.x += fires.x_ch
                fires.y += fires.y_ch
            else:
                try:
                    bullets.pop(bullets.index(fires))
                except:
                    None

    pressed_key = pygame.key.get_pressed()
    pressed_mouse = pygame.mouse.get_pressed()
    if pressed_mouse[0]:
        if player.shoot_timer == player.shoot_allow:
            bullets.append(Bullet(round(player.position[0] + player.width // 2),
                                  round(player.position[1] + player.length // 2),
                                  4,
                                  (255, 0, 0),
                                  player.angle,
                                  player.bullet_speed, pos=pos, owner='player'))
            player.shoot_timer = 0

    for board in boards:
        if board.shoot_timer < board.shoot_allow:
            board.shoot_timer += 1

    if pressed_key[pygame.K_UP]:
        if player.speed < player.max_velocity:
            player.acceleration = player.brake_deceleration
        else:
            player.acceleration = 0
    elif pressed_key[pygame.K_DOWN]:
        if player.speed > 0:
            player.acceleration = -player.brake_deceleration
        else:
            player.acceleration = 0
    else:
        if abs(player.speed) > player.free_deceleration:
            player.acceleration = -copysign(player.free_deceleration, player.speed)
        else:
            if dt != 0:
                player.acceleration = -player.speed / dt
    player.acceleration = max(-player.max_acceleration, min(player.acceleration, player.max_acceleration))

    if pressed_key[pygame.K_RIGHT]:
        player.steering -= 30
    elif pressed_key[pygame.K_LEFT]:
        player.steering += 30
    else:
        player.steering = 0

    player.steering = max(-player.max_steering, min(player.steering, player.max_steering))
    for board in boards:
        board.update(dt)
    redrawGameWindow(boards, bullets)

pygame.quit()

