#!/usr/bin/env python2.7
from Framework.apps.ambient import Ambient

from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
import colorsys, random
import math
import numpy as np


class Receiver(Thread):
    def __init__(self, sock):
        super(Receiver, self).__init__()
        self.daemon = True

        self.sock = sock
        self.pack = " " * 1024

    def run(self):
        while 1:
            self.pack = self.sock.recv(1024)


class Audio(Ambient):
    def __init__(self, matrix, parent):
        super(Audio, self).__init__(matrix, parent)

        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", 7777))

        self.receiver = Receiver(self.sock)
        self.receiver.start()

        self.colors = np.uint8(np.random.rand(20, 35, 3) * 255)

        self.am = self.prev_am = 0
        self.x, self.y = 17, 10

    def loop(self):
        self.clear()

        pack = self.receiver.pack
        vals = np.array(map(ord, pack))
        self.prev_am = self.am
        self.am = np.argmax(vals)
        v = vals[self.am] / 255.
        r = v * 15
        if abs(self.am - self.prev_am) > 25:
            self.y = random.randint(0, 19)
            self.x = random.randint(0, 34)
        cr, cg, cb = self.colors[self.y, self.x]

        for n in range(1, int(r)+1):
            for i in range(0, 100):
                s = math.sin((i / 100.) * (2 * math.pi)) * n
                c = math.cos((i / 100.) * (2 * math.pi)) * n
                dy, dx = int(self.y + s), int(self.x + c)
                if dy >= 0 and dy < 20 and dx >= 0 and dx < 35:
                    self.frame[dy, dx] = np.uint8(np.array((cr, cg, cb)) * float(n / r))

        if self.is_key_up("B"):
            self.parent.back()
