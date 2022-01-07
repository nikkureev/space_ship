import pygame
from math import sin, radians, degrees, copysign
from pygame import Vector2
import os
import math
import numpy as np


pygame.init()
screen_size = (500, 500)
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()
bg = pygame.image.load('C:/MY_GAMES/space_bg1.jpg')
current_dir = os.path.dirname(os.path.abspath(r'C:/MY_GAMES/spaceship1.png'))
image_path = os.path.join(current_dir, "spaceship1.png")
ship_image = pygame.image.load(image_path)
destr_image = pygame.image.load('C:/MY_GAMES/spaceship1.png')


class Ship():

    def __init__(self, x, y, angle=0.0, length=5, width=15, max_steering=3, max_acceleration=5.0, turning_velocity=20):
        self.position = Vector2(x, y)
        self.position1 = Vector2(1000, 1000)
        self.velocity = Vector2(0.0, 0.0)
        self.speed = 0.0
        self.angle = angle
        self.thrust = angle
        self.length = length
        self.width = width
        self.max_steering = max_steering
        self.max_acceleration = max_acceleration
        self.max_velocity = 30
        self.free_deceleration = 2
        self.brake_deceleration = 10
        self.turning_velocity = turning_velocity
        self.multiplier = 2

        self.health = 100
        self.start_health = 100
        self.health_bar = (self.position1.x - 12.5, self.position1.y - 35, 30, 7)
        self.hitbox = (self.position1.x - 25, self.position1.y - 25, 50, 50)
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
        # print(self.position.x, self.position.y)
        # self.bow = (self.position[0] + 10 * np.cos(self.thrust), self.position[1] + 10 * np.sin(self.thrust))
        # self.stern = (self.position[0] - 10 * np.cos(self.thrust), self.position[1] - 10 * np.sin(self.thrust))

        self.speed += self.acceleration * dt
        speed_component_x = self.speed * math.cos(radians(self.thrust))
        speed_component_y = self.speed * math.sin(radians(self.thrust))

        # self.velocity.x = speed_component_x
        # self.velocity.y = speed_component_y

        if self.steering:
            turning_angle = radians(degrees((self.speed + self.length) / math.sqrt(self.steering ** 2 + (self.speed + self.length) ** 2))) * dt
            if self.steering > 0:
                self.angle -= turning_angle * 10
            else:
                self.angle += turning_angle * 10

        # self.thrust = self.angle
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

        # self.velocity += (self.acceleration * dt, 0)
        # self.velocity.x = max(-self.max_velocity, min(self.velocity.x, self.max_velocity))
        #
        # if self.steering:
        #     turning_radius = self.length / sin(radians(self.steering))
        #     angular_velocity = self.turning_velocity / turning_radius
        # else:
        #     angular_velocity = 0
        #
        # self.old_position = self.position
        # new_position = self.position + self.velocity.rotate(-self.thrust) * dt
        # if 1000 >= new_position[0] >= 0 and 1000 >= new_position[1] >= 0:
        #     self.position = new_position
        #
        # self.angle += degrees(angular_velocity) * dt
        # if np.abs(self.angle) - np.abs(self.thrust) < 1:
        #     self.thrust = self.angle
        # else:
        #     if self.angle >= self.thrust:
        #         self.thrust += (np.abs(self.angle) - np.abs(self.thrust)) / (self.multiplier * self.velocity.x)
        #     elif self.angle <= self.thrust:
        #         self.thrust -= (np.abs(self.angle) - np.abs(self.thrust)) / (self.multiplier * self.velocity.x)
        # print(self.velocity.x, self.velocity.y)

        if 35 < self.health < 70:
            self.health_rate = 'Medium'
        elif 0 < self.health <= 35:
            self.health_rate = 'Low'
        elif self.health == 0:
            self.health_rate = 'Destroyed'

        healthy = 30 * self.health / self.start_health
        self.health_bar = (self.position1.x - 12.5, self.position1.y - 35, healthy, 7)
        preparing = 30 * self.shoot_timer / self.shoot_allow
        self.reload_bar = (self.position1.x - 12.5, self.position1.y + 30, preparing, 4)
        self.hitbox = (self.position1.x - 25, self.position1.y - 25, 50, 50)

    def hit(self, damage):
        self.health -= damage

    def update_coordinates(self):
        return (self.position.x, self.position.y)


class Bullet:

    def __init__(self, x, y, radius, color, angle, bsp, pos):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.angle = angle
        self.pos = pos
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
    screen.blit(rotated, board.position1 - (rect.width / 2, rect.height / 2))
    if board.health_rate == 'High':
        pygame.draw.rect(screen, board.health_color[0], board.health_bar)
    elif board.health_rate == 'Medium':
        pygame.draw.rect(screen, board.health_color[1], board.health_bar)
    else:
        pygame.draw.rect(screen, board.health_color[2], board.health_bar)
    pygame.draw.rect(screen, (0, 0, 255), board.reload_bar)

    # WHITE = (255, 255, 255)
    # GREEN = (0, 200, 64)
    # try:
    #     b1 = board.position[1] - board.position[0] * math.tan(board.angle)
    #     b2 = board.position[1] - board.position[0] * math.tan(board.thrust)
    #     print(board.angle, math.cos(board.angle), math.sin(board.angle))
    #     pygame.draw.line(screen, WHITE, [board.position[0], board.position[1]], [board.position[0] + 50 * math.cos(radians(board.thrust)), board.position[1] + 50 * math.sin(radians(board.thrust))])
    #     pygame.draw.line(screen, GREEN, [board.position[0], board.position[1]], [board.position[0] + 50 * math.cos(radians(board.angle)), board.position[1] + 50 * math.sin(radians(board.angle))])
    # except:
    #     pass


def redrawGameWindow(ship_list, new_x, new_y):
    #print('redraw', new_x, new_y)
    screen.blit(bg, (new_x, new_y))

    for board in ship_list:
        if board.health_rate == 'Destroyed':
            ship_draw(board, destr_image)
            ship_list.pop(ship_list.index(board))
        else:
            ship_draw(board, ship_image)

    for fires in bullets:
        fires.bullet_draw(screen)
    pygame.display.flip()

    pygame.display.update()


acceleration_slide = 0
speed_slide = 0

player = Ship(0, 0)
# enemy = Ship(100, 100)
# boards = [player, enemy]
boards = [player]
bullets = []

run = True
while run:
    player.position1.x = 250
    player.position1.y = 250
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
            if fires.y < board.hitbox[1] + board.hitbox[3] and fires.y > board.hitbox[1]:
                if fires.x > board.hitbox[0] and fires.x < board.hitbox[0] + board.hitbox[2]:
                    board.hit(player.damage)
                    bullets.pop(bullets.index(fires))
        if screen_size[0] > fires.x > 0 and screen_size[1] > fires.y > 0:
            fires.x += fires.x_ch
            fires.y += fires.y_ch
        else:
            bullets.pop(bullets.index(fires))

    pressed_key = pygame.key.get_pressed()
    pressed_mouse = pygame.mouse.get_pressed()
    if pressed_mouse[0]:
        if player.shoot_timer == player.shoot_allow:
            bullets.append(Bullet(round(player.position[0] + player.width // 2),
                                  round(player.position[1] + player.length // 2),
                                  4,
                                  (255, 0, 0),
                                  player.angle,
                                  player.bullet_speed, pos=pos))
            player.shoot_timer = 0
    if pressed_key[pygame.K_SPACE]:
        if player.shoot_timer == player.shoot_allow:
            bullets.append(Bullet(round(player.position[0] + player.width // 2),
                                  round(player.position[1] + player.length // 2),
                                  4,
                                  (255, 0, 0),
                                  player.angle,
                                  player.bullet_speed, pos=0))
            player.shoot_timer = 0
    if player.shoot_timer < player.shoot_allow:
        player.shoot_timer += 1


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
    player.update(dt)
    #print(player.update_coordinates())
    #enemy.update(dt)
    bgX = -player.update_coordinates()[0]
    bgY = -player.update_coordinates()[1]
    #print('script:', bgX, bdY)
    redrawGameWindow(boards, bgX, bgY)

pygame.quit()