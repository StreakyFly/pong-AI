import pygame


class Paddle:
    VEL = 4  # velocity

    SLIME_PADDLE_LEFT_SHADOW = pygame.image.load("Assets/SlimePaddleLeftShadow.png")
    SLIME_PADDLE_RIGHT_SHADOW = pygame.image.load("Assets/SlimePaddleRightShadow.png")

    def __init__(self, x, y, width, height, left, boost):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height
        self.left = left
        self.boost = boost

    def draw(self, win):
        if self.left:
            win.blit(self.SLIME_PADDLE_LEFT_SHADOW, (self.x - 5, self.y - 5))  # 5 is a fix for shadow size difference
        else:
            win.blit(self.SLIME_PADDLE_RIGHT_SHADOW, (self.x - 9, self.y - 5))  # 9 & 5 are a fix for shadow size difference
        # pygame.draw.rect(win, (255, 255, 255), (self.x, self.y, self.width, self.height))

    def move_no_boost(self, up=True):
        if up:
            self.y -= self.VEL
        else:
            self.y += self.VEL

    def move(self, up=True, fix=False):
        if not fix:
            if up:
                self.y -= int(self.VEL * self.boost)
            if up is False:
                self.y += int(self.VEL * self.boost)
        if fix:
            if up:
                self.y = 525-99  # 525 is window height, 99 is uhh paddle height sort of? dunno where that 1 pixel dissapears
            if up is False:
                self.y = 0

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
