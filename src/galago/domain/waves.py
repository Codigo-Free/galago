import random

from .entities import Enemy

FORMATION_DROP = 22.0


def make_enemies():
    layout = [('boss', 10), ('bee', 10), ('drone', 10), ('drone', 10)]
    return [Enemy(col, row, etype) for row, (etype, cols) in enumerate(layout) for col in range(cols)]


def formation_speed(wave: int) -> float:
    return min(2.0, 0.5 + (wave - 1) * 0.22)


def bullet_speed(wave: int) -> int:
    return min(11, 7 + (wave - 1))


def initial_swoop_cooldown() -> int:
    return random.randint(160, 340)


def next_swoop_cooldown(wave: int) -> int:
    return max(70, random.randint(100, 280) - wave * 8)
