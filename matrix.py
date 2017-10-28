import numpy as np
import socket
import time


class MatrixSimulator(object):
    def __init__(self):
        # TODO: Is this good practise?
        import pygame
        self.pygame = pygame
        self.pygame.init()

        self.width = 35
        self.height = 20
        self.colors = 3

        self.flip = True
        self.invert = False

        self.frame = np.array((self.height, self.width, self.colors))

        self.px_size = 20

        self.display = self.pygame.display.set_mode((self.width * self.px_size, self.height * self.px_size))

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect(("tisch.warpzone", 4321))

        self.joystick = self.pygame.joystick.Joystick(0)
        self.joystick.init()

    def generate_dgram_from_frame(self, frame):
        dgram = ""

        for x in range(0, 35):
            for y in range(0, 20) if x % 2 == 0 else range(0, 20)[::-1]:
                dgram += "%c%c%c" % tuple(frame[y, x])
        self.sock.send(dgram)

    def do_flip(self):
        self.flip = not self.flip

    def do_invert(self):
        self.invert = not self.invert

    def set_frame(self, frame):
        f_height, f_width, f_colors = frame.shape
        if f_height != self.height or f_width != self.width or f_colors != self.colors:
            raise IndexError("Shape (%d %d %d) does not fit into (%d %d %d)!" % (
                f_height, f_width, f_colors, self.height, self.width, self.colors))
        if self.invert:
            frame = 255 - frame
        for x in range(0, self.width):
            for y in range(0, self.height):
                color = tuple(map(int, frame[y, x]))
                self.pygame.draw.rect(self.display, color,
                                      (x * self.px_size, y * self.px_size, self.px_size, self.px_size))

        if self.flip:
            frame = np.rot90(frame, 2)
            frame = np.fliplr(frame)
        else:
            frame = np.fliplr(frame)
        self.generate_dgram_from_frame(frame)
        self.pygame.display.flip()

    def get_keys(self):
        out = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        it = 0
        self.pygame.event.pump()

        # Read input from the two joysticks
        for i in range(0, self.joystick.get_numaxes()):
            out[it] = self.joystick.get_axis(i)
            it += 1
        # Read input from buttons
        for i in range(0, self.joystick.get_numbuttons()):
            out[it] = self.joystick.get_button(i)
            it += 1

        keys_d = {
            "UP": out[1] < 0,
            "DOWN": out[1] > 0,
            "LEFT": out[0] < 0,
            "RIGHT": out[0] > 0,
            "A": out[3],
            "B": out[4],
            "X": out[5],
            "Y": out[2],
            "START": out[11],
            "SELECT": out[10],
        }

        return keys_d


if __name__ == "__main__":
    m = MatrixSimulator()
    while 1:
        n = np.uint8(np.random.rand(20, 35, 3) * 255)
        m.set_frame(n)