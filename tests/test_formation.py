from types import SimpleNamespace

from galago.constants import W
from galago.domain.formation import Formation


def make_enemy(home_x, alive=True, swooping=False):
    return SimpleNamespace(home_x=home_x, alive=alive, swooping=swooping)


def test_formation_moves_without_bouncing_when_far_from_edges():
    f = Formation(speed=2.0, drop=22.0)
    enemies = [make_enemy(W / 2)]
    f.update(enemies)
    assert f.dx == 2.0
    assert f.dir == 1
    assert f.dy == 0.0


def test_formation_bounces_and_drops_at_right_edge():
    f = Formation(speed=2.0, drop=22.0)
    f.dx = W - 55  # exactamente en el umbral de rebote
    enemies = [make_enemy(0.0)]  # home_x=0 -> x = 0 + dx = W-55
    f.update(enemies)
    assert f.dir == -1
    assert f.dy == 22.0


def test_formation_bounces_and_drops_at_left_edge():
    f = Formation(speed=2.0, drop=22.0)
    f.dir = -1
    f.dx = -(0 - 55)  # dx tal que home_x + dx == 55
    enemies = [make_enemy(0.0)]
    f.update(enemies)
    assert f.dir == 1
    assert f.dy == 22.0


def test_formation_ignores_dead_and_swooping_enemies():
    f = Formation(speed=2.0, drop=22.0)
    enemies = [
        make_enemy(W, alive=False),
        make_enemy(W, alive=True, swooping=True),
    ]
    f.update(enemies)
    # sin enemigos "en formación" activos, no debe rebotar aunque sus
    # posiciones nominales estén fuera de los límites
    assert f.dir == 1
    assert f.dy == 0.0
