import os
import pygame
from random import randint


class Location(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, screenSize, textures):
        self._setTex = textures
        self.screenSize = screenSize
        self.x, self.y = 0, 0
        self.levelStructure = []  # self.level_builder("44 61", TILESYMBOLS)

        self._load_sprites()

    def _load_sprites(self):  # Загрузка спрайтов
        self.wallSprites = pygame.sprite.Group()
        self.shaderSprites = pygame.sprite.Group()
        self.tileSprites = pygame.sprite.Group()

    def set_coords(self, px_py):
        self.x, self.y = (-px_py[0]) + (self.screenSize[0] // 2), (-px_py[1]) + (self.screenSize[1] // 2)

    @staticmethod
    def load_structure(currentLevel, file):
        path = os.path.abspath(f"levels\\uroven{currentLevel}\\{file}")
        with open(path, "r", newline="\n", encoding="utf-8") as ls:
            cellNameLen = int(ls.readline())
            structure = []
            for field in ls.readlines():
                cellList = []
                for s in range(cellNameLen, len(field.strip()) + cellNameLen, cellNameLen):
                    cellList.append(field[(s - cellNameLen):s])
                structure.append(cellList)
        return structure

    def tiles_loader(self):
        y = self.y
        for field in self.levelStructure:  # загружаем текстуры
            x = self.x
            for cell in field:
                self.tileSprites.add(Tile(x, y, self._setTex[CELLS[cell[:1]][cell[-1:]][0]], cell))
                x += TILESIZE
            y += TILESIZE

    def sectors_loader(self, shader=(), mask=('W', 'R')):  # [[x, y, xL, yL, [r,g,b]], _]
        if not shader:
            shader = self.find_max_rectangles(self.levelStructure, mask)
        for sector in shader:
            if mask[0] in sector[-1]:
                self.wallSprites.add(Sector(self.x + sector[1] * TILESIZE, self.y + sector[0] * TILESIZE,
                                            (sector[3] - sector[1] + 1) * TILESIZE,
                                            (sector[2] - sector[0] + 1) * TILESIZE, sector[4]))
            else:
                self.shaderSprites.add(Sector(self.x + sector[1] * TILESIZE, self.y + sector[0] * TILESIZE,
                                              sector[3] * TILESIZE, sector[2] * TILESIZE, sector[4]))

    @staticmethod
    def level_builder(x_y, symbols):  # строит уровень
        x, y = [int(p) for p in x_y.split()]
        level = []
        for field in range(1, y):
            if field == 1:
                level.append(symbols['W'][0] * x + "\n")
            else:
                level.append("{}{}{}{}".format(symbols['W'][0], symbols['G'][0] * (x - 2), symbols['W'][0], "\n"))
        level.append(symbols['W'][0] * x)
        return level

    @staticmethod
    def find_max_rectangles(matrix, mask: tuple):
        n = len(matrix)
        m = len(matrix[0]) if n > 0 else 0
        rectangles = []

        def is_inside(new_rect, existing_rect):
            return (new_rect[0] >= existing_rect[0] and
                    new_rect[1] >= existing_rect[1] and
                    new_rect[2] <= existing_rect[2] and
                    new_rect[3] <= existing_rect[3])

        for i in range(n):
            for j in range(m):
                if matrix[i][j][0] in mask:
                    start_row, start_col = i, j
                    bottom_row = start_row
                    while bottom_row < n and matrix[bottom_row][j][0] in mask:
                        bottom_row += 1
                    bottom_row -= 1
                    right_col = start_col
                    while right_col < m and all(matrix[x][right_col][0] in mask for x in range(start_row, bottom_row + 1)):
                        right_col += 1
                    right_col -= 1

                    new_rectangle = (start_row, start_col, bottom_row, right_col, mask[0])
                    if not any(is_inside(new_rectangle, existing) for existing in rectangles):
                        rectangles.append(new_rectangle)
        return rectangles  # Найденные прямоугольники (r1, c1, r2, c2, gN)


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, texture, groupName):
        super().__init__()
        self.x, self.y = x, y
        self.image = texture
        self.rect = self.image.get_rect()
        self.name = groupName
        if groupName == 'G':
            self.image = pygame.transform.rotate(self.image, 90 * randint(0, 3))

    def update(self, direction_x_y: list, speed: float):  # передвигаемся
        self.x += speed * direction_x_y[0]
        self.y += speed * direction_x_y[1]
        self.rect.topleft = self.x, self.y

    def check_click(self, pos):
        if self.rect.x <= pos[0] <= self.rect.x + self.rect.w and \
                self.rect.y <= pos[1] <= self.rect.y + self.rect.h:
            return True
        return False

    def do(self):
        print("aboba")
        return self.name

    def __str__(self):
        return self.name


class Sector(pygame.sprite.Sprite):
    def __init__(self, x, y, xL, yL, groupName):
        super().__init__()
        self.x, self.y = x, y

        self.image = pygame.Surface((xL, yL))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.groupName = groupName
        fill = [0, 0, 0]
        if type(groupName) == list:
            fill = groupName
            self.groupName = 'F'
        pygame.draw.rect(self.image, fill, (TILESIZE // 4, TILESIZE // 4, xL - TILESIZE // 2, yL - TILESIZE // 2))
        self.image.set_colorkey((255, 255, 255))

    def update(self, direction_x_y: list, speed: float):  # передвигаемся
        self.x += speed * direction_x_y[0]
        self.y += speed * direction_x_y[1]
        self.rect.topleft = self.x, self.y

    def hurt(self, damage):  # получение урона
        print(self.groupName, "damaged", damage)
        return self.groupName, "damaged", damage

    def __str__(self):
        return self.groupName
