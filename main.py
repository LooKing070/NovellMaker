import pygame
import os
from events import event_check
from manager import Manager
from rendering import Rendering


def main():
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    with open(os.path.abspath("p_data\\nm.txt"), 'r', encoding="UTF8") as nm_par:
        screen = pygame.display.set_mode([int(i) for i in nm_par.readline().split()], pygame.RESIZABLE)  # sssx, vsync=1
        pygame.display.set_caption(nm_par.readline().rstrip())
        pygame.display.set_icon(Rendering.load_texture(os.path.abspath("textures\\NM_icon.png")))

    vScreen = pygame.Surface((screen.get_width(), screen.get_height()))
    manager = Manager(vScreen)
    clock = pygame.time.Clock()
    fps = 60
    running = True
    while running:
        screen.fill((0, 0, 0))
        if manager.scene.show():
            manager.end_scene()
        for event in pygame.event.get():
            if event_check(manager, pygame.mouse.get_pos(), event) or event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()


if __name__ == "__main__":
    main()
