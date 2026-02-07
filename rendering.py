import os
import pygame
import json
import av


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

        self._vidContainer = []
        self._currentVidFrame = True
        self.textures = {}
        self.fonts = {"default": pygame.font.SysFont("arial", 22)}

        with open(f"{self._fontsPath}\\parameters.json") as fontsPar:
            for name, font in json.load(fontsPar).items():
                if "Font" in name:
                    self.fonts[name] = pygame.font.Font(f"{self._fontsPath}\\{font[0]}", font[1])
                else:
                    self.fonts[name] = self.fonts[font]

    def load_fon(self, texName, alfa=255, cols=1, rows=1, animaD=1, sk=1280):
        sheet = self.set_texture(texName, alfa)
        size = sk / sheet.get_rect().w
        return Fon((sheet, 0, 0, cols, rows, animaD, size))

    def set_texture(self, texName, alfa=255):
        if texName not in self.textures:
            tex = pygame.image.load(f"{self._texPath}\\{texName}")
            if "alpha" in texName:
                tex.set_colorkey(tex.get_at((0, 0)))
            tex.set_alpha(int(alfa))
            tex = tex.convert_alpha()
            self.textures[texName] = tex
        return self.textures[texName]

    @staticmethod
    def load_texture(path, alfa=255):
        tex = pygame.image.load(path)
        tex.set_alpha(int(alfa))
        tex = tex.convert_alpha()
        return tex

    @staticmethod
    def get_video_frame(screen, vidContainer):
        for frame in vidContainer:
            img = frame.to_image()
            img = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
            screen.blit(img, (0, 0))
            return img
        return None

    def play_video(self, screen, videoName=''):
        if videoName:
            self._vidContainer = av.open(self._videosPath + f"\\{videoName}").decode(video=0)
        if self._currentVidFrame:
            self._currentVidFrame = self.get_video_frame(screen, self._vidContainer)
        return self._currentVidFrame

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

    def set_transparency(self, coeff: int):
        for frame in range(len(self._savedFrames)):
            self.frames[frame].set_alpha(coeff)

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
        return False


class TextPlane(pygame.sprite.Sprite):
    def __init__(self, texture, transparency, x0, y0, pp, pSpeed, size=1):
        super().__init__()
        self.image = texture
        self._sizeCo = size
        self._savedImage = texture
        self.transparency = transparency
        self.rect = self.image.get_rect()
        self.rect.topleft = (x0, y0)

        self.text = None
        self.pp = pp  # режим печати словами или буквами
        self.pSpeed = pSpeed

    def print(self):
        pass


class Fon(AnimatedSprite):
    def __init__(self, textureParameters):
        super().__init__(*textureParameters)

    def update(self, size=()):
        if size:
            self.resize(size[0], size[1])

