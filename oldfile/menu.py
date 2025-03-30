import pygame


class Menu(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __str__(self):
        return "Menu"

    def __init__(self, screen, textures, text, fon, buttons, sounds=None):
        self.screen = screen
        self.setTex = textures
        self.text = text
        self.fon = fon[0]
        self.buttons = buttons
        self._sounds, self.fonMusic = sounds, None

        self._load_sprites()
        self._load_music()

    def _load_music(self):
        if self._sounds:
            self.fonMusic = self._sounds.fonMusic["dead_rave"]

    def _load_sprites(self):  # Загрузка спрайтов в этой сцене
        self.menuSprites = pygame.sprite.Group()  # группа меню спрайтов
        self.menuSprites.add(self.fon)
        self.menuSprites.add(self.text["start"]), self.menuSprites.add(self.text["settings"])
        for buttonSpr in self.buttons.values():
            self.menuSprites.add(buttonSpr)

    def show(self):  # возвращает False для продолжения сцены
        self.menuSprites.draw(self.screen)
        return not all([button.do_anim() for button in self.buttons.values()])
