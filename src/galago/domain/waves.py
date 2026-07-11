import random

from ..constants import W
from .entities import Enemy

FORMATION_DROP = 22.0
FINAL_WAVE = 100
FINAL_BOSS_EXTRA_SIZE = 15  # además del tope normal de boss_size()
MINION_SPAWN_INTERVAL = 240  # 4s @60fps: cada cuánto el boss final invoca más refuerzos
MAX_MINIONS = 6  # tope de refuerzos vivos a la vez
INITIAL_MINIONS = 2  # refuerzos que ya están presentes desde el primer frame de la pelea
FINAL_BOSS_HP = 10  # el único enemigo del juego que no muere de un solo impacto


def make_enemies(wave: int) -> list[Enemy]:
    if is_boss_wave(wave):
        return _make_boss_wave(wave)
    if is_bonus_wave(wave):
        return _make_bonus_wave(wave)
    return _make_normal_wave()


def _make_normal_wave() -> list[Enemy]:
    layout = [('boss', 10), ('bee', 10), ('drone', 10), ('drone', 10)]
    return [Enemy(col, row, etype) for row, (etype, cols) in enumerate(layout) for col in range(cols)]


def _make_boss_wave(wave: int) -> list[Enemy]:
    boss = Enemy(0, 0, 'boss', size_override=boss_size(wave))
    boss.variant = boss_index(wave)
    boss.home_x = W / 2
    boss.x = float(boss.home_x)
    if not is_final_wave(wave):
        return [boss]

    boss.is_final = True
    boss.size += FINAL_BOSS_EXTRA_SIZE
    boss.hp = FINAL_BOSS_HP
    boss.max_hp = FINAL_BOSS_HP
    enemies = [boss]
    for _ in range(INITIAL_MINIONS):
        minion = make_minion()
        minion.start_swoop()
        enemies.append(minion)
    return enemies


def make_minion() -> Enemy:
    """Refuerzo (drone o bee) que el boss final invoca mientras sigue vivo."""
    etype = random.choice(('drone', 'bee'))
    minion = Enemy(0, 0, etype)
    minion.home_x = random.uniform(80, W - 80)
    minion.home_y = 60.0
    minion.x = float(minion.home_x)
    minion.y = float(minion.home_y)
    return minion


def _make_bonus_wave(wave: int) -> list[Enemy]:
    layout = [('drone', 8), ('bee', 8)]
    enemies = []
    for row, (etype, cols) in enumerate(layout):
        for col in range(cols):
            enemy = Enemy(col, row, etype)
            enemy.no_shoot = True
            enemies.append(enemy)
    return enemies


def is_bonus_wave(wave: int) -> bool:
    return wave % 10 == 5  # 5, 15, 25, ... 95


def is_boss_wave(wave: int) -> bool:
    return wave % 10 == 0  # 10, 20, 30, ... 100


def is_final_wave(wave: int) -> bool:
    return wave == FINAL_WAVE


def boss_index(wave: int) -> int:
    return wave // 10  # 1..10


def boss_size(wave: int) -> int:
    return 20 + boss_index(wave) * 3  # 23 (wave10) -> 50 (wave100)


def boss_bullet_speed(wave: int) -> int:
    return min(16, 8 + boss_index(wave))  # 9 (wave10) -> tope 16


def boss_swoop_interval(wave: int) -> int:
    return max(40, 150 - boss_index(wave) * 12)  # 138 (wave10) -> tope 40 (wave100)


def formation_speed(wave: int) -> float:
    return min(2.0, 0.5 + (wave - 1) * 0.22)


def bullet_speed(wave: int) -> int:
    return min(11, 7 + (wave - 1))


def initial_swoop_cooldown() -> int:
    return random.randint(160, 340)


def next_swoop_cooldown(wave: int) -> int:
    return max(70, random.randint(100, 280) - wave * 8)
