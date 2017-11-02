import numpy as np
import time
from theme import theme
from font import render_text
import matrix as mx


class Settings(object):
    def __init__(self, matrix, parent):
        self.matrix = matrix
        self.parent = parent

        self.frame = np.zeros((20, 35, 3), np.uint8)

        self.keys_down = self.matrix.get_keys()
        self.last_keys_down = self.keys_down

        self.options = {
            "Invert": self.matrix.do_invert,
            "Flip": self.matrix.do_flip,
            "Joyst.": self.matrix.change_to_joystick,
            "Keyb.": self.matrix.change_to_keyboard
        }

        if type(self.matrix) == mx.MatrixSimulator:
            self.options.update({"Mode": self.matrix.do_mode_change})
            self.options.update({"Fullscr.": self.matrix.do_fullscreen_change})

        self.keys = self.options.keys()
        self.index = 0

    def activation(self):
        pass

    def self_update(self, keys_down):
        self.last_keys_down = self.keys_down
        self.keys_down = keys_down

        self.frame = np.zeros((20, 35, 3), np.uint8) + theme["background"]
        render_text(self.get_frame(), theme["header"], theme["background"], "Settings", 0, 0)
        render_text(self.get_frame(), theme["text"], theme["background"], self.keys[self.index], 2, 8)
        a = "<"
        b = ">"
        if self.index == 0:
            a = " "
        if self.index == len(self.keys) - 1:
            b = " "
        render_text(self.frame, theme["elements"], theme["background"], "%s      %s" % (a, b), 2, 14)

        if self.keys_down["LEFT"] and not self.last_keys_down["LEFT"]:
            if self.index > 0:
                self.index -= 1

        if self.keys_down["RIGHT"] and not self.last_keys_down["RIGHT"]:
            if self.index < len(self.keys) - 1:
                self.index += 1

        if self.keys_down["A"] and not self.last_keys_down["A"]:
            self.options[self.keys[self.index]]()

        if self.keys_down["B"] and not self.last_keys_down["B"]:
            self.parent.back()

        time.sleep(0.03)

    def get_frame(self):
        return self.frame
