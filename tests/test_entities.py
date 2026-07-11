from galago.domain import entities
from galago.domain.entities import Enemy


def test_no_shoot_enemy_never_appends_bullets():
    enemy = Enemy(0, 0, 'drone')
    enemy.no_shoot = True

    for _ in range(30):
        enemy.shoot_cd = 0  # fuerza el chequeo de disparo en cada frame
        enemy.update(fm_dx=0.0, fm_dy=0.0)

    assert enemy.bullets == []


def test_shooting_enemy_still_appends_bullets_when_not_no_shoot():
    enemy = Enemy(0, 0, 'drone')
    enemy.shoot_cd = 0

    events = enemy.update(fm_dx=0.0, fm_dy=0.0)

    assert len(enemy.bullets) == 1
    assert 'enemy_shoot' in events


def test_size_override_replaces_default_etype_size():
    default = Enemy(0, 0, 'boss')
    scaled = Enemy(0, 0, 'boss', size_override=50)

    assert scaled.size == 50
    assert scaled.pts == default.pts  # los puntos no cambian, solo el tamaño


def test_swoop_pattern_varies_by_variant(monkeypatch):
    monkeypatch.setattr(entities.random, "uniform", lambda a, b: a)
    monkeypatch.setattr(entities.random, "choice", lambda seq: seq[0])

    def p1_y_offset(variant):
        enemy = Enemy(0, 0, 'boss')
        enemy.variant = variant
        enemy.start_swoop()
        p0, p1, _, _ = enemy._bezier
        return p1[1] - p0[1]

    assert p1_y_offset(0) == 180  # patrón clásico (también el de enemigos normales, variant=0)
    assert p1_y_offset(1) == 140  # S ancha y rápida
    assert p1_y_offset(2) == 220  # picada angosta
    assert p1_y_offset(3) == 180  # variant % 3 vuelve a 0: el 3er boss repite el patrón clásico


def test_final_boss_picks_pattern_randomly_ignoring_variant(monkeypatch):
    monkeypatch.setattr(entities.random, "uniform", lambda a, b: a)
    monkeypatch.setattr(entities.random, "choice", lambda seq: seq[0])

    def p1_y_offset_with_forced_pick(forced_pattern):
        monkeypatch.setattr(entities.random, "randint", lambda a, b: forced_pattern)
        enemy = Enemy(0, 0, 'boss')
        enemy.variant = 7  # 7 % 3 == 1, pero is_final debe ignorar esto
        enemy.is_final = True
        enemy.start_swoop()
        p0, p1, _, _ = enemy._bezier
        return p1[1] - p0[1]

    # los 3 patrones deben quedar disponibles vía random.randint, sin
    # importar que `variant % 3` fijaría siempre el patrón 1
    assert p1_y_offset_with_forced_pick(0) == 180
    assert p1_y_offset_with_forced_pick(1) == 140
    assert p1_y_offset_with_forced_pick(2) == 220
