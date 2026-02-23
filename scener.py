import os
import json
import pygame
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
            if obj in self.objects:
                if type(event) == str:
                    result = self.objects[obj].do(event)
                elif event[0] == '$':  # блок с выбором действия персонажем
                    for i in range(1, len(event), 2):
                        if event[i] <= self.objects[obj].plotScore:
                            result = self.objects[obj].do(event[i + 1])
                            break
                print(result)
                self.action += 1
            elif event[0] == '&':  # хз
                for i in range(1, len(event), 2):
                    result = self.objects[event[i]].do(event[i + 1])
                self.action += 1
                print(result)
            else: print(f"ERROR: OBJECT '{obj}' NOT FOUND. ERROR BLOCK - {self.action + 1}")
        else: print("THE ACTION ENDED IN THE SCENE")
        return result

    def show(self):  # Возвращает текущие действия
        self.fon.draw(self.screen)
        for obj in self.objects.values():
            if obj.transparency:
                obj.draw(self.screen)
                obj.do_anim()
            if obj.runAnim:
                if obj.tName not in self.q:
                    self.q.append(obj.tName)
            elif obj.tName in self.q:
                self.q.remove(obj.tName)
        if self.q:
            print(self.q)
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
                    value[0] = os.path.abspath(f"textures\\bg\\{value[0]}")
                    if len(value) == 1: value += [255, 1, 1, 1000, self.screen.get_width()]
                    fon = Rendering.load_fon(*value)
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
                    case [name, '-', event] if action[1][0] == '&':
                        action[1] += [name, event]
                    case ['$'] | ['&']:
                        script.append(action)
                        action = []
                    case other:
                        pass
        return self.scenes[sceneType](sceneName, self.screen, fon, music, objects, script)

    def _load_objects(self, path: str, objects: list):  # Загрузка объектов (кнопок) в этой сцене
        newObjects = []
        for currentDir, objectType in objects:
            obj = self.objectsCreator.create(path, currentDir, objectType)
            if obj: newObjects.append(obj)
        return newObjects
