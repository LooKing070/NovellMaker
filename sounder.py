import pygame
from builder import resource_path


class Sounder(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self._sounds = {}

    def load_fon_music(self, fileName: str) -> pygame.mixer.Sound:
        if fileName not in self._sounds:
            self._sounds[fileName] = pygame.mixer.Sound(resource_path(["sounds", "fon_music", f"{fileName}"]))
        return self._sounds[fileName]

    def load_sound(self, fileName: str) -> pygame.mixer.Sound:
        if fileName not in self._sounds:
            self._sounds[fileName] = pygame.mixer.Sound(resource_path(["sounds", "interaction_sounds", f"{fileName}"]))
        return self._sounds[fileName]
