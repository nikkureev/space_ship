import pygame
from math import sin, radians, degrees, copysign
from pygame import Vector2
import os


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
        self.health_bar = (self.position.x - 12.5, self.position.y - 50, 30, 7)
        self.hitbox = (self.position.x - 25, self.position.y - 25, 50, 50)

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

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += degrees(angular_velocity) * dt
        self.health_bar = (self.position.x - 12.5, self.position.y - 50, 30, 7)
        self.hitbox = (self.position.x - 25, self.position.y - 25, 50, 50)
        
        
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 1000))
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False

    def run(self):

        current_dir = os.path.dirname(os.path.abspath(r'C:/MY_GAMES/spaceship1.png'))
        image_path = os.path.join(current_dir, "spaceship1.png")
        ship_image = pygame.image.load(image_path)
        ship = Ship(0, 0)
        
        while not self.exit:
            dt = self.clock.get_time() / 100

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            pressed = pygame.key.get_pressed()

            if pressed[pygame.K_UP]:
                if ship.velocity.x < 0:
                    ship.acceleration = ship.brake_deceleration
                else:
                    ship.acceleration += 1 * dt
            elif pressed[pygame.K_DOWN]:
                if ship.velocity.x > 0:
                    ship.acceleration = -ship.brake_deceleration
                else:
                    ship.acceleration -= 1 * dt
            else:
                if abs(ship.velocity.x) > ship.free_deceleration:
                    ship.acceleration = -copysign(ship.free_deceleration, ship.velocity.x)
                else:
                    if dt != 0:
                        ship.acceleration = -ship.velocity.x / dt
            ship.acceleration = max(-ship.max_acceleration, min(ship.acceleration, ship.max_acceleration))

            if pressed[pygame.K_RIGHT]:
                ship.steering -= 30
            elif pressed[pygame.K_LEFT]:
                ship.steering += 30
            else:
                ship.steering = 0
            ship.steering = max(-ship.max_steering, min(ship.steering, ship.max_steering))

            ship.update(dt)

            self.screen.fill((0, 0, 0))
            rotated = pygame.transform.rotate(ship_image, ship.angle)
            rect = rotated.get_rect()
            self.screen.blit(rotated, ship.position - (rect.width / 2, rect.height / 2))
            pygame.draw.rect(self.screen, (255, 0, 0), ship.health_bar)
            pygame.draw.rect(self.screen, (255, 0, 0), ship.hitbox, 2)
            pygame.display.flip()

            self.clock.tick(self.ticks)
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
