import os
import pygame


class Sounder(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self._music_path = os.path.abspath("sounds\\fon_music")
        self._sounds_path = os.path.abspath("sounds\\interaction_sounds")
        self._sounds = {}

    def load_fon_music(self, fileName: str) -> pygame.mixer.Sound:
        if fileName not in self._sounds:
            self._sounds[fileName] = pygame.mixer.Sound(f"{self._music_path}\\{fileName}")
        return self._sounds[fileName]

    def load_sound(self, fileName: str) -> pygame.mixer.Sound:
        if fileName not in self._sounds:
            self._sounds[fileName] = pygame.mixer.Sound(f"{self._sounds_path}\\{fileName}")
        return self._sounds[fileName]
