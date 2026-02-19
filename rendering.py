import os
import pygame
import json
import av
from typing import Tuple, List, Optional


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

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)


class TextPlane(pygame.sprite.Sprite):
    _GLOBAL_CHAR_CACHE = {}  # Глобальный кэш символов: {(шрифт, символ, цвет): поверхность}

    def __init__(self, texture: pygame.Surface, font: pygame.font.Font,  transparency: int = 255,
                 x0: int = 0, y0: int = 0, size: float = 1.0, padding: int = 15,
                 line_spacing: int = 8, color: Tuple[int, int, int] = (0, 0, 0), alignment: str = 'left',
                 animationDelay: int = 40, mode: str = "char"):
        """
        :param sprite: фоновая поверхность (прямоугольный спрайт)
        :param font: шрифт Pygame для рендеринга текста
        :param color: цвет текста (R, G, B)
        :param padding: отступы текста от краёв спрайта
        :param line_spacing: дополнительный интервал между строками
        :param alignment: выравнивание текста внутри спрайта
        """
        super().__init__()
        self.image = texture
        self._sizeCo = size
        self._savedImage = texture
        self.transparency = transparency
        self.rect = self.image.get_rect()
        self.rect.topleft = (x0, y0)

        self.font = font
        self.color = color
        self.padding = padding
        self.line_spacing = line_spacing
        self.alignment = alignment  # 'left', 'center', 'right'

        self.text = ""
        self.displayed_chars = 0  # количество отображённых символов
        self.mode = mode  # 'char' или 'word'
        self.word_boundaries: List[int] = []  # индексы окончаний слов
        self.animationTimer, self.animationDelay = 0, animationDelay

        self._line_layouts: List[List[Tuple[str, int, int]]] = []  # [(символ, x, y), ...]
        self._total_chars = 0

    def set_text(self, text: str, mode: str = 'char') -> None:
        self.text = text
        self.mode = mode
        self.displayed_chars = 0
        # Разбивка на строки с учётом ширины спрайта
        self._line_layouts = self._layout_text(text)
        self._total_chars = sum(len(line) for line in self._line_layouts)
        # Вычисление границ слов для пословного режима
        self.word_boundaries = self._calculate_word_boundaries()

    def _layout_text(self, text: str) -> List[List[Tuple[str, int, int]]]:
        """
        Разбивает текст на строки с позициями символов.
        Возвращает список строк, где каждая строка — список (символ, x, y).
        """
        max_width = self.image.get_width() - 2 * self.padding
        lines = []
        y_offset = self.padding
        paragraphs = text.split('\n')

        for paragraph in paragraphs:
            words = paragraph.split(' ')
            current_line = []
            current_width = 0

            for i, word in enumerate(words):
                # Рендерим слово целиком для измерения ширины
                word_with_space = word + (' ' if i < len(words) - 1 else '')
                word_surf = self.font.render(word_with_space, True, self.color)
                word_width = word_surf.get_width()
                # Проверяем, влезает ли слово в текущую строку
                if current_width + word_width > max_width and current_line:
                    # Формируем строку и начинаем новую
                    lines.append(self._build_line(current_line, y_offset))
                    y_offset += self.font.get_height() + self.line_spacing
                    current_line = []
                    current_width = 0
                # Добавляем символы слова в буфер строки
                for char in word_with_space:
                    current_line.append(char)
                    current_width += self._get_char_width(char)

            if current_line:
                lines.append(self._build_line(current_line, y_offset))
                y_offset += self.font.get_height() + self.line_spacing

        return lines

    def _build_line(self, chars: List[str], y: int) -> List[Tuple[str, int, int]]:
        """Собирает строку с координатами для каждого символа"""
        line = []
        x = self.padding
        for char in chars:
            line.append((char, x, y))
            x += self._get_char_width(char)
        if self.alignment == 'center':
            total_width = sum(self._get_char_width(c) for c in chars)
            offset = (self.image.get_width() - total_width) // 2 - self.padding
            line = [(c, x + offset, y) for (c, x, y) in line]
        elif self.alignment == 'right':
            total_width = sum(self._get_char_width(c) for c in chars)
            offset = (self.image.get_width() - 2 * self.padding) - total_width
            line = [(c, x + offset, y) for (c, x, y) in line]
        return line

    def _calculate_word_boundaries(self) -> List[int]:
        """Вычисляет индексы символов, на которых заканчиваются слова"""
        boundaries = []
        char_index = 0
        for line in self._line_layouts:
            line_text = ''.join(c for c, _, _ in line)
            in_word = False
            for i, char in enumerate(line_text):
                is_word_char = char.isalnum() or char in "'-"
                if is_word_char and not in_word:
                    in_word = True
                elif not is_word_char and in_word:
                    in_word = False
                    boundaries.append(char_index + i)  # конец слова
            if in_word:  # Последнее слово в строке
                boundaries.append(char_index + len(line_text))
            char_index += len(line_text)
        return boundaries

    def _get_char_width(self, char: str) -> int:
        """Возвращает ширину символа через кэш метрик шрифта"""
        metrics = self.font.metrics(char)
        if metrics and metrics[0]:
            return metrics[0][4]  # advance width
        return self.font.size(char)[0]

    def _get_cached_char(self, char: str) -> pygame.Surface:
        # Ключ кэша: (идентификатор шрифта, символ, цвет)
        # id(font) так как объекты шрифта не хэшируются напрямую
        cache_key = (id(self.font), char, self.color)
        if cache_key not in self._GLOBAL_CHAR_CACHE:
            surf = self.font.render(char, True, self.color)
            self._GLOBAL_CHAR_CACHE[cache_key] = surf
        return self._GLOBAL_CHAR_CACHE[cache_key]

    @classmethod
    def clear_cache(cls) -> None:
        cls._GLOBAL_CHAR_CACHE.clear()

    def do_anim(self) -> bool:  # return: True если анимация ещё не завершена, False если текст полностью отображён
        runAnim = self.displayed_chars >= self._total_chars
        if not runAnim and pygame.time.get_ticks() >= self.animationTimer:
            if self.mode == 'char':
                self.displayed_chars += 1
            else:  # word mode
                next_boundary = next((b for b in self.word_boundaries if b > self.displayed_chars), self._total_chars)
                self.displayed_chars = next_boundary
            self.animationTimer = pygame.time.get_ticks() + self.animationDelay
        if runAnim:
            pygame.time.set_timer(self.animationTimer, 0)
        return runAnim

    def reset(self) -> None:
        self.displayed_chars = 0

    def draw(self, surface: pygame.Surface) -> None:
        # 1. Отрисовываем фоновый спрайт
        surface.blit(self.image, self.rect.topleft)
        # 2. Отрисовываем текст по кэшированным позициям
        drawn_chars = 0
        px, py = self.rect.topleft
        for line in self._line_layouts:
            if drawn_chars >= self.displayed_chars:
                break
            for char, rel_x, rel_y in line:
                if drawn_chars >= self.displayed_chars:
                    break
                char_surf = self._get_cached_char(char)
                surface.blit(char_surf, (px + rel_x, py + rel_y))
                drawn_chars += 1

    def get_progress(self) -> float:  # return: 0-100%
        return min(1.0, self.displayed_chars / max(1, self._total_chars))


class Fon(AnimatedSprite):
    def __init__(self, textureParameters):
        super().__init__(*textureParameters)

    def update(self, size=()):
        if size:
            self.resize(size[0], size[1])

