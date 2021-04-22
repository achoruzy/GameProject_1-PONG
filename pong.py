# Copyright (c) 2021 Arkadiusz Choruży
# License: MIT

import pygame as pg
import sys
import random

pg.init()
pg.font.init()

# App variables
app_size = app_w, app_h = 1200, 740
app = pg.display.set_mode(app_size)
pg.display.set_caption('PONGme')

# Resolution downscaling
window_size = window_w, window_h = 240, 144
window = pg.surface.Surface(window_size)
window_center = cen_x, cen_y = int(window_w / 2), int(window_h / 2)

# Timer
FPS = 60
timer = pg.time.Clock()

# Fonts
game_font = pg.font.SysFont('Roboto.ttf', 24)

# Colors
BLACK = 0, 0, 0
GRAY = 100, 100, 100
WHITE = 255, 255, 255
WHITE_REDDISH = 255, 210, 210
RED = 255, 40, 0
BALL_COLOR = 146, 205, 240

# Gameplay variables
MOVE_SPD = 5
BALL_SPD = 2

plr_score = 0
enm_score = 0
plr_y = cen_y - 10
plr_x = int(window_w * 0.02)
enm_y = cen_y - 10
enm_x = int((window_w * 0.98) - 3)
ball_x, ball_y = cen_x - 3, cen_y - 3
rand_num = 0

ball_move = False
running = True
state = 'Title'


# Functions

def controls(pressed_list):
    """ Paddles control function"""
    global plr_y, enm_y

    if pressed_list[pg.K_w] and plr_y >= 0:
        plr_y -= 3
    if pressed_list[pg.K_s] and plr_y <= window_h - 20:
        plr_y += 3
    if pressed_list[pg.K_UP] and enm_y >= 0:
        enm_y -= 3
    if pressed_list[pg.K_DOWN] and enm_y <= window_h - 20:
        enm_y += 3


def random_num() -> float:
    """ Function generates random float for use on ball move direction"""
    return random.choice([random.uniform(-1, -0.8), random.uniform(0.8, 1)])


def score_reset():
    """
    Function resets score when new game starts
    """
    global plr_score, enm_score, plr_y, enm_y

    plr_score = 0
    enm_score = 0
    plr_y = cen_y - 10
    enm_y = cen_y - 10


class Title:
    def __init__(self):
        self.start_title = 'Press enter to start'
        self.color = WHITE
        self.pos_x = cen_x
        self.pos_y = cen_y
        self.font_size = 24
        self.font = 'Roboto.ttf'

        self.render_title()

    def render_title(self):
        """
        Function builds a title screen
        """
        window.fill(BLACK)
        title_font = pg.font.SysFont(self.font, self.font_size)
        title_text = title_font.render(self.start_title, False, self.color)
        title_text_pos = title_text.get_rect(centerx=self.pos_x, centery=self.pos_y)

        window.blit(title_text, title_text_pos)


class Level:
    def __init__(self):
        self.game_font = pg.font.SysFont('Roboto.ttf', 24)

        window.fill(BLACK)
        pg.draw.line(window, GRAY, (cen_x, 0), (cen_x, window_h), 1)
        window.blit(self.game_font.render(str(plr_score), False, WHITE), (window_w * 0.25, window_h * 0.1))
        window.blit(self.game_font.render(str(enm_score), False, WHITE), (window_w * 0.75, window_h * 0.1))

    def score_check(self):
        if enm_score == 10 or plr_score == 10:
            Ball.ball_reset()
            window.fill(GRAY)
            if enm_score > plr_score:
                game_over_text = 'Enemy WON!'
                window.blit(self.game_font.render(game_over_text, False, RED), (cen_x, cen_y))
            if enm_score < plr_score:
                game_over_text = 'Player WON!'
                window.blit(self.game_font.render(game_over_text, False, RED), (cen_x - 100, cen_y))


class Paddle:
    def __init__(self, pos_y, pos_x, color):
        self.width = 6
        self.height = 20

        self.player = pg.Rect(pos_x, pos_y, self.width, self.height)

        pg.draw.rect(window, color, self.player)


class Ball:
    def __init__(self):
        self.ball = pg.Rect(ball_x, ball_y, 6, 6)
        pg.draw.rect(window, BALL_COLOR, self.ball)

    @staticmethod
    def ball_reset():
        """ Function resets ball position and stops its movement"""
        global ball_x, ball_y, ball_move, BALL_SPD_x, BALL_SPD_y

        BALL_SPD_x = 0
        BALL_SPD_y = 0

        ball_x, ball_y = cen_x - 3, cen_y - 3
        ball_move = False

    @staticmethod
    def ball_start_move():
        """ Function initialise ball movement"""
        global ball_x, ball_y, BALL_SPD_x, BALL_SPD_y, ball_move

        if not ball_move:
            if pressed[pg.K_SPACE]:
                # Ball reset
                BALL_SPD_x, BALL_SPD_y = BALL_SPD, BALL_SPD
                rand_num_x = random_num()
                rand_num_y = random_num()
                BALL_SPD_x *= rand_num_x
                BALL_SPD_y *= rand_num_y
                ball_move = True

        if ball_move:
            ball_x += BALL_SPD_x
            ball_y += BALL_SPD_y

    def boundary_collision(self):
        """
        Function checks ball's collisions with window boundary.
        For collision with left or right window boundary, score for opposite player is added (+1).
        """
        global BALL_SPD_y, BALL_SPD_x, plr_score, enm_score

        if self.ball.bottom >= window_h:
            BALL_SPD_y *= -1

        if self.ball.top <= 0:
            BALL_SPD_y *= -1

        if self.ball.left <= 0:
            self.ball_reset()
            enm_score += 1

        if self.ball.right >= window_w:
            self.ball_reset()
            plr_score += 1

    def paddle_collision(self):
        """ Function checks for collisions with paddles"""
        global BALL_SPD_y, BALL_SPD_x
        if self.ball.colliderect(enemy.player):
            if abs(self.ball.right - enemy.player.left) < 4:
                BALL_SPD_x *= -1.2
        if self.ball.colliderect(player.player):
            if abs(self.ball.left - player.player.right) < 4:
                BALL_SPD_x *= -1.2


# Game Loop
if __name__ == '__main__':

    while running:
        # Upscaling app to window size
        pg.transform.scale(window, (1200, 740), app)

        # Get pressed keys
        pressed = pg.key.get_pressed()

        # Quit and Game state changes
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                running = False
                sys.exit()

            if ev.type == pg.KEYDOWN:
                if ev.key == pg.K_RETURN and state == 'Title':
                    state = 'Game'
                    score_reset()
                    Ball.ball_reset()

                if state == 'Game':
                    if ev.key == pg.K_ESCAPE:
                        state = 'Title'

        # GAME STATES
        if state == 'Title':
            title = Title()

        if state == 'Game':
            Ball.ball_start_move()

            # CONTROLS
            controls(pressed)

            # DRAW GAME
            level = Level()

            player = Paddle(plr_y, plr_x, WHITE)
            enemy = Paddle(enm_y, enm_x, WHITE_REDDISH)
            ball = Ball()

            # COLLISION CHECK
            ball.boundary_collision()
            ball.paddle_collision()

            # Score Check
            level.score_check()

        pg.display.update()
        timer.tick(FPS)
