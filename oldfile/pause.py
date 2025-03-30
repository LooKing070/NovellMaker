import os
import pygame


class Pause(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __str__(self):
        return "Pause"

    def __init__(self, screen, textures, text, fons, buttons, fonts, sounds, playerLogin):
        self.screen = screen
        self.setTex = textures
        self.text = text
        self.fon = fons
        self.buttons = buttons
        self.fonts = fonts
        self._sounds, self.fonMusic = sounds, None
        self.playerLogin = playerLogin

        self._load_music()
        self._load_sprites()

    def _load_music(self):
        if self._sounds:
            self.fonMusic = self._sounds.fonMusic["rain_fon"]

    def _load_sprites(self):
        self.pauseSprites = pygame.sprite.Group()
        self.pauseSprites.add(self.text["Player"])
        self.pauseSprites.add(self.text["Level"])
        self.pauseSprites.add(self.text["Kills"])

    def show(self, result="PAUSED", kills=0):
        if result == "YOU DED":
            self.screen.blit(self.fon[0].image, (0, 0))
        elif result == "YOU ESCAPED":
            self.screen.blit(self.fon[1].image, (0, 0))
            self.write_results((self.playerLogin["totalLevel"], kills))
        elif result == "PAUSED":
            self.screen.blit(self.fon[2].image, (0, 0))
        self.pauseSprites.draw(self.screen)
        self.screen.blit(self.text[result].image, (self.text[result].rect.x - len(str(self.text[result])) * 8, self.text[result].rect.y))
        self.screen.blit(self.fonts["settingsFont"].render(f"{self.playerLogin['name']}", 1, (151, 45, 45)), (256, 104))
        self.screen.blit(self.fonts["settingsFont"].render(f"{self.playerLogin['currentLevel']}", 1, (151, 45, 45)), (256, 40))
        self.screen.blit(self.fonts["settingsFont"].render(f"{kills}", 1, (151, 45, 45)), (256, 168))

    def write_results(self, results):
        with open(os.path.abspath("players_data\\login.csv"), "r", newline='', encoding="utf-8") as loginFile:
            playerF = loginFile.readlines()
            plId = playerF[1].split(';')
            plId[1] = str(results[0] + 1)
            plId[3] = str(int(plId[3]) + results[1])
            playerF[1] = ';'.join(plId)
        with open(os.path.abspath("players_data\\login.csv"), "w", newline='', encoding="utf-8") as loginFile:
            loginFile.writelines(playerF)
        # writer = csv.writer(loginFile, delimiter=';', quotechar='\n', quoting=csv.QUOTE_MINIMAL)
