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
        self.choose_scene()
        print(self.scenes)

    @staticmethod
    def open_logins_params(path):
        playerLogin = {}
        with open(path, "r", newline="", encoding="utf-8") as loginFile:
            reader = csv.reader(loginFile, delimiter=';', quotechar='\n')
            readed = []
            for index, row in enumerate(reader):
                if index > 0:
                    for p in range(len(row)):
                        row[p] = [i.strip('"') for i in row[p].split()]
                readed.append(row)
            for column in range(len(readed[0])):
                for login in range(1, len(readed)):
                    key = readed[0][column]
                    if key in playerLogin:
                        if len(readed[login][column]) > 1:
                            playerLogin[key] += [readed[login][column]]
                        else:
                            playerLogin[key] += readed[login][column]
                    else:
                        if len(readed[login][column]) > 1:
                            playerLogin[key] = [readed[login][column]]
                        else:
                            playerLogin[key] = readed[login][column]
        return playerLogin

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
        return

