import pygame


class PygameClock:
    def __init__(self):
        self._clock = pygame.time.Clock()

    def tick(self, fps: int) -> None:
        self._clock.tick(fps)
