from Framework.apps.games import Game
from Framework.theme import theme
from Framework.font import render_text
from random import uniform, randint
import numpy as np


class Paddle(object):
    def __init__(self, x, size=5):
        self.x = x
        self.size = size

        self.y = 10
        self.y0 = self.y - int(self.size / 2.)
        self.y1 = self.y + int(self.size / 2.)

        self.points = 0

    def recalc(self):
        self.y0 = self.y - int(self.size / 2.)
        self.y1 = self.y + int(self.size / 2.)

    def draw(self, frame):
        for y in range(self.y0, self.y1 + 1):
            frame[y, self.x] = theme["pong_paddle"]

    def move_up(self):
        self.y -= 1
        if self.y <= int(self.size / 2.) - 1:
            self.y += 1
        self.recalc()

    def move_down(self):
        self.y += 1
        if self.y >= 20 - int(self.size / 2.):
            self.y -= 1
        self.recalc()


class Ball(object):
    def __init__(self, left_paddle, right_paddle):
        self.x = 17
        self.y = 10

        self.speed = 1

        self.velocity = [-self.speed, 0]

        self.left_paddle = left_paddle
        self.right_paddle = right_paddle

        self.left_x = self.left_paddle.x
        self.right_x = self.right_paddle.x

        self.over_angle = -0.08
        self.max_angle = 0.5

        self.lasts = []

    def update(self):

        self.lasts.append([self.x, self.y])
        if len(self.lasts) > 10:
            self.lasts.pop(0)

        self.x += self.velocity[0]
        self.y += self.velocity[1]

        if int(self.y) >= 20 or int(self.y) < 0:
            self.y -= self.velocity[1]
            self.velocity[1] *= -1

        if int(self.x) == self.left_x:
            if int(self.y) >= self.left_paddle.y0 and int(self.y) <= self.left_paddle.y1:
                vy = uniform(-self.over_angle, self.max_angle)
                if self.right_paddle.y < 10:
                    vy *= -1
                self.velocity = [self.speed, vy]
            else:
                vy = uniform(-self.over_angle, self.max_angle)
                if self.right_paddle.y < 10:
                    vy *= -1
                self.velocity = [-self.speed, vy]
                self.x = 17
                self.right_paddle.points += 1

        if int(self.x) == self.right_x:
            if int(self.y) >= self.right_paddle.y0 and int(self.y) <= self.right_paddle.y1:
                vy = uniform(self.over_angle, -self.max_angle)
                if self.left_paddle.y < 10:
                    vy *= -1
                self.velocity = [-self.speed, vy]
            else:
                vy = uniform(-self.over_angle, self.max_angle)
                if self.left_paddle.y < 10:
                    vy *= -1
                self.velocity = [self.speed, vy]
                self.x = 17
                self.left_paddle.points += 1

    def draw(self, frame):
        for i in range(0, len(self.lasts)):
            x, y = self.lasts[i]
            n = (i / float(len(self.lasts))) / 2
            frame[int(y), int(x)] = np.uint8(np.array(theme["pong_ball"]) * n)

        frame[int(self.y), int(self.x)] = theme["pong_ball"]


class Pong(Game):
    def __init__(self, *args, **kwargs):
        super(Pong, self).__init__(*args, **kwargs)

        self.player_paddle = Paddle(2)
        self.computer_paddle = Paddle(32)

        self.ball = Ball(self.player_paddle, self.computer_paddle)

    def loop(self):

        self.clear()

        self.ball.update()

        scores = "%02x    %02x" % (self.player_paddle.points, self.computer_paddle.points)
        render_text(self.frame, theme["pong_score"], theme["background"], scores, 2, 2)

        c = randint(0, 100) > 30

        if self.ball.y > self.computer_paddle.y1 and c:
            self.computer_paddle.move_down()
        if self.ball.y < self.computer_paddle.y0 and c:
            self.computer_paddle.move_up()

        self.ball.draw(self.frame)
        self.player_paddle.draw(self.frame)
        self.computer_paddle.draw(self.frame)

        if self.is_key_pressed("UP"):
            self.player_paddle.move_up()
        if self.is_key_pressed("DOWN"):
            self.player_paddle.move_down()

        if self.is_key_up("B"):
            self.parent.back()
