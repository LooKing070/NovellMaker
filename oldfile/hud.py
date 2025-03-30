import pygame


class Hud:
    def __init__(self, textures, screenSize, items, owner="Player", currentInventory=('', '', '', '')):
        self.owner = owner
        self.setTex = textures
        self.screenSize = screenSize
        self.elements = {k: v for k, v in items.items()}
        self.inventory = currentInventory[:]
        self.activeItem = self.inventory[0]

        self._load_sprites()

    def _load_sprites(self):  # Загрузка спрайтов
        self.hudSprites = pygame.sprite.Group()
        for i in HUDITEMS:
            self.elements[i[0]] = pygame.sprite.Sprite()
            self.elements[i[0]].image = self.setTex[i[1]]
            self.elements[i[0]].rect = self.elements[i[0]].image.get_rect()
            if self.owner in i[0]:
                self.hudSprites.add(self.elements[i[0]])
            elif i[0] not in list(WEAPONS.keys()):
                self.hudSprites.add(self.elements[i[0]])

        self.elements["playerRamka"].rect.x, self.elements["playerRamka"].rect.y = 0, 0
        self.elements["playerInventory"].rect.x, self.elements["playerInventory"].rect.y =\
            0, self.elements["playerRamka"].rect.h
        self.elements["Player"].rect.x = (self.elements["playerRamka"].rect.w - self.elements["Player"].rect.w) // 2
        self.elements["Player"].rect.y = (self.elements["playerRamka"].rect.h - self.elements["Player"].rect.h) // 2
        self.elements["eRamka"].rect.x = self.screenSize[0] - self.elements["eRamka"].rect.w
        self.elements["unknown"].rect.x = self.screenSize[0] - self.elements["eRamka"].rect.w + 4
        self.elements["unknown"].rect.y = 4

    def interaction_with_inventory(self, action: str, item: str):
        if action == "select":
            self.activeItem = item
        elif action == "add":
            if not all(self.inventory):
                self.inventory.insert(self.inventory.index(''), item)
        elif action == "put":
            self.inventory.remove(item)
            self.inventory.append('')
            if self.activeItem not in self.inventory:
                self.interaction_with_inventory("select", self.inventory[0])

    def render_inventory(self, groupSprites):
        for item in self.inventory:
            if item:
                shiftX = (self.inventory.index(item) + 1) % 2
                shiftY = round((self.inventory.index(item) + 1) ** 0.5 / 3) - 1
                itemW, itemH = self.elements["almanac"].rect.w, self.elements["almanac"].rect.h
                originX, originY =\
                    self.elements["playerInventory"].rect.centerx, self.elements["playerInventory"].rect.centery
                shiftX = originX - itemW * shiftX + (2 * -shiftX + 1)
                shiftY = originY + itemH * shiftY + 11 + shiftY * 2
                self.elements[item].rect.x = shiftX
                self.elements[item].rect.y = shiftY
                groupSprites.add(self.elements[item])
