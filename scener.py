import json
import os
import pygame
from builder import resource_path
from objects import ObjectsCreator
from sounder import Sounder


class Scene:
    def __str__(self):
        return self.sceneName

    def __init__(self, sceneName, screen, objects, script: list):
        self.sceneName = sceneName
        self.screen = screen
        self.screenSize = self.screen.get_width(), self.screen.get_height()
        self.script = script  # [[obj, [event]], [obj, [event]], ]
        self.action = 0
        self.plotScore = 0
        self.q = []  # очередь из ивентов
        self.objects = {}
        for obj in objects:
            self.objects[obj.tName] = obj
        self.result = "PAUSED"

    def continue_script(self):  # выполнение скрипта
        result = ''
        if len(self.script) > self.action:
            obj, event = self.script[self.action]

            if obj in self.objects:
                if type(event) == str:
                    result = self.objects[obj].do(event)
                elif event[0] == '$':  # блок с выбором действия исходя из сюжета
                    for i in range(1, len(event), 2):
                        if event[i] <= self.plotScore:
                            result = self.objects[obj].do(event[i + 1])
                            break

            elif event[0] == '&':  # блок одновременного выполнения ивентов разными персонажами
                for i in range(1, len(event), 2):
                    result = self.objects[event[i]].do(event[i + 1])

            else: print(f"ERROR: OBJECT '{obj}' NOT FOUND. ERROR BLOCK - {self.action + 1}")
            self.action += 1

        else: print("THE ACTION ENDED IN THE SCENE")
        return result

    def show(self):  # Возвращает текущие действия
        if self.q:
            if isinstance(self.q[0], list):
                if self.q[0][0] == "sa&":
                    self.objects[self.q[0][1]].do(self.q[0][2:])
                    self.q[0].remove("sa&")
                elif self.q[0][0] == "pl&":
                    self.plotScore += self.q[0][1]
                elif not self.objects[self.q[0][0]].runAnim:
                    self.q.pop(0)
            # print(self.q)
        for obj in self.objects.values():
            if obj.transparency:
                obj.draw(self.screen)
                obj.do_anim()
            if obj.runAnim:
                if obj.tName not in self.q:
                    self.q.append(obj.tName)
            elif obj.tName in self.q:
                self.q.remove(obj.tName)
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
        self.scenes = {"baseScene": Scene, "conversation": Scene, "activity": Scene}

    def load_scene(self, sceneName: str = "menu"):
        music = {}
        objects = []
        script = []
        sceneType = "conversation"
        path = os.path.join(self.path, sceneName)
        with open(os.path.join(path, "parameters.json"), 'r', encoding="utf-8") as par_file:
            file = dict(json.load(par_file).items())
            if "type" not in file: file["type"] = "baseScene"
            if file["type"] in ["conversation", "activity", "baseScene"]:
                sceneType = file.pop("type")
                music["sounds"] = {"music": self.sounder.load_fon_music(file.pop("music"))}
                if "texture" in file: file["texture"] = self.objectsCreator.render.set_texture(file["texture"])
                fon = self.objectsCreator.objectTypes["Picture"](file, music)
                objects.append(fon)
            # print(F"ERROR: PARAMETERS ARE NOT CORRECT IN SCENE {sceneName}")

        objects += self._load_objects(path)
        with open(os.path.join(path, "script.txt"), 'r', encoding="utf-8") as scr_file:
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
        return self.scenes[sceneType](sceneName, self.screen, objects, script)

    def _load_objects(self, path: str):  # Загрузка объектов (кнопок) в этой сцене
        objects = []
        with os.scandir(path) as currentDirs:
            for currentDir in currentDirs:
                if currentDir.is_dir():
                    obj = self.objectsCreator.create(path, currentDir.name)
                    if obj: objects.append(obj)
        return objects
