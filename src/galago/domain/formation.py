from ..constants import W
from .waves import FORMATION_DROP


class Formation:
    def __init__(self, speed: float, drop: float = FORMATION_DROP):
        self.dx = 0.0
        self.dy = 0.0
        self.dir = 1
        self.speed = speed
        self.drop = drop

    def update(self, enemies):
        alive_form = [e for e in enemies if e.alive and not e.swooping]
        if alive_form:
            xs = [e.home_x + self.dx for e in alive_form]
            if max(xs) >= W - 55 and self.dir == 1:
                self.dir = -1
                self.dy += self.drop
            elif min(xs) <= 55 and self.dir == -1:
                self.dir = 1
                self.dy += self.drop
        self.dx += self.speed * self.dir
