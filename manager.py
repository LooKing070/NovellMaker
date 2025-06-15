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
        self.local_settings = self.open_settings()

        self.choose_scene()
        self.choose_volume(0)
        print(self.scenes)

    def open_login_save(self):
        with open(f"{self.dataPath}\\login.csv", "r", newline="", encoding="utf-8") as loginFile:
            playerLoginSave = csv.DictReader(loginFile, delimiter=';', quotechar='\n')
            for line in playerLoginSave:
                playerLoginSave = dict(line)
        return playerLoginSave

    def open_settings(self, edit: bool = False):
        if edit:
            with open(f"{self.dataPath}\\local_settings.csv", "w", newline="", encoding="utf-8") as settingsFile:
                pass
        else:
            with open(f"{self.dataPath}\\local_settings.csv", "r", newline="", encoding="utf-8") as settingsFile:
                settings = csv.DictReader(settingsFile, delimiter=';', quotechar='\n')
                for line in settings:
                    settings = dict(line)
                settings["volume"] = float(settings["volume"])
                settings["resolution"] = [int(i) for i in settings["resolution"].split()]
        return settings

    def check_click(self, pos, objects):
        for button in objects:
            clicks = button.check_click(pos)
            if clicks:  # проверка попадания по кнопке
                result = button.do()
                if type(result) == list:
                    for dr in result:
                        if dr in self.scenes:
                            self.choose_scene(dr)
                print(result)

    def choose_scene(self, scene="menu"):
        if not self.scenes[scene]:
            self.scenes[scene] = self.sceneCreator.load_scene(scene)
        self.scene = self.scenes[scene]
        for obj in self.scene.objects:
            if str(obj) == "Button":
                obj.do("on_start")

    def choose_resolution(self, screen, oldRes):
        self.screen = screen
        self.scene.screen = self.screen
        wPercent, hPercent = screen.get_width() / oldRes[0], screen.get_height() / oldRes[1]
        self.scene.fon.update((wPercent, hPercent))
        self.scene.objects.update((wPercent, hPercent))

    def choose_volume(self, percent: float):
        self.local_settings["volume"] += percent
        self.scene.music.set_volume(self.local_settings["volume"])
        """for obj in self.scene.objects:
            obj.sounds.set_volume(self.local_settings["volume"])"""
