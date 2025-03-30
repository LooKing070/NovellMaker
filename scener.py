import os
import pygame
import json
from rendering import Rendering
from sounder import Sounder


class Scene:
    def __str__(self):
        return self.sceneName

    def __init__(self, sceneName, screen, fon, music, objects):
        self.sceneName = sceneName
        self.screen = screen
        self.screenSize = self.screen.get_width(), self.screen.get_height()
        self._fon = fon
        self._music = music
        self.objects = pygame.sprite.Group()
        for obj in objects:
            self.objects.add(obj)
        self.result = "PAUSED"

        self._music.play(-1)

    def show(self):  # Возвращает ЛОЖЬ для продолжения игры
        self.objects.draw(self.screen)
        return False


class Camera(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, screenSize):
        self.width, self.height = screenSize
        self.speed = 0
        self.moving = False
        self.direction = [0, 0]

    def move_obj(self, objectGroup):
        if self.moving:
            if objectGroup.sprites():
                objectGroup.update((-self.direction[0], -self.direction[1]), self.speed / 2)

    def move_target(self, target):
        if self.moving:
            if target.update(self.direction, 0.0001):
                self.speed = target.speed
            else:
                self.speed = 0


class SceneCreator(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, screen, scenePath: str):
        self.path = scenePath
        self.screen = screen
        self.render = Rendering()
        self.sounder = Sounder()
        self.scenes = {"baseScene": Scene}

    def load_scene(self, sceneName: str = "menu"):
        fon = pygame.sprite.Sprite()
        fon.rect = self.screen.get_width(), self.screen.get_height()
        music = None
        objects = []
        sceneType = ''
        path = f"{self.path}\\{sceneName}"
        with open(f"{path}\\parameters.json") as par_file:
            for key, value in json.load(par_file).items():
                if key == "scene_type":
                    sceneType = value
                elif key == "fon":
                    fon.image = self.render.set_texture(f"\\bg\\{value}")
                elif key == "music":
                    music = self.sounder.load_fon_music(value)
                else:
                   objects = self._load_objects(path, value)
        return self.scenes[sceneType](sceneName, self.screen, fon, music, objects)

    def _load_objects(self, path: str, objects: list):  # Загрузка объектов (кнопок) в этой сцене
        newObjects = []
        for currentDir, objectType, position, animaParameters in objects:
            events, parameters, speech = {}, {}, {}
            for f in os.listdir(f"{path}\\{currentDir}"):
                if ".json" in f:
                    with open(f"{path}\\{currentDir}\\{f}", 'r', encoding="utf-8") as file:
                        if "events" in f:
                            events = {k: v for k, v in json.load(file).items()}
                        elif "parameters" in f:
                            parameters = {k: v for k, v in json.load(file).items()}
                elif ".txt" in f[-4:]:
                    with open(f"{path}\\{currentDir}\\{f}", 'r', encoding="UTF8") as text:
                        for string in text.readlines():
                            string = string.rstrip()
                            if string[-1] == string[0] == '&':
                                title = string[1:-1]
                                speech[title] = []
                            else:
                                speech[title].append(string)
            objects.append(self.render.buttonsCreator.create_button(self.render.set_texture(parameters["texture"]),
                                                                    parameters["sounds"], objectType, tuple(position),
                                                                    (*animaParameters, parameters["name"],
                                                                     parameters["speech"], events, speech)))
        return newObjects
