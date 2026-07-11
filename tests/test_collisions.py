from types import SimpleNamespace

from galago.domain.collisions import (
    enemy_bullet_hits_player,
    enemy_reached_bottom,
    player_bullet_hits_enemy,
)


def bullet(x, y):
    return SimpleNamespace(x=x, y=y)


def enemy(x=100.0, y=100.0, size=15, alive=True, swooping=False):
    return SimpleNamespace(x=x, y=y, size=size, alive=alive, swooping=swooping)


def player(x=100.0, y=100.0, is_dual=False):
    return SimpleNamespace(x=x, y=y, is_dual=is_dual)


def test_player_bullet_hits_enemy_within_radius():
    e = enemy(x=100, y=100, size=15)
    assert player_bullet_hits_enemy(bullet(105, 105), e) is True


def test_player_bullet_misses_enemy_outside_radius():
    e = enemy(x=100, y=100, size=15)
    assert player_bullet_hits_enemy(bullet(200, 200), e) is False


def test_player_bullet_never_hits_dead_enemy():
    e = enemy(x=100, y=100, size=15, alive=False)
    assert player_bullet_hits_enemy(bullet(100, 100), e) is False


def test_enemy_bullet_hits_single_ship_player():
    p = player(x=100, y=100, is_dual=False)
    assert enemy_bullet_hits_player(bullet(105, 105), p) is True
    assert enemy_bullet_hits_player(bullet(200, 200), p) is False


def test_enemy_bullet_hits_dual_ship_player_on_either_hitbox():
    p = player(x=100, y=100, is_dual=True)
    # cerca de la nave izquierda (x - 16)
    assert enemy_bullet_hits_player(bullet(84, 100), p) is True
    # cerca de la nave derecha (x + 16)
    assert enemy_bullet_hits_player(bullet(116, 100), p) is True
    # entre ambas naves, fuera de las dos hitboxes
    assert enemy_bullet_hits_player(bullet(100, 100), p) is False


def test_enemy_reached_bottom_only_when_alive_and_not_swooping():
    floor_y = 650.0
    assert enemy_reached_bottom(enemy(y=700, alive=True, swooping=False), floor_y) is True
    assert enemy_reached_bottom(enemy(y=700, alive=True, swooping=True), floor_y) is False
    assert enemy_reached_bottom(enemy(y=700, alive=False, swooping=False), floor_y) is False
    assert enemy_reached_bottom(enemy(y=600, alive=True, swooping=False), floor_y) is False
