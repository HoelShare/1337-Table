import numpy as np
import random
from Framework.theme import theme
import time
from Framework.font import render_text
from Framework.apps.games import Game
from Framework import defaults
import os
import json


class Snake(Game):
    def __init__(self, matrix, parent):
        super(Snake, self).__init__(matrix, parent)

        self.particle = [random.randint(0, 34), random.randint(0, 19)]
        self.snake = [[random.randint(0, 34), random.randint(0, 19)]]
        self.direction = [1, 0]
        self.speed = 1
        random.shuffle(self.direction)
        self.length = 3
        self.ingame = False
        self.firstrun = True
        self.menu_point = "top"
        self.score_board_selection = False
        self.scoreboard_text = ["_" for _ in range(0, 7)]
        self.scoreboard_text_sel = 0
        self.firstmen = True

        self.default_scoreboard = {

        }

        self.scoreboard_alphabet = ["_", " "]
        for a in range(0, 26):
            self.scoreboard_alphabet.append(chr(a + 65))
        for i in range(0, 10):
            self.scoreboard_alphabet.append(str(i))

    def loop(self):
        if self.ingame:
            if self.is_key_down("LEFT"):
                if not self.direction[0] == 1:
                    self.direction = [-1, 0]
            if self.is_key_down("RIGHT"):
                if not self.direction[0] == -1:
                    self.direction = [1, 0]
            if self.is_key_down("UP"):
                if not self.direction[1] == 1:
                    self.direction = [0, -1]
            if self.is_key_down("DOWN"):
                if not self.direction[1] == -1:
                    self.direction = [0, 1]

            if self.is_key_down("B"):
                self.ingame = False
                self.firstrun = False
                self.firstmen = True

            self.frame = np.zeros((20, 35, 3), np.uint8) + theme["snake_background"]
            particle_x, particle_y = self.particle
            self.frame[particle_y, particle_x] = theme["snake_food"]

            newpoint = list(self.snake[-1])
            newpoint[0] = (newpoint[0] + int(self.direction[0] * self.speed)) % 35
            newpoint[1] = (newpoint[1] + int(self.direction[1] * self.speed)) % 20
            self.snake.append(newpoint)

            if newpoint in self.snake[:-1]:
                self.ingame = False
                self.firstrun = False

            if newpoint[0] == self.particle[0] and newpoint[1] == self.particle[1]:
                self.length += 1
                self.particle = [random.randint(0, 34), random.randint(0, 19)]

            if len(self.snake) > self.length:
                self.snake.pop(0)

            time.sleep(0.03)
            n = 1
            for point in self.snake:
                point_x, point_y = point
                self.frame[point_y, point_x] = np.uint8(np.array(theme["snake_snake"]) * (n / float(self.length)))
                n += 1
        else:
            render_text(self.get_self_frame(), theme["header"], theme["snake_background"], "Snake", 0, 0)
            if self.menu_point == "top":
                if self.firstrun and self.firstmen:
                    render_text(self.get_self_frame(), theme["snake_welcome"], theme["snake_background"], "Welcome", 2,
                                8)
                elif self.firstmen:
                    self.menu_point = "lose_screen"
                    self.firstmen = False
                    render_text(self.get_self_frame(), theme["snake_lose"], theme["snake_background"], "You lose", 2, 7)
                else:
                    render_text(self.get_self_frame(), theme["snake_lose"], theme["snake_background"], "You lose", 2, 7)

                if self.keys_down["A"] and not self.last_keys_down["A"]:
                    self.particle = [random.randint(0, 34), random.randint(0, 19)]
                    self.snake = [[random.randint(0, 34), random.randint(0, 19)]]
                    self.direction = [1, 0]
                    random.shuffle(self.direction)
                    self.length = 3
                    self.ingame = True
                    self.firstmen = True
                    self.menu_point = "top"

                if self.last_keys_down["B"] and not self.keys_down["B"]:
                    self.parent.back()
            if self.menu_point == "lose_screen":

                render_text(self.get_self_frame(), theme["snake_lose"], theme["snake_background"], "You lose", 2, 7)

                if self.score_board_selection:
                    render_text(self.get_self_frame(), theme["yes"], theme["snake_background"], "Y", 6, 14)
                    render_text(self.get_self_frame(), theme["out_grayed"], theme["snake_background"], "X", 26, 14)
                else:
                    render_text(self.get_self_frame(), theme["out_grayed"], theme["snake_background"], "Y", 6, 14)
                    render_text(self.get_self_frame(), theme["no"], theme["snake_background"], "X", 26, 14)

                if self.is_key_up("A"):
                    if self.score_board_selection:
                        self.frame = np.zeros(self.frame.shape)
                        self.menu_point = "scoreboard_enter"
                    else:
                        self.menu_point = "top"
                        self.firstmen = False
                        self.clear()
                if self.is_key_down("RIGHT"):
                    self.score_board_selection = False
                if self.is_key_down("LEFT"):
                    self.score_board_selection = True

            if self.menu_point == "scoreboard_enter":
                self.clear()
                render_text(self.get_self_frame(), theme["header"], theme["snake_background"], "Score", 0, 0)
                scoreboard_text = ''.join(self.scoreboard_text)
                render_text(self.get_self_frame(), theme["no"], theme["snake_background"], scoreboard_text, 4, 10)

                x = self.scoreboard_text_sel * 4 + 5
                self.frame[8, x] = theme["elements"]

                if self.is_key_down("RIGHT"):
                    self.scoreboard_text_sel = (self.scoreboard_text_sel + 1) % 7
                if self.is_key_down("LEFT"):
                    self.scoreboard_text_sel = (self.scoreboard_text_sel - 1) % 7
                if self.is_key_down("UP"):
                    current = self.scoreboard_text[self.scoreboard_text_sel]
                    ind = self.scoreboard_alphabet.index(current)
                    new_ind = (ind + 1) % len(self.scoreboard_alphabet)
                    new = self.scoreboard_alphabet[new_ind]
                    self.scoreboard_text[self.scoreboard_text_sel] = new
                if self.is_key_down("DOWN"):
                    current = self.scoreboard_text[self.scoreboard_text_sel]
                    ind = self.scoreboard_alphabet.index(current)
                    new_ind = (ind - 1) % len(self.scoreboard_alphabet)
                    new = self.scoreboard_alphabet[new_ind]
                    self.scoreboard_text[self.scoreboard_text_sel] = new

                if self.is_key_down("A"):
                    path = defaults.get_data_directory("snake") + "scoreboard.json"
                    if not os.path.exists(path):
                        with open(path, "a+") as target:
                            json.dump(self.default_scoreboard, target)
                    else:
                        db_scoreboard = self.default_scoreboard
                        with open(path) as target:
                            db_scoreboard = json.load(target)
                        db_scoreboard.update({
                            ''.join(self.scoreboard_text):
                                [self.length, int(time.time())]
                        })
                        with open(path, 'w+') as target:
                            json.dump(db_scoreboard, target)
                    self.menu_point = "top"
                    self.clear()