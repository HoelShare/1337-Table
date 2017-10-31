import time
import numpy as np
from Framework.font import render_text
from Framework.theme import theme
from Framework.apps.ambient import Ambient


class Clock(Ambient):
    def loop(self):
        t = time.localtime()
        text = "%02d:%02d" % (t.tm_hour, t.tm_min)

        self.frame = np.zeros((20, 35, 3), np.uint8) + theme["clock_background"]
        x = (35 / 2) - ((len(text) * 4) / 2)
        render_text(self.frame, theme["clock_color"], theme["clock_background"], text, x, 14)

        tmp = np.zeros((5, 4 * len(text), 3))
        render_text(tmp, theme["clock_color"], theme["clock_background"], text, 0, 0)
        tmp = np.rot90(tmp, 2)
        self.frame[1:6, x:x + (4 * len(text))] = tmp

        for i in range(0, 35):
            self.frame[9, i] = theme["clock_spacer"]
            self.frame[10, i] = theme["clock_spacer"]

        if self.last_keys_down["B"] and not self.keys_down["B"]: self.parent.back()
