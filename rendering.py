import os
import pygame
import json


class Rendering(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self._texPath = os.path.abspath("textures")
        self._fontsPath = os.path.abspath("fonts")
        self._videosPath = os.path.abspath("videos")

        self.textures = {}
        self.fonts = {"default": pygame.font.SysFont("arial", 22)}
        self.buttonsCreator = ButtonsCreator()

        with open(f"{self._fontsPath}\\parameters.json") as fontsPar:
            for name, font in json.load(fontsPar).items():
                if "Font" in name:
                    self.fonts[name] = pygame.font.Font(f"{self._fontsPath}\\{font[0]}", font[1])
                else:
                    self.fonts[name] = self.fonts[font]

    def load_fon(self, texName, colorKey=False, cols=1, rows=1, animaD=1, sk=1280):
        sheet = self.set_texture(texName, colorKey)
        size = sk / sheet.get_rect().w
        return Fon((sheet, 0, 0, cols, rows, animaD, size))

    def set_texture(self, texName, colorKey=0):
        if texName not in self.textures:
            tex = pygame.image.load(f"{self._texPath}\\{texName}")
            colorKey = int(colorKey)
            if colorKey:
                tex.set_alpha(colorKey)
                colorKey = tex.get_at((0, 0))
                tex.set_colorkey(colorKey)
                tex = tex.convert()
            else:
                tex = tex.convert_alpha()
            self.textures[texName] = tex
        return self.textures[texName]

    @staticmethod
    def load_texture(path, colorKey=False):
        tex = pygame.image.load(path)
        if colorKey:
            colorKey = tex.get_at((0, 0))
            tex.set_colorkey(colorKey)
            tex = tex.convert()
        else:
            tex = tex.convert_alpha()
        return tex

    def play_screen_saver(self):
        return


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, x=0, y=0, columns=1, rows=1, animationDelay=0, size=1):
        super().__init__()
        self.frames = []
        self._cut_sheet(sheet, columns, rows)
        self._sizeCo = size
        self._savedFrames = self.frames[::]
        self.currentFrame = 0
        self.animationTimer, self.animationDelay = 0, animationDelay
        self.runAnim = 0
        self.image = self.frames[self.currentFrame]

        self.rect.topleft = (x, y)
        self.resize(1, 1)

    def _cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def resize(self, xCo, yCo):
        for frame in range(len(self._savedFrames)):
            sheet = self._savedFrames[frame]
            self.frames[frame] = pygame.transform.scale(sheet, (sheet.get_width() * self._sizeCo * xCo,
                                                                sheet.get_height() * self._sizeCo * yCo))
        self.image = self.frames[self.currentFrame]
        self.rect.size = self.image.get_size()

    def do_anim(self, currentFrame=0, endFrame=0, object=None):
        if not endFrame: endFrame = len(self.frames) - 1
        if not currentFrame: currentFrame = self.currentFrame
        if self.runAnim and pygame.time.get_ticks() >= self.animationTimer:
            self.currentFrame = (self.currentFrame + 1) % len(self.frames)
            if object:
                object.image = self.frames[self.currentFrame]
            else:
                self.image = self.frames[self.currentFrame]
            if currentFrame == endFrame:
                self.runAnim -= 1
                pygame.time.set_timer(self.animationTimer, 0)
            self.animationTimer = pygame.time.get_ticks() + self.animationDelay
            return self.runAnim
        return True


class TextPlane(pygame.sprite.Sprite):
    def __init__(self, parameters, font, coords: tuple):
        super().__init__()
        self.font = font
        self.image = self.font.render(*parameters)
        self.rect = self.image.get_rect()
        self.rect.topleft = coords


class Fon(AnimatedSprite):
    def __init__(self, textureParameters):
        super().__init__(*textureParameters)

    def update(self, size=()):
        if size:
            self.resize(size[0], size[1])


class Perehod(AnimatedSprite):
    def __init__(self, textureParameters):
        super().__init__(*textureParameters)

    def update(self, size=()):
        if size:
            self.resize(size[0], size[1])


class Button(AnimatedSprite):
    def __init__(self, parameters: dict, events: dict, text: dict):
        super().__init__(*parameters["texture"])
        self.x, self.y = self.rect.x, self.rect.y
        self.events = events
        self.text = text
        self.sounds = parameters["sounds"]
        textFonts = parameters["speech"]
        self.type = parameters["type"]
        # self.name = TextPlane(textFonts, parameters["name"])

        self.showed = False
        self.clicks = 0

    def __str__(self):
        return "Button"

    def check_click(self, pos):
        if self.rect.x <= pos[0] <= self.rect.x + self.rect.w and \
                self.rect.y <= pos[1] <= self.rect.y + self.rect.h:
            self.clicks += 1
            return self.clicks
        return False

    def update(self, size=(), animaCount=1):
        if size:
            self.resize(size[0], size[1])
            self.rect.x = self.x * size[0]
            self.rect.y = self.y * size[1]
        else:
            self.runAnim = animaCount

    def do(self, event="on_click"):
        result = ''
        if event in self.events:
            if "on_" in event:
                result = [self.do(eS) for eS in self.events[event]]
            elif "show_" in event:
                result = "sh&" + self.events[event]
            elif "say_" in event:
                result = "sa&" + self.text[self.events[event]]
            elif "sound_" in event:
                self.sounds[self.events[event]].play(-1)
            elif "play_" in event:
                self.update(animaCount=self.events[event])
            elif "load_" in event:
                result = "lo&" + self.events[event]
        return result


class BindBox(Button):
    def __init__(self, parameters: dict, events: dict, text: dict):
        super().__init__(parameters, events, text)


class Lister(Button):
    def __init__(self, parameters: dict, events: dict, text: dict):
        super().__init__(parameters, events, text)


class Actor(Button):
    def __init__(self, parameters: dict, events: dict, text: dict):
        super().__init__(parameters, events, text)


class Dialog(Button):
    def __init__(self, parameters: dict, events: dict, text: dict):
        super().__init__(parameters, events, text)


class ButtonsCreator(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self.buttonTypes = {"Button": Button, "BinBox": BindBox, "Lister": Lister, "Actor": Actor}

    def create_button(self, type, parameters, events, text):
        if type in self.buttonTypes:
            return self.buttonTypes[type](parameters, events, text)
        else:
            return self.buttonTypes["Button"](parameters, events, text)
