import numpy as np
import time
from font import render_text
from theme import theme

from settings import Settings
from game_handler import GameHandler
from ambient_handler import AmbientHandler
from Framework.apps.background_apps import conf as background_apps_conf


class Menu(object):
    def __init__(self, matrix):
        self.matrix = matrix

        self.frame = np.zeros((20, 35, 3), np.uint8)

        self.points = {
            "Settings": Settings(self.matrix, self),
            "Games": GameHandler(self.matrix, self),
            "Ambient": AmbientHandler(self.matrix, self)
        }

        self.background_app_labels = background_apps_conf.background_apps
        self.background_apps = []
        for app_label in self.background_app_labels:
            app = app_label(self.matrix, self)
            app.start()
            self.background_apps.append(app)

        self.background = False
        self.active_background_app = None

        self.keys = self.points.keys()
        self.index = 0
        self.active = self

        self.keys_down = self.matrix.get_keys()
        self.last_keys_down = self.keys_down

        self.active_paused = False

        self.back_time = time.time()
        self.standby_timeout = 20

    def back(self):
        self.active = self
        self.back_time = time.time()

    def standby(self):
        self.active = self.points["Ambient"]
        time.sleep(0.1)
        self.active.standby()

    def enable_background_app(self, app):
        self.background = True
        self.active_background_app = app
        self.active_paused = True

    def disable_background_app(self):
        if self.background:
            self.active_paused = False
            self.background = False
            self.active_background_app = None

    def self_update(self, keys_down):
        self.last_keys_down = self.keys_down
        self.keys_down = keys_down

        self.frame = np.zeros((20, 35, 3), np.uint8) + theme["background"]
        render_text(self.get_frame(), theme["header"], theme["background"], "1337Table", 0, 0)
        render_text(self.get_frame(), theme["text"], theme["background"], self.keys[self.index], 2, 8)
        a = "<"
        b = ">"
        if self.index == 0:
            a = " "
        if self.index == len(self.keys) - 1:
            b = " "
        render_text(self.frame, theme["elements"], theme["background"], "%s      %s" % (a, b), 2, 14)

        if self.keys_down["LEFT"] and not self.last_keys_down["LEFT"]:
            self.back_time = time.time()
            if self.index > 0:
                self.index -= 1

        if self.keys_down["RIGHT"] and not self.last_keys_down["RIGHT"]:
            self.back_time = time.time()
            if self.index < len(self.keys) - 1:
                self.index += 1

        if self.last_keys_down["A"] and not self.keys_down["A"]:
            self.active = self.points[self.keys[self.index]]
            self.active.activation()
            time.sleep(0.1)

        if time.time() - self.back_time > self.standby_timeout:
            self.standby()
        else:
            tleft = time.time() - self.back_time
            if tleft > 0:
                tleft /= float(self.standby_timeout)
                r = int(tleft * 255)
                g = 255 - r
                b = 0
                self.frame[18, 1] = (r, g, b)


        time.sleep(0.05)

    def get_frame(self):
        return self.frame

    def draw(self):
        if not self.background:
            self.matrix.set_frame(self.active.get_frame())
        else:
            self.matrix.set_frame(self.active_background_app.get_frame())
        # time.sleep(0.05)

    def update(self, keys_down):
        if not self.active_paused:
            self.active.self_update(keys_down)
        elif self.active_background_app is not None and self.background:
            self.active_background_app.update(keys_down)

