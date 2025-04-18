import pygame


def event_check(manager, mouse_x_y, event):  # если возвращает False, то приложение не закрывается
    mouse_x, mouse_y = mouse_x_y
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:  # Левая кнопка мыши
            manager.check_click((mouse_x, mouse_y), manager.scene.objects)
        elif event.button == 3:  # Правая кнопка мыши
            manager.check_click((mouse_x, mouse_y), manager.scene.objects)
        elif event.button == 2:  # Колесо мыши
            print("Колесо мыши было нажато")
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            if str(manager.scene) == "menu":
                return True
            manager.choose_scene()
        elif str(manager.scene) == "game":
            if pygame.key.name(event.key).isdigit():
                if 0 < int(pygame.key.name(event.key)) < 5:
                    manager.scene.player.hud.interaction_with_inventory("select", manager.scene.player.hud
                                                                .inventory[int(pygame.key.name(event.key)) - 1])
                    manager.scene.player.weapon_check()
            elif event.key == pygame.K_w:
                manager.scene.camera.moving = True
                manager.scene.camera.direction[1] = -1
            elif event.key == pygame.K_s:
                manager.scene.camera.moving = True
                manager.scene.camera.direction[1] = 1
            elif event.key == pygame.K_a:
                manager.scene.camera.moving = True
                manager.scene.camera.direction[0] = -1
            elif event.key == pygame.K_d:
                manager.scene.camera.moving = True
                manager.scene.camera.direction[0] = 1
        elif str(manager.scene) == "Pause":
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                manager.choose_scene()
    elif event.type == pygame.KEYUP:
        if str(manager.scene) == "Game":
            if event.key == event.key == pygame.K_w:
                manager.scene.camera.direction[1] = 0
            elif event.key == pygame.K_s:
                manager.scene.camera.direction[1] = 0
            elif event.key == pygame.K_a:
                manager.scene.camera.direction[0] = 0
            elif event.key == pygame.K_d:
                manager.scene.camera.direction[0] = 0
            if not any(manager.scene.camera.direction):
                manager.scene.camera.moving = False
    return False
