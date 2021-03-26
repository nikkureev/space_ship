import pygame
from pygame import Vector2


game_size = (1000, 1000)
border_size = [200, 200]
player_screen = (500, 500)

screen = pygame.display.set_mode(game_size)
player_screen = pygame.display.set_mode(player_screen)
clock = pygame.time.Clock()


class Ship():

    def __init__(self, x_default, y_default, x, y):
        self.position = Vector2(x, y)
        self.position = Vector2(x_default, y_default)

    def draw_object(self, player, screen):
        if player:
            pygame.draw.rect(screen, (0, 0, 255), (enemy.position.x + x_slide, enemy.position.y + y_slide, 20, 20), 4)

band = 400
y_slide, x_slide = 0, 0
player = Ship(250, 250)
enemy = Ship(200, 200)
run = True
while run:
    screen.fill((0, 0, 0))
    clock.tick(60)
    dt = clock.get_time() / 100

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pressed_key = pygame.key.get_pressed()

    if pressed_key[pygame.K_UP]:
        if border_size[0] + y_slide <= player.position.y:
            y_slide += 1
    elif pressed_key[pygame.K_DOWN]:
        if player.position.y <= border_size[0] + 600 - 20 + y_slide:
            y_slide -= 1
    elif pressed_key[pygame.K_RIGHT]:
        if player.position.x <= border_size[1] + 600 - 20 + x_slide:
            x_slide -= 1
    elif pressed_key[pygame.K_LEFT]:
        if border_size[1] + x_slide <= player.position.x:
            x_slide += 1

    if enemy.position.y < band:
        enemy.position.y += 1
        band = 400
    else:
        enemy.position.y -= 1
        band = 200

    pygame.draw.rect(player_screen, (255, 0, 0), (border_size[1] + x_slide, border_size[0] + y_slide, 600, 600), 1)
    pygame.draw.rect(player_screen, (0, 0, 255), (player.position.x, player.position.y, 20, 20), 4)
    pygame.draw.rect(player_screen, (0, 0, 255), (enemy.position.x + x_slide, enemy.position.y + y_slide, 20, 20), 4)
    pygame.display.update()

pygame.quit()
