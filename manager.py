import os
import pygame
import csv
import json
from scener import SceneCreator


class Manager(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, screen):
        self.screen = screen

        self.dataPath = os.path.abspath("p_data")
        self.scenePath = os.path.abspath("scenes")

        self.sceneCreator = SceneCreator(self.screen, self.scenePath)

        self.scenes = {k: None for k in os.listdir(self.scenePath)}
        self.scene = None
        self.save = self.open_login_save()
        self.localSettings = self.open_settings()
        self.interactionMB = self.localSettings["interactionMB"]

        self.choose_scene()
        self.choose_volume(0)
        print(self.scenes)

    def open_login_save(self):
        with open(f"{self.dataPath}\\login.csv", "r", newline="", encoding="utf-8") as loginFile:
            playerLoginSave = csv.DictReader(loginFile, delimiter=',', quotechar='\n')
            for line in playerLoginSave:
                playerLoginSave = dict(line)
        return {k: v.split() if ' ' in v else v for k, v in playerLoginSave.items()}

    def open_settings(self):
        with open(f"{self.dataPath}\\local_settings.csv", "r", newline="", encoding="utf-8") as settingsFile:
            settings = csv.DictReader(settingsFile, delimiter=',', quotechar='\n')
            for line in settings:
                settings = dict(line)
            settings["volume"] = float(settings["volume"])
            settings["resolution"] = [int(i) for i in settings["resolution"].split()]
            settings["interactionMB"] = [int(i) for i in settings["interactionMB"].split()]
        return settings

    def save_settings(self):
        with open(f"{self.dataPath}\\local_settings.csv", "w", newline="", encoding="utf-8") as settingsFile:
            writer = csv.DictWriter(settingsFile, list(self.localSettings.keys()))
            saveSettings = {k: ' '.join([str(i) for i in v]) if type(v) == list else str(v)
                            for k, v in self.localSettings.items()}
            writer.writeheader()
            writer.writerow(saveSettings)

    def check_click(self, pos, objects):
        for button in objects.values():
            clicks = button.check_click(pos)
            if clicks:  # проверка попадания по кнопке
                self.do(button.do())

    def do(self, result):
        if '&' in result:
            if "tr&" == result[:3]:
                self.scene.objects[result[3:]].transparency = 1
            elif "sa&" == result[:3]:
                pass
            elif "lo&" == result[:3]:
                self.choose_scene(result[3:])
        else:
            for r in result:
                self.do(r)
        pass

    def choose_scene(self, scene="menu"):
        if self.scene:
            self.scene.music.stop()
        if not self.scenes[scene]:
            self.scenes[scene] = self.sceneCreator.load_scene(scene)
        self.scene = self.scenes[scene]
        self.scene.music.play(-1)

    def choose_resolution(self, screen, oldRes):
        self.screen = screen
        self.scene.screen = self.screen
        screenW, screenH = screen.get_width(), screen.get_height()
        wPercent, hPercent = screenW / oldRes[0], screenH / oldRes[1]
        self.localSettings["resolution"] = [screenW, screenH]
        self.scene.fon.update((wPercent, hPercent))
        for obj in self.scene.objects.values():
            obj.update((wPercent, hPercent))

    def choose_volume(self, percent: float):
        if 0 <= self.localSettings["volume"] + percent <= 1:
            self.localSettings["volume"] += percent
        elif self.localSettings["volume"] + percent >= 1:
            self.localSettings["volume"] = 1
        else:
            self.localSettings["volume"] = 0
        self.scene.music.set_volume(self.localSettings["volume"])
        """for obj in self.scene.objects:
            obj.sounds.set_volume(self.local_settings["volume"])"""
