import numpy as np
import telegram
from telegram.error import NetworkError, Unauthorized
import threading
import subprocess
from PIL import Image
import time
import os

from Framework.font import render_text
from Framework.apps.background_apps import BackgroundApp


class TelegramBotThread(threading.Thread):
    def __init__(self, parent):
        super(TelegramBotThread, self).__init__()
        self.daemon = True

        self.parent = parent

        # TODO: Generate new bot and don't push keys to github :)
        self.bot = telegram.Bot('357068228:AAHZmriAYgH1ywcFX4JOuOEp5t7BZFFzZ1U')
        # self.bot = telegram.Bot('453991406:AAG_pYzmFSQT4gYnAcI4GNECMGXd0ZXlyYo')  # Backup
        try:
            self.update_id = self.bot.get_updates()[0].update_id
        except IndexError:
            self.update_id = None

    def echo(self):
        for update in self.bot.get_updates(offset=self.update_id, timeout=10):
            self.update_id = update.update_id + 1
            if update.message:
                if len(update.message.photo) > 0:
                    self.parent.new_photo = True
                    photo_file = self.bot.get_file(update.message.photo[-1].file_id)
                    self.parent.photo = photo_file["file_path"]
                else:
                    self.parent.new_text = True
                    if not update.message.text is None:
                        self.parent.text = update.message.text.strip()

    def run(self):
        while 1:
            try:
                self.echo()
            except NetworkError:
                time.sleep(1)
            except Unauthorized:
                self.update_id += 1


class Telegram(BackgroundApp):
    def __init__(self, matrix, parent):
        super(Telegram, self).__init__(matrix, parent)

        self.last_text = self.text = ""
        self.new_text = self.new_photo = False
        self.photo = ""
        self.show_mode = "text"
        self.actual_render = self.frame
        self.shift = 0
        self.imshowframe = np.zeros((20, 35, 3), np.uint8)

        self.bot = TelegramBotThread(self)
        self.bot.start()

        self.set_loop_interval(1)  # Sleep 1 second after update

    def loop(self):

        if self.last_keys_down["B"] and not self.keys_down["B"]: self.parent.back()

        if len(self.text) > 0:
            self.frame = np.zeros((20, 35, 3), np.uint8)

            if self.new_text:
                if len(self.text) >= 9:
                    self.text += "  --  "
                self.actual_render = np.zeros((20, 4 * len(self.text), 3), np.uint8)
                render_text(self.actual_render, (255, 255, 255), (0, 0, 0), self.text, 1, 8)
                self.new_text = False
                self.show_mode = "text"
                self.go_to_foreground()
                self.schedule_background(timedelta=10)
            elif self.new_photo:
                self.new_photo = False
                self.show_mode = "photo"
                ext = self.photo.split(".")[-1]
                with open(os.devnull, 'w') as devnull:
                    if subprocess.call(["wget", "-O", "/tmp/image.%s" % ext, self.photo], stdout=devnull) == 0:
                        im = Image.open("/tmp/image.%s" % ext)
                        im.thumbnail((35, 20), Image.ANTIALIAS)
                        data = list(im.getdata())
                        width, height = im.size
                        tmp = np.zeros((height, width, 3))
                        i = 0
                        for y in range(0, height):
                            for x in range(0, width):
                                tmp[y, x] = data[i]
                                i += 1
                        self.imshowframe = np.zeros((20, 35, 3), dtype=np.uint8)
                        x = (35 / 2) - (width / 2)
                        y = (20 / 2) - (height / 2)
                        self.imshowframe[y:y + height, x:x + width] = np.uint8(tmp)
                        subprocess.call(["rm", "/tmp/image.%s" % ext])  # remove image to free storage
                    else:
                        self.show_mode = ""
                        self.text = "Failed to show image"
                        self.new_text = True

            if self.show_mode == "text":
                if self.actual_render.shape[1] <= 35:
                    x = (35 / 2) - (self.actual_render.shape[1] / 2)
                    self.frame[0:20, x:x + self.actual_render.shape[1]] = self.actual_render
                else:
                    self.frame = np.zeros((20, 35, 3), np.uint8)
                    self.frame[0:20, 0:35] = self.actual_render[0:20, 0:35]
                    self.actual_render = np.roll(self.actual_render, -1, 1)
                    time.sleep(0.1)

            if self.show_mode == "photo":
                self.frame = np.zeros((20, 35, 3), np.uint8)
                self.frame = np.array(self.imshowframe)
                time.sleep(0.1)
