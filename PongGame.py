from Paddle import Paddle
from Ball import Ball
from random import choice, randint
import pygame
pygame.init()


class GameInformation:
    def __init__(self, left_hits, right_hits, left_score, right_score):
        self.left_hits = left_hits
        self.right_hits = right_hits
        self.left_score = left_score
        self.right_score = right_score
        self.beans = "beans"  # does absolutely nothing 👍


class Game:
    """
    To use this class simply initialize an instance and call the .loop() method
    inside a pygame event loop (i.e. while loop). Inside your event loop
    you can call the .draw() and .move_paddle() methods according to your use case.
    Use the information returned from .loop() to determine when to end the game by calling .reset().
    """
    SCORE_FONT1 = pygame.font.Font("Assets/Fonts/8-bit Arcade In.ttf", 70)
    SCORE_FONT2 = pygame.font.Font("Assets/Fonts/8-bit Arcade Out.ttf", 70)
    FPS_FONT = pygame.font.Font("Assets/Fonts/Brandon Grotesque (Light).otf", 16)

    BALL_DEATH_SFX = pygame.mixer.Sound("Assets/Sounds/SlimeDeath.mp3")
    # BALL_DEATH_SFX = pygame.mixer.Sound("Assets/Sounds/bruh.mp3")
    # BALL_WALL_BOUNCE_SFX = pygame.mixer.Sound("Assets/Sounds/CartoonBoing.mp3")
    BALL_PADDLE_BOUNCE_1_SFX = pygame.mixer.Sound("Assets/Sounds/SlimeBounce1.mp3")
    BALL_PADDLE_BOUNCE_2_SFX = pygame.mixer.Sound("Assets/Sounds/SlimeBounce2.mp3")
    BALL_PADDLE_BOUNCE_3_SFX = pygame.mixer.Sound("Assets/Sounds/SlimeBounce3.mp3")
    BALL_PADDLE_BOUNCE_4_SFX = pygame.mixer.Sound("Assets/Sounds/SlimeBounce4.mp3")

    PADDLE_BOUNCE_SFX_LIST = [BALL_PADDLE_BOUNCE_1_SFX, BALL_PADDLE_BOUNCE_2_SFX,
                              BALL_PADDLE_BOUNCE_3_SFX, BALL_PADDLE_BOUNCE_4_SFX]

    BACKGROUND = pygame.image.load("Assets/Background.jpg")

    PADDLE_EFFECT_FIRE_IMG = pygame.image.load("Assets/PaddleEffectFire.jpg")
    PADDLE_EFFECT_FIRE_IMG.set_alpha(15)
    PADDLE_EFFECT_SLIME_IMG = pygame.image.load("Assets/PaddleEffectSlime.jpg")
    PADDLE_EFFECT_SLIME_IMG.set_alpha(15)

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    DARK_GREEN = (89, 175, 69)
    DARK2_GREEN = (74, 146, 58)

    PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
    BALL_RADIUS = 7

    ball_particles = []
    paddle_particles = []

    left_paddle_clicked = False
    right_paddle_clicked = False

    steps = 0

    def __init__(self, window, window_width, window_height, fps_multiplier):
        self.window_width = window_width
        self.window_height = window_height
        self.FPS_MULTIPLIER = fps_multiplier

        self.left_paddle = Paddle(10, self.window_height // 2 - self.PADDLE_HEIGHT // 2,
                                  self.PADDLE_WIDTH, self.PADDLE_HEIGHT, True, 1)
        self.right_paddle = Paddle(self.window_width - 10 - self.PADDLE_WIDTH, self.window_height // 2 - self.PADDLE_HEIGHT//2,
                                   self.PADDLE_WIDTH, self.PADDLE_HEIGHT, False, 1)
        self.ball = Ball(self.window_width // 2, self.window_height // 2, self.BALL_RADIUS, fps_multiplier)

        self.left_score = 0
        self.right_score = 0
        self.left_hits = 0
        self.right_hits = 0
        self.window = window

        self.ball_above_top_border = 0
        self.ball_below_bottom_border = 0

    def _draw_score(self):
        left_score_text = self.SCORE_FONT1.render(str(self.left_score), True, self.WHITE)
        right_score_text = self.SCORE_FONT1.render(str(self.right_score), True, self.WHITE)
        self.window.blit(left_score_text, (self.window_width // 4 - left_score_text.get_width()//2, 20))
        self.window.blit(right_score_text, (self.window_width * (3/4) - right_score_text.get_width()//2, 20))
        left_score_text = self.SCORE_FONT2.render(str(self.left_score), True, self.DARK_GREEN)
        right_score_text = self.SCORE_FONT2.render(str(self.right_score), True, self.DARK_GREEN)
        self.window.blit(left_score_text, (self.window_width // 4 - left_score_text.get_width()//2, 20))
        self.window.blit(right_score_text, (self.window_width * (3/4) - right_score_text.get_width()//2, 20))

    def _draw_hits(self):
        hits_text = self.SCORE_FONT1.render(str(self.left_hits + self.right_hits), True, self.WHITE)
        self.window.blit(hits_text, (self.window_width // 2 - hits_text.get_width()//2, 10))
        hits_text = self.SCORE_FONT2.render(str(self.left_hits + self.right_hits), True, self.DARK2_GREEN)
        self.window.blit(hits_text, (self.window_width // 2 - hits_text.get_width()//2, 10))

    def _handle_collision(self):
        ball = self.ball
        left_paddle = self.left_paddle
        right_paddle = self.right_paddle

        # trying to exploit poor game design to your advantage? well, I hope you like surprises... 😉
        if self.ball_above_top_border >= 180/self.FPS_MULTIPLIER:
            ball.y_vel = +7  # ball go down
            self.ball_above_top_border = 0
        elif self.ball_below_bottom_border >= 180/self.FPS_MULTIPLIER:
            ball.y_vel = -7  # ball go up??
            self.ball_below_bottom_border = 0

        elif ball.y + self.BALL_RADIUS >= self.window_height:
            ball.y_vel *= -1
            choice(self.PADDLE_BOUNCE_SFX_LIST).play()
            self.ball_below_bottom_border += 1
            self.ball_above_top_border = 0
        elif ball.y + self.BALL_RADIUS >= self.window_height-7:
            self.ball_below_bottom_border += 1

        elif ball.y - self.BALL_RADIUS <= 0:
            ball.y_vel *= -1
            choice(self.PADDLE_BOUNCE_SFX_LIST).play()
            self.ball_above_top_border += 1
            self.ball_below_bottom_border = 0
        elif ball.y - self.BALL_RADIUS <= 7:
            self.ball_above_top_border += 1

        if ball.x_vel < 0:
            if left_paddle.y <= ball.y + self.BALL_RADIUS and ball.y - self.BALL_RADIUS <= left_paddle.y + self.PADDLE_HEIGHT:
                if ball.x - self.BALL_RADIUS <= left_paddle.x + self.PADDLE_WIDTH:
                    ball.x_vel *= -1

                    middle_y = left_paddle.y + self.PADDLE_HEIGHT / 2
                    difference_in_y = middle_y - ball.y
                    reduction_factor = (self.PADDLE_HEIGHT / 2) / ball.MAX_VEL
                    y_vel = difference_in_y / reduction_factor
                    # "* 1+randint(1, 10)/100" changes the y_vel up to 10%, to make sure if the paddles are still,
                    # the ball can't get trapped in an endless/perfect loop
                    ball.y_vel = -1 * y_vel * 1+randint(1, 10)/100
                    self.left_hits += 1
                    choice(self.PADDLE_BOUNCE_SFX_LIST).play()
        else:
            if right_paddle.y <= ball.y + self.BALL_RADIUS and ball.y - self.BALL_RADIUS <= right_paddle.y + self.PADDLE_HEIGHT:
                if ball.x + self.BALL_RADIUS >= right_paddle.x:
                    ball.x_vel *= -1

                    middle_y = right_paddle.y + self.PADDLE_HEIGHT / 2
                    difference_in_y = middle_y - ball.y
                    reduction_factor = (self.PADDLE_HEIGHT / 2) / ball.MAX_VEL
                    y_vel = difference_in_y / reduction_factor
                    # "* 1+randint(1, 10)/100" changes the y_vel up to 10%, to make sure if the paddles are still,
                    # the ball can't get trapped in an endless/perfect loop
                    ball.y_vel = -1 * y_vel * 1+randint(1, 10)/100
                    self.right_hits += 1
                    choice(self.PADDLE_BOUNCE_SFX_LIST).play()

    def old_draw(self, clock=None, show_score=True, show_hits=False):
        """
        Initial draw method. Much simpler compared to the new draw method.
        Ball and paddle textures can be changed to white (or anything else) in Ball.py & Paddle.py.
        """
        self.window.fill(self.BLACK)

        pygame.draw.circle(self.window, (100, 0, 0), (self.window_width//2, self.window_height//2), 50)

        # draws divider/dotted line in the middle
        for i in range(0, self.window_height, self.window_height // 24):
            if i % 2 == 1:
                continue
            pygame.draw.rect(self.window, self.WHITE, (self.window_width // 2 - 5, i, 10, self.window_height // 24))

        if show_score:
            self._draw_score()
        if show_hits:
            self._draw_hits()

        self.left_paddle.draw(self.window)
        self.right_paddle.draw(self.window)

        self.ball.draw(self.window)

        if clock is not None:
            fps_text = pygame.font.SysFont(None, 24).render(str(round(clock.get_fps())), True, (128, 0, 0))
            self.window.blit(fps_text, (4, 4))

    def draw(self, clock=None, show_score=True, show_hits=False):
        """
        Draws a bunch of stuff on the screen that is of similar color as green beans
        """
        self.window.blit(self.BACKGROUND, (0, 0))

        if show_score:
            self._draw_score()
        if show_hits:
            self._draw_hits()

        self._paddle_particles(self.left_paddle)
        self._paddle_particles(self.right_paddle)

        self.left_paddle.draw(self.window)
        self.right_paddle.draw(self.window)

        self._ball_particles()
        self.ball.draw(self.window)

        if clock is not None:
            fps_text = self.FPS_FONT.render(str(round(clock.get_fps())), True, self.WHITE)
            self.window.blit(fps_text, (4, 3))

    def _ball_particles(self):
        if self.ball.x_vel < 0:  # if the ball is moving to the left
            rand_displacement = randint(0, 15)
        else:
            rand_displacement = randint(-15, 0)

        add_particle_every_x_step = round(1 / self.FPS_MULTIPLIER) if round(1 / self.FPS_MULTIPLIER) != 0 else 1
        if self.steps % add_particle_every_x_step == 0:
            self.ball_particles.append([[self.ball.x + rand_displacement, self.ball.y + randint(-2, 2)], [0, 0], randint(2, 4)])
        for particle in self.ball_particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 0.07 * self.FPS_MULTIPLIER  # particle disappear speed
            particle[1][1] += 0.01 * self.FPS_MULTIPLIER  # particle gravity force
            pygame.draw.circle(self.window, self.WHITE, [int(particle[0][0]), int(particle[0][1])], int(particle[2]))

            radius = particle[2] * 2
            self.window.blit(self._circle_surf(radius, self.DARK_GREEN),
                             (int(particle[0][0] - radius), int(particle[0][1] - radius)), special_flags=1)

            if particle[2] <= 0:
                self.ball_particles.remove(particle)

    def _paddle_particles(self, paddle):
        add_particle_every_x_step = round(1 / self.FPS_MULTIPLIER) if round(1 / self.FPS_MULTIPLIER) != 0 else 1
        if self.steps % add_particle_every_x_step == 0:
            self.paddle_particles.append([[paddle.x, paddle.y], [0, 0], 30])

        for particle in self.paddle_particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 1 * self.FPS_MULTIPLIER  # particle disappear speed

            # self.window.blit(self.PADDLE_EFFECT_FIRE_IMG, (int(particle[0][0]), int(particle[0][1])+randint(-14, 14)))
            self.window.blit(self.PADDLE_EFFECT_SLIME_IMG, (int(particle[0][0]), int(particle[0][1])))

            if particle[2] <= 0:
                self.paddle_particles.remove(particle)

    def _circle_surf(self, radius, color):
        surf = pygame.Surface((radius * 2, radius * 2))
        pygame.draw.circle(surf, color, (radius, radius), radius)
        surf.set_colorkey((0, 0, 0))
        return surf

    def move_paddle(self, left=True, up=True, no_press_left=False, no_press_right=False):
        """
        Move the left or right paddle.
        :returns: boolean indicating if paddle movement is valid.
        Movement is invalid if it causes paddle to go off the screen
        """
        BOOST_INCR = 0.03
        BOOST_LIMIT = 2.5

        if no_press_left:
            self.left_paddle.boost = 1
        if no_press_right:
            self.right_paddle.boost = 1

        if left:
            if self.left_paddle_clicked != up:
                self.left_paddle.boost = 1
                self.left_paddle_clicked = up
            else:
                if self.left_paddle.boost < BOOST_LIMIT:
                    self.left_paddle.boost += BOOST_INCR

            if up and self.left_paddle.y <= 0:
                self.left_paddle.move(not up, True)
                return False
            if not up and self.left_paddle.y + self.PADDLE_HEIGHT >= self.window_height:
                self.left_paddle.move(not up, True)
                return False

            self.left_paddle.move(up)

        elif left is False:
            if self.right_paddle_clicked != up:
                self.right_paddle.boost = 1
                self.right_paddle_clicked = up
            else:
                if self.right_paddle.boost < BOOST_LIMIT:
                    self.right_paddle.boost += BOOST_INCR

            if up and self.right_paddle.y <= 0:
                self.right_paddle.move(not up, True)
                return False
            if not up and self.right_paddle.y + self.PADDLE_HEIGHT >= self.window_height:
                self.right_paddle.move(not up, True)
                return False

            self.right_paddle.move(up)

        return True

    def loop(self, reset_hits=True):
        """
        Executes a single game loop.
        :returns: GameInformation instance stating score and hits of each paddle.
        """
        self.ball.move()
        self._handle_collision()

        if self.ball.x < 0:
            self.ball.reset()
            self.right_score += 1
            self.BALL_DEATH_SFX.play()
            if reset_hits:
                self.right_hits = 0
                self.left_hits = 0
        elif self.ball.x > self.window_width:
            self.ball.reset()
            self.left_score += 1
            self.BALL_DEATH_SFX.play()
            if reset_hits:
                self.left_hits = 0
                self.right_hits = 0

        game_info = GameInformation(self.left_hits, self.right_hits, self.left_score, self.right_score)

        return game_info

    def reset(self):
        """
        Resets the entire game.
        """
        self.ball.reset()
        self.left_paddle.reset()
        self.right_paddle.reset()
        self.left_score = 0
        self.right_score = 0
        self.left_hits = 0
        self.right_hits = 0
