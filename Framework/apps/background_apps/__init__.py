import numpy as np
from Framework.theme import theme
import time
import threading


class BackgroundApp(threading.Thread):
    def __init__(self, matrix, parent):
        super(BackgroundApp, self).__init__()
        self.daemon = True

        self.matrix = matrix
        self.parent = parent

        self.frame = np.zeros((20, 35, 3), np.uint8) + theme["background"]

        self.schedule_timestamp = 0
        self._schedule_function = None

        self.keys_down = self.matrix.get_keys()
        self.last_keys_down = self.keys_down

        self.loop_interval = 1

    def schedule_foreground(self, timedelta=0, timestamp=0):
        if self.schedule_timestamp == 0 and self._schedule_function is None:
            self._schedule(self.go_to_foreground, timedelta, timestamp)
        else:
            pass

    def schedule_background(self, timedelta=0, timestamp=0):
        if self.schedule_timestamp == 0 and self._schedule_function is None:
            self._schedule(self.go_to_background, timedelta, timestamp)
        else:
            pass

    def _schedule(self, function, timedelta=0, timestamp=0):
        if (timedelta > 0) ^ (timestamp > 0):  # Check if one of them is > 0 via xor

            if timestamp:
                if timestamp > time.time():
                    self._schedule_function = function
                    self.schedule_timestamp = timestamp
                else:
                    function()
            else:
                if timedelta > 0:
                    self._schedule_function = function
                    self.schedule_timestamp = time.time() + timedelta
                else:
                    function()

        else:
            if timestamp + timedelta > 0:
                raise ValueError("The use of timedelta and timestamp cannot be combined")
            else:
                raise ValueError("No time argument given")

    def go_to_foreground(self):
        self.parent.enable_background_app(self)

    def go_to_background(self):
        self.parent.disable_background_app()

    def set_loop_interval(self, interval):
        self.loop_interval = interval

    def loop(self):
        pass

    def clear(self):
        self.frame = np.zeros((20, 35, 3), np.uint8) + theme["background"]

    def is_key_down(self, key):
        return self.keys_down[key] and not self.last_keys_down[key]

    def is_key_pressed(self, key):
        return self.keys_down[key]

    def is_key_up(self, key):
        return self.last_keys_down[key] and not self.keys_down[key]

    def update(self, keys_down):
        self.last_keys_down = self.keys_down
        self.keys_down = keys_down

    def run(self):
        while True:
            self.loop()
            if time.time() >= self.schedule_timestamp and self._schedule_function is not None:
                self._schedule_function()
                self.schedule_timestamp = 0
                self._schedule_function = None
            time.sleep(self.loop_interval)

    def get_frame(self):
        return self.frame
