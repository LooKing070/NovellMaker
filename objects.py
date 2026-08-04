import os
import json
import pygame.font
from pygame import sprite
from rendering import AnimatedSprite, TextPlane, Rendering
from sounder import Sounder


class Button(AnimatedSprite):
    def __init__(self, visual: dict, parameters: dict, events: dict, text: dict = None):
        super().__init__(**visual)
        self.x, self.y = self.rect.x, self.rect.y
        self.events = events
        self.text = text
        self.sounds = parameters["sounds"]
        self.textFonts = parameters["speech"]
        self.tName = parameters["tName"]  # техническое имя

        self.clicks = 0

    def __str__(self):
        return "Button"

    def check_click(self, pos):
        if self.rect.x <= pos[0] <= self.rect.x + self.rect.w and \
                self.rect.y <= pos[1] <= self.rect.y + self.rect.h and self.image.get_alpha() > 0:
            self.clicks += 1
            return self.do()
        return False

    def do(self, event="on_click"):
        result = ''
        if event in self.events:
            if "on_" in event:
                result = [self.do(eS) for eS in self.events[event]]
            elif "tran_" in event:
                self.set_transparency(self.events[event])
                result = self.tName
            elif "play_" in event:
                self.update(animaCount=self.events[event][0])
                result = self.tName
            elif "sdut_" in event:
                self.sounds[self.events[event]].play(0)
                result = self.tName
            else:
                result = self._do(event)
        else:
            print(self.tName, "ERROR: THERE IS NO SUCH EVENT")
        return result

    def _do(self, event=""):
        result = ''
        if "load_" in event:
            result = "lo&" + self.events[event]
        return result

    def update(self, size=(), animaCount=1):
        if size:
            self.resize(size[0], size[1])
            self.rect.x = self.x * size[0]
            self.rect.y = self.y * size[1]
        else:
            self.runAnim = animaCount


class VideoPlayer:
    def __init__(self, visual: dict, parameters: dict, events: dict, text: dict):
        self.screen = parameters["screen"]
        self.sounds = parameters["sounds"]
        self.tName = parameters["tName"]
        self.events = events

    def __str__(self):
        return "VidPlr"

    def do(self, event="play_video"):
        result = ''
        if "play_" in event:
            Rendering.play_video(self.screen, self.events[event])
            result = self.tName
        elif "sdut_" in event:
            self.sounds[self.events[event]].play(0)
            result = self.tName
        else:
            print(str(self), "ERROR: THERE IS NO SUCH EVENT")
        return result


class BindBox(Button):
    def __init__(self, visual: dict, parameters: dict, events: dict, text: dict):
        super().__init__(visual, parameters, events, text)
        self.tName = parameters["tName"]

    def __str__(self):
        return "BinBox"


class Actor(Button):
    def __init__(self, visual: dict, parameters: dict, events: dict, text: dict):
        super().__init__(visual, parameters, events, text)
        self.name = parameters["name"]

    def __str__(self):
        return "Actor"

    def _do(self, event=""):
        result = ''
        if "say_" in event:
            result = []
            for i in range(0, len(self.events[event]), 2):
                result += ["sa&", self.events[event][i], self.name, self.text[self.events[event][i+1]],
                           self.textFonts[self.events[event][i+1]] if self.events[event][i+1] in self.textFonts else None]
        """elif "plot_" in event:
            self.plotScore += self.events[event]
            result = self.tName"""
        return result


class Dialog(TextPlane):
    def __init__(self, visual: dict, parameters: dict, events: dict, font: pygame.font.Font):
        super().__init__(font, **visual)
        self.tName = parameters["tName"]
        self.sounds = parameters["sounds"]
        self.clicks = 0
        self.events = events
        self.events["paus_"] = None

    def __str__(self):
        return "Dialog"

    def check_click(self, pos):
        if self.rect.x <= pos[0] <= self.rect.x + self.rect.w and \
                self.rect.y <= pos[1] <= self.rect.y + self.rect.h and self.image.get_alpha() > 0:
            self.clicks += 1
            return self.do("paus_")
        return False

    def do(self, event):
        result = ''
        if isinstance(event, list):
            result = self.tName
            self.runAnim = True
            self.set_text(*event)
        elif event in self.events:
            if "on_" in event:
                result = [self.do(eS) for eS in self.events[event]]
            elif "tran_" in event:
                self.set_transparency(self.events[event])
                result = self.tName
            elif "paus_" in event:
                self.runAnim = not self.runAnim
                result = self.tName
            else:
                pass
                # result = self._do(event)
        else:
            print(self.tName, "ERROR: THERE IS NO SUCH EVENT")
        return result

    def update(self, size=()):
        self.resize(size[0], size[1])
        self.rect.x = self.x * size[0]
        self.rect.y = self.y * size[1]


class Inventory(sprite.Sprite):
    def __init__(self, visual: dict, parameters: dict, events: dict, text: dict):
        super().__init__()
        self._cols = 8
        self._rows = 3
        self._bagesInterval = 10  # толщина линий между ячейками
        self.cellSize = 80
        self.cells = []
        self.currentCell = 0

    def __str__(self):
        return "Inventory"

    def check_click(self, pos):
        if self.rect.x <= pos[0] <= self.rect.x + self.rect.w and \
                self.rect.y <= pos[1] <= self.rect.y + self.rect.h and self.image.get_alpha() > 0:
            self.clicks += 1
            return self.do("choose_")
        return False

    def do(self, event=""):
        result = ''
        if "add_" in event:
            pass
        elif "del_" in event:
            pass
        return result


class Picture(AnimatedSprite):
    def __init__(self, visual: dict, parameters: dict = None, events: dict = None, text: dict = None):
        super().__init__(**visual)
        if parameters and "tName" in parameters: self.tName = parameters["tName"]  # техническое имя
        else: self.tName = "fon"
        self.clicks = 0

    def check_click(self, pos):
        if self.rect.x <= pos[0] <= self.rect.x + self.rect.w and \
                self.rect.y <= pos[1] <= self.rect.y + self.rect.h and self.image.get_alpha() > 0:
            self.clicks += 1
        return False

    def update(self, size=()):
        if size:
            self.resize(size[0], size[1])


class ObjectsCreator(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self.render = Rendering()
        self.sounder = Sounder()
        self.objectTypes = {"Button": Button, "BinBox": BindBox, "VidPlr": VideoPlayer, "Actor": Actor,
                            "Inventory": Inventory, "Dialog": Dialog, "Picture": Picture}

    def create(self, path, currentDir):
        events, parameters, speech, visual = {}, {}, {}, {}
        objectType = ''
        for f in os.listdir(os.path.join(path, currentDir)):
            if ".json" in f:
                with open(os.path.join(path, currentDir, f), 'r', encoding="utf-8") as file:
                    if "events" in f:
                        events = {k: v for k, v in json.load(file).items()}
                    elif "parameters" in f:
                        for k, v in json.load(file).items():
                            if k in ["type", "sounds", "buttons", "owners", "music", "name", "speech"]:
                                parameters[k] = v
                            else: visual[k] = v
                        if "type" in parameters: objectType = parameters["type"]
                        parameters["tName"] = currentDir
                        if "texture" in visual: visual["texture"] = self.render.set_texture(visual["texture"])
                        if "sounds" in parameters:
                            sounds = {}
                            for i in range(len(parameters["sounds"])):
                                sounds[parameters["sounds"][i][:-4]] = self.sounder.load_sound(parameters["sounds"][i])
                            parameters["sounds"] = sounds
                        if "speech" in parameters:
                            textFonts = {}
                            for i in range(0, len(parameters["speech"]), 2):
                                textFonts[parameters["speech"][i]] = self.render.fonts[parameters["speech"][i+1]]
                            parameters["speech"] = textFonts

            elif ".txt" == f[-4:]:
                with open(os.path.join(path, currentDir, f), 'r', encoding="UTF8") as text:
                    for string in text.readlines():
                        string = string.rstrip()
                        if string[-1] == string[0] == '&':
                            title = string[1:-1]
                            speech[title] = ""
                        else:
                            speech[title] += string + ' '

        if objectType == "Dialog":
            speech = self.render.fonts["default"]
        if objectType not in self.objectTypes:
            print(f"ERROR: OBJECT_TYPE '{objectType}' IS NOT EXIST")
            return None
        return self.objectTypes[objectType](visual, parameters, events, speech)
