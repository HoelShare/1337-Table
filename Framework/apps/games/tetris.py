from Framework.apps.games import Game
from Framework.theme import theme

import numpy as np
from random import randint


class Block(object):
    def __init__(self, shape, num):
        self.base_shape = self.shape = np.array(shape)
        self.num = num
        self.color = theme["tetris_%1d_color" % self.num]

        self.height = self.width = 0
        self.recalc()

        self.y = 0
        self.x = (10 / 2) - (self.width / 2)

        self.speed = 0.2

    def new(self):
        return Block(self.base_shape, self.num)

    def recalc(self):
        self.height, self.width = self.shape.shape

    def rot(self):
        self.shape = np.rot90(self.shape)
        self.recalc()

    def draw(self, frame):
        for x in range(0, self.width):
            for y in range(0, self.height):
                if self.shape[y, x]:
                    dx = int(self.x) + x
                    dy = int(self.y) + y
                    frame[dy, dx] = self.color

    def move_down(self, ibm):

        if (int(self.y) + self.height + self.speed) >= 20:
            return False

        y0 = int(self.y + self.speed)
        y1 = int(self.y + self.height + self.speed)
        x0 = int(self.x)
        x1 = int(self.x + self.width)
        for y in range(y0, y1):
            for x in range(x0, x1):
                if ibm[y, x] and self.shape[y - y0, x - x0]:
                    return False

        self.y += self.speed

        return True

    def move_left(self):
        self.move_horizontal(-self.speed)

    def move_right(self):
        self.move_horizontal(self.speed)

    def move_horizontal(self, x):
        prev = self.x
        self.x += x
        if self.x < 0:
            self.x = prev
        if int(self.x + self.width) > 10:
            self.x = prev

    def put_ibm(self, ibm):
        for x in range(0, self.width):
            for y in range(0, self.height):
                if self.shape[y, x]:
                    ibm[int(self.y) + y, int(self.x) + x] = 1


class Tetris(Game):
    def __init__(self, *args, **kwargs):
        super(Tetris, self).__init__(*args, **kwargs)

        self.blocks = [
            Block(
                [
                    [0, 1, 0],
                    [1, 1, 1]
                ], 1),
            Block(
                [
                    [1],
                    [1],
                    [1],
                    [1]
                ], 2),
            Block(
                [
                    [1, 0],
                    [1, 1],
                    [0, 1]
                ], 3),
            Block(
                [
                    [0, 1],
                    [1, 1],
                    [1, 0]
                ], 4),
            Block(
                [
                    [0, 1],
                    [0, 1],
                    [1, 1]
                ], 5),
            Block(
                [
                    [1, 0],
                    [1, 0],
                    [1, 1]
                ], 6),
            Block(
                [
                    [1, 1],
                    [1, 1]
                ], 7),
        ]

        self.active_block = self.blocks[randint(0, len(self.blocks) - 1)]
        self.inactive_blocks = []

    def loop(self):
        self.clear()

        ibm = np.zeros((20, 10))
        for block in self.inactive_blocks:
            block.put_ibm(ibm)
            block.draw(self.frame)

        if not self.active_block.move_down(ibm):
            self.inactive_blocks.append(self.active_block)
            self.active_block = self.blocks[randint(0, len(self.blocks) - 1)].new()

        self.active_block.draw(self.frame)

        if self.is_key_pressed("LEFT"):
            self.active_block.move_left()
        if self.is_key_pressed("RIGHT"):
            self.active_block.move_right()
        if self.is_key_up("UP"):
            self.active_block.rot()

        if self.is_key_down("B"):
            self.parent.back()
