import pygame
import random
import math


class Ball:
    MAX_VEL = 6  # basically the default speed of ball

    SLIME_BALL_SHADOW = pygame.image.load("Assets/SlimeballShadow.png")

    def __init__(self, x, y, radius, fps_multiplier):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.radius = radius
        self.MAX_VEL *= fps_multiplier

        angle = self._get_random_angle(-30, 30, [0])
        side = 1 if random.random() < 0.5 else -1

        self.x_vel = side * abs(math.cos(angle) * self.MAX_VEL)
        self.y_vel = math.sin(angle) * self.MAX_VEL

    def _get_random_angle(self, min_angle, max_angle, excluded):
        angle = 0
        while angle in excluded:
            angle = math.radians(random.randrange(min_angle, max_angle))
        return angle

    def draw(self, win):
        win.blit(self.SLIME_BALL_SHADOW, (self.x - self.radius - 5, self.y - self.radius - 5))  # 5 is a fix for shadow size difference
        # pygame.draw.circle(win, (255, 255, 255), (self.x, self.y), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y

        angle = self._get_random_angle(-30, 30, [0])
        y_vel = math.sin(angle) * self.MAX_VEL

        self.y_vel = y_vel
        self.x_vel *= -1
