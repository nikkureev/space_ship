import pygame
from math import sin, radians, degrees, copysign
from pygame import Vector2
import os
import math


pygame.init()
screen_size = (1000, 1000)
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()
bg = pygame.image.load('C:/SpaceShip/space_bg.jpg')
current_dir = os.path.dirname(os.path.abspath(r'C:/SpaceShip/spaceship.png'))
image_path = os.path.join(current_dir, "spaceship.png")
ship_image = pygame.image.load(image_path)
destr_image = pygame.image.load('C:/SpaceShip/exp_img.png')


class Ship():

    def __init__(self, x, y, angle=0.0, length=5, width=15, max_steering=3, max_acceleration=5.0, turning_velocity=20):
        self.position = Vector2(x, y)
        self.velocity = Vector2(0.0, 0.0)
        self.angle = angle
        self.length = length
        self.width = width
        self.max_steering = max_steering
        self.max_acceleration = max_acceleration
        self.max_velocity = 30
        self.free_deceleration = 2
        self.brake_deceleration = 10
        self.turning_velocity = turning_velocity

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
        self.velocity += (self.acceleration * dt, 0)
        self.velocity.x = max(-self.max_velocity, min(self.velocity.x, self.max_velocity))

        if self.steering:
            turning_radius = self.length / sin(radians(self.steering))
            angular_velocity = self.turning_velocity / turning_radius
        else:
            angular_velocity = 0

        if 35 < self.health < 70:
            self.health_rate = 'Medium'
        elif 0 < self.health <= 35:
            self.health_rate = 'Low'
        elif self.health == 0:
            self.health_rate = 'Destroyed'

        self.old_position = self.position
        new_position = self.position + self.velocity.rotate(-self.angle) * dt
        if 1000 >= new_position[0] >= 0 and 1000 >= new_position[1] >= 0:
            self.position = new_position
        self.angle += degrees(angular_velocity) * dt
        healthy = 30 * self.health / self.start_health
        self.health_bar = (self.position.x - 12.5, self.position.y - 35, healthy, 7)
        preparing = 30 * self.shoot_timer / self.shoot_allow
        self.reload_bar = (self.position.x - 12.5, self.position.y + 30, preparing, 4)
        self.hitbox = (self.position.x - 25, self.position.y - 25, 50, 50)

    def hit(self, damage):
        self.health -= damage


class Bullet:

    def __init__(self, x, y, radius, color, angle, bsp):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.angle = angle
        self.x_ch = int(math.cos(radians(self.angle)) * bsp)
        self.y_ch = int(math.sin(radians(self.angle)) * bsp)

    def bullet_draw(self, field):
        pygame.draw.circle(field, self.color, (self.x, self.y), self.radius)


def ship_draw(board, img):
    rotated = pygame.transform.rotate(img, board.angle)
    rect = rotated.get_rect()
    screen.blit(rotated, board.position - (rect.width / 2, rect.height / 2))
    if board.health_rate == 'High':
        pygame.draw.rect(screen, board.health_color[0], board.health_bar)
    elif board.health_rate == 'Medium':
        pygame.draw.rect(screen, board.health_color[1], board.health_bar)
    else:
        pygame.draw.rect(screen, board.health_color[2], board.health_bar)
    pygame.draw.rect(screen, (0, 0, 255), board.reload_bar)


def redrawGameWindow(ship_list):
    screen.blit(bg, (0, 0))

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


player = Ship(0, 0)
enemy = Ship(100, 100)
boards = [player, enemy]
bullets = []

run = True
while run:
    clock.tick(60)
    dt = clock.get_time() / 100

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    for fires in bullets:
        if fires.y < enemy.hitbox[1] + enemy.hitbox[3] and fires.y > enemy.hitbox[1]:
            if fires.x > enemy.hitbox[0] and fires.x < enemy.hitbox[0] + enemy.hitbox[2]:
                enemy.hit(player.damage)
                bullets.pop(bullets.index(fires))
        if screen_size[0] > fires.x > 0 and screen_size[1] > fires.y > 0:
            fires.x += fires.x_ch
            fires.y += fires.y_ch
        else:
            bullets.pop(bullets.index(fires))

    pressed = pygame.key.get_pressed()

    if pressed[pygame.K_SPACE]:
        if player.shoot_timer == player.shoot_allow:
            bullets.append(Bullet(round(player.position[0] + player.width // 2),
                                  round(player.position[1] + player.length // 2),
                                  4,
                                  (255, 0, 0),
                                  -player.angle,
                                  player.bullet_speed))
            player.shoot_timer = 0
    if player.shoot_timer < player.shoot_allow:
        player.shoot_timer += 1

    if pressed[pygame.K_UP]:
        if player.velocity.x < 0:
            player.acceleration = player.brake_deceleration
        else:
            player.acceleration += 1 * dt
    elif pressed[pygame.K_DOWN]:
        if player.velocity.x > 0:
            player.acceleration = -player.brake_deceleration
        else:
            player.acceleration -= 1 * dt
    else:
        if abs(player.velocity.x) > player.free_deceleration:
            player.acceleration = -copysign(player.free_deceleration, player.velocity.x)
        else:
            if dt != 0:
                player.acceleration = -player.velocity.x / dt
    player.acceleration = max(-player.max_acceleration, min(player.acceleration, player.max_acceleration))

    if pressed[pygame.K_RIGHT]:
        player.steering -= 30
    elif pressed[pygame.K_LEFT]:
        player.steering += 30
    else:
        player.steering = 0
    player.steering = max(-player.max_steering, min(player.steering, player.max_steering))
    player.update(dt)
    enemy.update(dt)

    redrawGameWindow(boards)

pygame.quit()
