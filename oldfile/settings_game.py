import pygame


class Settings(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __str__(self):
        return "Settings"

    def __init__(self, screen, textures, text, fon, buttons, sounds, playerSettings):
        self.screen = screen
        self.setTex = textures
        self.text = text
        self.fon = fon[0]
        self.buttons = buttons
        self._sounds, self.fonMusic = sounds, None
        self.playerSettings = playerSettings

        self._load_sprites()
        self._load_music()

    def _load_music(self):
        if self._sounds:
            self.fonMusic = self._sounds.fonMusic["city_fon"]

    def _load_sprites(self):  # Загрузка спрайтов в этой сцене
        self.settingsSprites = pygame.sprite.Group()
        self.settingsSprites.add(self.fon)
        self.settingsSprites.add(self.text["Controls"]), self.settingsSprites.add(self.text["Sound & Music & Video"])
        self.settingsSprites.add(self.text["Change slot"]), self.settingsSprites.add(self.text["Music"])
        self.settingsSprites.add(self.text["Walking"]), self.settingsSprites.add(self.text["Sounds"])
        self.settingsSprites.add(self.text["Interaction"]), self.settingsSprites.add(self.text["Resolution"])
        self.settingsSprites.add(self.text["Combat"]), self.settingsSprites.add(self.text["Language"])
        for buttonSpr in self.buttons.values():
            self.settingsSprites.add(buttonSpr)

    def show(self):
        self.settingsSprites.draw(self.screen)

    def save_settings(self):
        pass

