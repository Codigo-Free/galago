import pygame

from ...ports.input import InputState


class PygameInputProvider:
    def poll(self) -> InputState:
        quit_ = False
        enter = False
        space = False
        high_scores = False
        left = False
        right = False
        up = False
        down = False

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                quit_ = True
            elif ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_q):
                    quit_ = True
                elif ev.key == pygame.K_RETURN:
                    enter = True
                elif ev.key == pygame.K_SPACE:
                    space = True
                elif ev.key == pygame.K_h:
                    high_scores = True
                elif ev.key == pygame.K_LEFT:
                    left = True
                elif ev.key == pygame.K_RIGHT:
                    right = True
                elif ev.key == pygame.K_UP:
                    up = True
                elif ev.key == pygame.K_DOWN:
                    down = True

        keys = pygame.key.get_pressed()
        move = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move = 1
        shoot = bool(keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w])

        return InputState(
            quit=quit_, enter=enter, space=space, move=move, shoot=shoot,
            high_scores=high_scores, left=left, right=right, up=up, down=down,
        )
