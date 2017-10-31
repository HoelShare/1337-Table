from Framework.apps.games import Game
from Framework.theme import theme
import numpy as np


class Block(object):
    def __init__(self, shape):
        self.shape = np.array(shape)
        self.height, self.width = self.shape.shape

        self.x = self.y = 0

    def new(self):
        return Block(self.shape)

    def update(self):
        pass

    def draw(self):
        pass


class Tetris(Game):
    def __init__(self, *args, **kwargs):
        super(Tetris, self).__init__(*args, **kwargs)

        self.blocks = [

            Block([
                [0, 1, 0],
                [1, 1, 1]
            ]),

            Block([
                [1, 1],
                [1, 1]
            ]),

            Block([
                [1, 0],
                [1, 1],
                [0, 1]
            ]),

            Block([
                [0, 1],
                [1, 1],
                [1, 0]
            ]),

            Block([
                [1, 0],
                [1, 0],
                [1, 1]
            ]),

            Block([
                [0, 1],
                [0, 1],
                [1, 1]
            ]),

            Block([
                [1],
                [1],
                [1],
                [1]
            ])
        ]

        self.active_blocks = []

    def draw(self):
        self.frame[0: 20, 11] = theme["tetris_borders"]
        self.frame[0: 20, 23] = theme["tetris_borders"]



    def loop(self):
        self.draw()

        if self.is_key_up("B"):
            self.parent.back()
