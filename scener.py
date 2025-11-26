import os
import pygame
import json
from rendering import Rendering
from sounder import Sounder


class Scene:
    def __str__(self):
        return self.sceneName

    def __init__(self, sceneName, screen, fon, music, objects, script: list):
        self.sceneName = sceneName
        self.screen = screen
        self.screenSize = self.screen.get_width(), self.screen.get_height()
        self.fon = fon
        self.music = music
        self.script = script  # [[obj, event], [obj, event], ]
        self.action = 0
        self.objects = {}
        for obj in objects:
            self.objects[obj.tName] = obj
        self.result = "PAUSED"

    def show(self):  # Возвращает ЛОЖЬ для продолжения игры
        self.fon.update()
        self.screen.blit(self.fon.image, (0, 0))
        for obj in self.objects.values():
            if obj.transparency:
                self.screen.blit(obj.image, obj.rect.topleft)
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
        fon = None
        music = None
        objects = []
        script = []
        sceneType = ''
        path = f"{self.path}\\{sceneName}"
        with open(f"{path}\\parameters.json", 'r', encoding="utf-8") as par_file:
            for key, value in json.load(par_file).items():
                if key == "scene_type":
                    sceneType = value
                elif key == "fon":
                    value[0] = f"\\bg\\{value[0]}"
                    value += [False, 1, 1, 1, self.screen.get_width()]
                    fon = self.render.load_fon(*value)
                elif key == "music":
                    music = self.sounder.load_fon_music(value)
                else:
                   objects = self._load_objects(path, value)
        with open(f"{path}\\script.txt", 'r', encoding="utf-8") as scr_file:
            s = [el.rstrip('\n') for el in scr_file.readlines() if el]
            action = []
            for i in range(len(s)):
                match s[i].split():
                    case [name, '-', '$']:
                        action.append([name, '$'])
                    case [name, '-', '&']:
                        action.append([name, '&'])
                    case [name, '-', event] if not action:
                        script.append([name, event])
                    case [score, '-', event] if action[0][1] == '$':
                        action.append([int(score), event])
                    case [myEvent, name, '-', event] if action[0][1] == '&':
                        action.append([myEvent, name, event])
                    case ['$'] | ['&']:
                        script.append(action)
                        action = []
                    case other:
                        print(other)
        return self.scenes[sceneType](sceneName, self.screen, fon, music, objects, script)

    def _load_objects(self, path: str, objects: list):  # Загрузка объектов (кнопок) в этой сцене
        newObjects = []
        for currentDir, objectType in objects:
            events, parameters, speech = {}, {}, {}
            for f in os.listdir(f"{path}\\{currentDir}"):
                if ".json" in f:
                    with open(f"{path}\\{currentDir}\\{f}", 'r', encoding="utf-8") as file:
                        if "events" in f:
                            events = {k: v for k, v in json.load(file).items()}
                        elif "parameters" in f:
                            parameters = {k: v for k, v in json.load(file).items()}
                            parameters["type"] = currentDir
                            parameters["texture"][0] = self.render.set_texture(*parameters["texture"][0].split('+'))
                            for i in range(len(parameters["sounds"])):
                                parameters["sounds"][i] = self.sounder.load_sound(parameters["sounds"][i])
                elif ".txt" in f[-4:]:
                    with open(f"{path}\\{currentDir}\\{f}", 'r', encoding="UTF8") as text:
                        for string in text.readlines():
                            string = string.rstrip()
                            if string[-1] == string[0] == '&':
                                title = string[1:-1]
                                speech[title] = []
                            else:
                                speech[title].append(string)
            newObjects.append(self.render.buttonsCreator.create_button(objectType, parameters, events, speech))
        return newObjects
