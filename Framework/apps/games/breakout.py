"""
Breakout by ands
"""

from Framework.apps.games import Game
from Framework.theme import theme

import random
import math



class Breakout(Game):
    def __init__(self, matrix, parent):
        super(Breakout, self).__init__(matrix, parent)
        self.paddle_x = 15

        self.ball = [17, 17]
        self.ball_attached = True
        self.speed = 0.7

        self.level = None
        self.count = 0

        self.loadlevel()

    def loadlevel(self):
        # [ands] TODO: Add multiple levels!

        self.level = [[1, 0, 1, 0, 1, 0, 1],
                      [0, 1, 0, 0, 0, 1, 0],
                      [1, 0, 2, 2, 2, 0, 1],
                      [0, 0, 2, 3, 2, 0, 0],
                      [1, 0, 2, 2, 2, 0, 1],
                      [0, 1, 0, 0, 0, 1, 0],
                      [1, 0, 1, 0, 1, 0, 1]]

        self.count = 0
        for y in range(0, 7):
            for x in range(0, 7):
                self.count += self.level[y][x]

    def loop(self):
        # Level
        for y in range(0, 7):
            for x in range(0, 7):
                c = (0, 0, 0)
                if self.level[y][x] == 3:
                    c = theme["breakout_block_3"]
                if self.level[y][x] == 2:
                    c = theme["breakout_block_2"]
                if self.level[y][x] == 1:
                    c = theme["breakout_block_1"]
                for i in range(0, 5):
                    self.frame[y * 2 + 0, x * 5 + i] = c
                    self.frame[y * 2 + 1, x * 5 + i] = c

        # Paddle
        if self.is_key_pressed("LEFT") and self.paddle_x > 0:
            self.frame[18, self.paddle_x + 4] = (0, 0, 0)
            self.paddle_x = self.paddle_x - 1
        if self.is_key_pressed("RIGHT") and self.paddle_x < 30:
            self.frame[18, self.paddle_x] = (0, 0, 0)
            self.paddle_x = self.paddle_x + 1
        for i in range(0, 5):
            self.frame[18, self.paddle_x + i] = theme["breakout_paddle"]

        # Ball
        self.frame[int(self.ball[1]), int(self.ball[0])] = (0, 0, 0)
        if self.ball_attached:
            self.ball[0] = self.paddle_x + 2
            self.ball[1] = 17
            if self.is_key_pressed("A"):
                self.ball_attached = False
                self.ball_velocity = [random.uniform(-1.0, 1.0), random.uniform(-0.1, -1.0)]
                v_length = math.sqrt(
                    self.ball_velocity[0] ** 2 + self.ball_velocity[1] ** 2)
                self.ball_velocity = [self.speed * self.ball_velocity[0] / v_length,
                                      self.speed * self.ball_velocity[1] / v_length]
        else:
            prev_cell = [int(self.ball[0] / 5), int(self.ball[1] / 2)]

            # Move
            self.ball[0] = self.ball[0] + self.ball_velocity[0]
            self.ball[1] = self.ball[1] + self.ball_velocity[1]

            # Hit walls
            if self.ball[0] < 0:
                self.ball[0] = 0
                self.ball_velocity[0] = -self.ball_velocity[0]
            if self.ball[0] > 34:
                self.ball[0] = 34
                self.ball_velocity[0] = -self.ball_velocity[0]
            if self.ball[1] < 0:
                self.ball[1] = 0
                self.ball_velocity[1] = -self.ball_velocity[1]
            if self.ball[1] > 19:
                self.ball_attached = True
                self.ball[1] = 19
                # [ands] TODO: Add "lives". Decrease them here. Add game over screen.

            # Hit paddle
            if int(self.ball[1]) == 18 and self.ball[0] >= self.paddle_x and self.ball[0] < self.paddle_x + 5:
                dx = self.paddle_x + 2 - self.ball[0]
                self.ball_velocity[0] = self.ball_velocity[0] - self.speed * 0.5 * dx
                v_length = math.sqrt(
                    self.ball_velocity[0] * self.ball_velocity[0] + self.ball_velocity[1] * self.ball_velocity[1])
                self.ball_velocity = [self.speed * self.ball_velocity[0] / v_length,
                                      self.speed * self.ball_velocity[1] / v_length]
                self.ball[1] = 17
                self.ball_velocity[1] = -self.ball_velocity[1]

            cell = [int(self.ball[0] / 5), int(self.ball[1] / 2)]

            # Hit block
            if cell[1] < 7 and self.level[cell[1]][cell[0]] > 0:
                self.level[cell[1]][cell[0]] = self.level[cell[1]][cell[0]] - 1
                self.count = self.count - 1
                if self.count == 0:
                    self.loadlevel()
                    self.ball_attached = True
                    self.speed = self.speed * 1.2
                else:
                    if cell[0] != prev_cell[0]:
                        self.ball_velocity[0] = -self.ball_velocity[0]
                    if cell[1] != prev_cell[1]:
                        self.ball_velocity[1] = -self.ball_velocity[1]

        self.frame[int(self.ball[1]), int(self.ball[0])] = theme["breakout_ball"]

        if self.is_key_up("B"):
            self.parent.back()
