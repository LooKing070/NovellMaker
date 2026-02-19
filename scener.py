import os
import pygame
import json
from rendering import Rendering
from objects import ObjectsCreator
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
        self.script = script  # [[obj, [event]], [obj, [event]], ]
        self.action = 0
        self.q = []  # очередь из ивентов
        self.objects = {}
        for obj in objects:
            self.objects[obj.tName] = obj
        self.result = "PAUSED"

    def continue_script(self):
        result = ''
        if len(self.script) > self.action:
            obj, event = self.script[self.action]
            if type(event) == str:
                result = self.objects[obj].do(event)
            elif event[0] == '$':  # блок с выбором действия персонажем
                for pScore in range(1, len(event), 2):
                    if pScore <= self.objects[obj].plotScore:
                        result = self.objects[obj].do(event[pScore + 1])
                        break
            elif event[0] == '&':  # хз
                pass
            print(result)
            self.action += 1
        else: print("THE ACTION ENDED IN THE SCENE")
        return result

    def show(self):  # Возвращает текущие действия
        self.fon.draw(self.screen)
        for obj in self.objects.values():
            if obj.image.get_alpha():
                obj.draw(self.screen)
                obj.do_anim()
                if obj.runAnim:
                    if obj.tName not in self.q:
                        self.q.append(obj.tName)
                elif obj.tName in self.q:
                    self.q.remove(obj.tName)
        # print(self.q)
        return self.q


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
        self.objectsCreator = ObjectsCreator()
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
                    if len(value) == 1: value += [255, 1, 1, 1, self.screen.get_width()]
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
                        action = [name, ['$']]
                    case [name, '-', '&']:
                        action = [name, ['&']]
                    case [name, '-', event] if not action:
                        script.append([name, event])
                    case [score, '-', event] if action[1][0] == '$':
                        action[1] += [int(score), event]
                    case [myEvent, name, '-', event] if action[1][0] == '&':
                        action[1] += [myEvent, name, event]
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
                            sounds = {}
                            for i in range(len(parameters["sounds"])):
                                sounds[parameters["sounds"][i][:-4]] = self.sounder.load_sound(parameters["sounds"][i])
                            parameters["sounds"] = sounds
                elif ".txt" in f[-4:]:
                    with open(f"{path}\\{currentDir}\\{f}", 'r', encoding="UTF8") as text:
                        for string in text.readlines():
                            string = string.rstrip()
                            if string[-1] == string[0] == '&':
                                title = string[1:-1]
                                speech[title] = []
                            else:
                                speech[title].append(string)
            newObjects.append(self.objectsCreator.create(objectType, parameters, events, speech))
        return newObjects
