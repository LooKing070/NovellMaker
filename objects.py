from pygame import sprite
from rendering import AnimatedSprite, TextPlane, Rendering


class Button(AnimatedSprite):
    def __init__(self, parameters: dict, events: dict, text: dict):
        super().__init__(*parameters["texture"])
        self.x, self.y = self.rect.x, self.rect.y
        self.events = events
        self.text = text
        self.sounds = parameters["sounds"]
        textFonts = parameters["speech"]
        self.tName = parameters["type"]  # техническое имя

        self.clicks = 0
        self.plotScore = 0

    def __str__(self):
        return "Button"

    def check_click(self, pos):
        if self.rect.x <= pos[0] <= self.rect.x + self.rect.w and \
                self.rect.y <= pos[1] <= self.rect.y + self.rect.h:
            self.clicks += 1
            self.do()
            return self.clicks
        return False

    def update(self, size=(), animaCount=1):
        if size:
            self.resize(size[0], size[1])
            self.rect.x = self.x * size[0]
            self.rect.y = self.y * size[1]
        else:
            self.runAnim = animaCount
            self.do_anim()

    def do(self, event="on_click"):
        result = False
        if "on_" in event:
            result = [self.do(eS) for eS in self.events[event]]
        elif "tran_" in event:
            self.set_transparency(int(self.events[event]))
            result = True
        elif "play_" in event:
            if self.events[event].isdigit():
                self.update(animaCount=self.events[event])
            else:
                self.sounds[self.events[event]].play(-1)
            result = True
        else:
            result = self._do(event)
            if not result:
                print(self.tName, "ERROR: THERE IS NO SUCH EVENT")
        return result

    def _do(self, event=""):
        result = False
        if "load_" in event:
            result = "lo&" + self.events[event]
        return result


class VideoPlayer:
    def __init__(self, parameters: dict, events: dict, text: dict):
        self.screen = parameters["screen"]
        self.sounds = parameters["sounds"]
        self.textFonts = parameters["speech"]
        self.tName = parameters["type"]
        self.events = events
        self.text = text

        self.plotScore = 0

    def __str__(self):
        return "VidPlr"

    def do(self, event="play_video"):
        if "play_" in event:
            if self.events[event][-3:] == "mp4":
                Rendering.play_video(self.screen, self.events[event])
            else:
                self.sounds[self.events[event]].play(-1)
        else:
            print(str(self), "ERROR: THERE IS NO SUCH EVENT")


class BindBox(Button):
    def __init__(self, parameters: dict, events: dict, text: dict):
        super().__init__(parameters, events, text)

    def __str__(self):
        return "BinBox"


class Actor(Button):
    def __init__(self, parameters: dict, events: dict, text: dict):
        super().__init__(parameters, events, text)
        # self.name = TextPlane(textFonts, parameters["name"])

    def __str__(self):
        return "Actor"

    def _do(self, event=""):
        result = False
        if "say_" in event:
            result = "sa&" + self.text[self.events[event]]
        elif "plot_" in event:
            self.plotScore += int(self.events[event])
            result = self.plotScore
        return result


class Dialog(Button):
    def __init__(self, parameters: dict, events: dict, text: dict):
        super().__init__(parameters, events, text)

    def __str__(self):
        return "Dialog"


class Inventory(sprite.Sprite):
    def __init__(self, parameters: dict, events: dict, text: dict):
        super().__init__()
        self._cols = 8
        self._rows = 3
        self._bagesInterval = 10  # толщина линий между ячейками
        self.cellSize = 80

    def __str__(self):
        return "Inventory"

    def do(self, event=""):
        result = False
        if "add_" in event:
            pass
        elif "del_" in event:
            pass
        return result


class ObjectsCreator(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self.objectTypes = {"Button": Button, "BinBox": BindBox, "VidPlr": VideoPlayer, "Actor": Actor,
                            "Inventory": Inventory, "Dialog": Dialog}

    def create(self, type, parameters, events, text):
        if type in self.objectTypes:
            return self.objectTypes[type](parameters, events, text)
        else:
            return self.objectTypes["Button"](parameters, events, text)
