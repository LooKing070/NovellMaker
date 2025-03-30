import os
import pygame
import json
import random


class Game(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __str__(self):
        return "Game"

    def __init__(self, screen, textures, text, fon, buttons, sounds, playerLogin: dict):
        self.screen = screen
        self.screenSize = self.screen.get_width(), self.screen.get_height()
        self._setTex = textures
        self._text = text
        self._fon = fon[0]
        self.buttons = buttons
        self._sounds, self.fonMusic = sounds, None
        self.result = "PAUSED"

        self._load_player_login(playerLogin)
        self._load_level_parameters()
        self.location = location.Location(self.screenSize, self._setTex)
        self._load_sprites()
        self._load_music()

        self.camera = Camera(self.screenSize)
        self.entityCreator = entities.EntityCreator(self._setTex, self._sounds, self.levelParameters["difficulty"],
                                                    self.entityColliders)

    def _load_sprites(self):  # Загрузка спрайтов в этой сцене
        self.damagerSprites = pygame.sprite.Group()
        self.enemySprites = pygame.sprite.Group()
        self.broSprites = pygame.sprite.Group()
        self.itemHudSprites = pygame.sprite.Group()

        self.entityColliders = {"wallS": self.location.wallSprites, "enemyS": self.enemySprites,
                                "broS": self.broSprites, "damagerS": self.damagerSprites}

    def _load_music(self):
        if self._sounds:
            if self.currentLevel < 2:
                self.fonMusic = self._sounds.fonMusic["city_fon"]
            elif self.currentLevel == 2:
                self.fonMusic = self._sounds.fonMusic["rain_fon"]

    def _load_player_login(self, playerLogin: dict):
        self.playerName = playerLogin["name"]
        self.currentLevel = int(playerLogin["currentLevel"])
        self.currentInventory = playerLogin["currentInventory"]

    def _load_level_parameters(self):
        with open(os.path.abspath(f"levels\\uroven{self.currentLevel}\\parameters.json")) as par_file:
            self.levelParameters = json.load(par_file)
            for key, value in self.levelParameters.items():
                if key == "entities":
                    self.bro = value[:1]
                    self.enemies = value[1:]
                    # self.enemies == [[x, y, 'Zomb', count, inventory], [_, _, _, _], _].
                elif key == "estate":
                    self.estate = value
                    # self.estate == [[x, y, 'Wardrobe', rotationAngle, inventory], [_, _, _, _], _]

    def _load_location(self):
        self.location.tileSprites.empty(), self.location.wallSprites.empty()
        self._load_level_parameters()
        self.location.set_coords(self.levelParameters["entities"][0][:2])
        self.location.levelStructure = self.location.load_structure(self.currentLevel, "structure.txt")
        self.location.tiles_loader()
        self.location.sectors_loader()
        self.location.sectors_loader(self.levelParameters["shader"])
        c = 0
        for tile in self.location.tileSprites:
            if str(tile) in ["GS"]:
                self.buttons[f"{tile}{c}"] = tile
                c += 1

    def _load_entities(self):
        self.enemies = self.entityCreator.entity_coord_improver(self.screenSize, self.levelParameters["entities"][0],
                                                                self.enemies)
        self.aliveEnemies = []
        for enemi in range(len(self.enemies)):
            enemyEnt = self.enemies[enemi]
            enemyEnt.append(hud.Hud(self._setTex, self.screenSize, self.buttons, enemyEnt[2], enemyEnt.pop(3)))
            enemy = self.entityCreator.create_entity(enemyEnt)
            enemy.weapon = self.entityCreator.create_entity([enemy.x, enemy.y, enemy.hud.activeItem, []])
            self.aliveEnemies.append(enemy)
        playerEnt = self.bro[0][:-2]
        playerEnt.append(hud.Hud(self._setTex, self.screenSize, self.buttons, playerEnt[2], self.currentInventory))
        self.player = self.entityCreator.create_entity(playerEnt)
        self.player.weapon = self.entityCreator.create_entity([self.player.x, self.player.y, self.player.hud.activeItem, []])

    def start(self, playerLogin):
        self._load_player_login(playerLogin)
        self._load_location()
        self._load_entities()

    def show(self):  # Возвращает ЛОЖЬ для продолжения игры
        if self.player.state != "alive":
            self.result = "YOU DED"
            return True
        self.camera.move_target(self.player)
        self.camera.move_obj(self.enemySprites)
        self.camera.move_obj(self.location.tileSprites)
        self.camera.move_obj(self.location.wallSprites)

        self.player.weapon.entityCollider.do_anim(self.player.weapon.entityCollider.currentFrame, 3, self.player.weapon)
        self.location.tileSprites.draw(self.screen)
        self.location.wallSprites.draw(self.screen)
        self.damagerSprites.draw(self.screen)
        for entity in self.aliveEnemies:
            self.player.see((entity.x, entity.y), entity)
            entity.see([self.player.x, self.player.y])
            entity.particleGenerator.draw(self.screen)
        self.player.particleGenerator.draw(self.screen)
        self.broSprites.draw(self.screen)
        self.enemySprites.draw(self.screen)
        self.player.hud.hudSprites.draw(self.screen)
        if self.player.sight:
            self.player.sight.hud.hudSprites.draw(self.screen)
        self.itemHudSprites.draw(self.screen)
        self.screen.blit(self._text[self.player.hud.activeItem].image, self._text[self.player.hud.activeItem].rect)
        return False


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
                # camspx = abs(target.rect.centerx - self.camcx) / 200 + 1
                # camspy = abs(target.rect.centery - self.camcy) / 200 + 1
                self.speed = target.speed
                # self.camcx += 0.0001 * self.direction[0]  # self.speedx
                # self.camcy += 0.0001 * self.direction[1]  # self.speedy
            else:
                self.speed = 0
