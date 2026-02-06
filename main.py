import pygame
import os
from events import event_check
from manager import Manager
from rendering import Rendering


def main():
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    windowTypes = {"resizable": pygame.RESIZABLE, "scaled": pygame.SCALED}
    with open(os.path.abspath("p_data\\nm.txt"), 'r', encoding="UTF8") as nm_par:
        windowType = nm_par.readline().lower().rstrip()
        windowRes = [int(i) for i in nm_par.readline().split()]
        screen = pygame.display.set_mode(windowRes, windowTypes[windowType])  # sssx, vsync=1
        pygame.display.set_caption(nm_par.readline().rstrip())
        pygame.display.set_icon(Rendering.load_texture(os.path.abspath("textures\\NM_icon.png")))

    vScreen = pygame.Surface(screen.get_size())
    manager = Manager(vScreen)
    screen = pygame.display.set_mode(manager.localSettings["resolution"], windowTypes[windowType])
    vScreen = pygame.transform.scale(vScreen, manager.localSettings["resolution"])
    manager.choose_resolution(vScreen, windowRes)

    pygame.key.set_repeat(500, 50)
    clock = pygame.time.Clock()
    fps = 24
    running = True
    while running:
        vScreen.fill((0, 0, 0))
        if manager.scene.show():
            if manager.scene.q[0][:3] == "lo&":
                manager.choose_scene(manager.scene.q[0][3:])
        for event in pygame.event.get():
            if event_check(manager, pygame.mouse.get_pos(), event) or event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                vScreen = pygame.transform.scale(vScreen, event.size)
                manager.choose_resolution(vScreen, windowRes)
        screen.blit(vScreen, (0, 0))
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()


if __name__ == "__main__":
    main()
