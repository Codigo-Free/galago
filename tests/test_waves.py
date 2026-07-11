from galago.domain import waves


def test_formation_speed_scales_then_caps():
    assert waves.formation_speed(1) == 0.5
    assert waves.formation_speed(7) < 2.0
    assert waves.formation_speed(8) == 2.0
    assert waves.formation_speed(20) == 2.0


def test_bullet_speed_scales_then_caps():
    assert waves.bullet_speed(1) == 7
    assert waves.bullet_speed(5) == 11
    assert waves.bullet_speed(10) == 11


def test_initial_swoop_cooldown_within_expected_range():
    for _ in range(50):
        value = waves.initial_swoop_cooldown()
        assert 160 <= value <= 340


def test_next_swoop_cooldown_uses_wave_scaled_random_with_floor(monkeypatch):
    monkeypatch.setattr(waves.random, "randint", lambda a, b: 200)
    assert waves.next_swoop_cooldown(wave=1) == 192  # 200 - 1*8
    assert waves.next_swoop_cooldown(wave=20) == 70  # 200 - 160 -> floor de 70


def test_make_enemies_layout():
    enemies = waves.make_enemies()
    assert len(enemies) == 40

    by_row = {}
    for e in enemies:
        row = round((e.home_y - 100) / 52)
        by_row.setdefault(row, []).append(e.etype)

    assert by_row[0] == ['boss'] * 10
    assert by_row[1] == ['bee'] * 10
    assert by_row[2] == ['drone'] * 10
    assert by_row[3] == ['drone'] * 10
