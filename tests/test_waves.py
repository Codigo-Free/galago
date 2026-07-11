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
    enemies = waves.make_enemies(wave=1)
    assert len(enemies) == 40

    by_row = {}
    for e in enemies:
        row = round((e.home_y - 100) / 52)
        by_row.setdefault(row, []).append(e.etype)

    assert by_row[0] == ['boss'] * 10
    assert by_row[1] == ['bee'] * 10
    assert by_row[2] == ['drone'] * 10
    assert by_row[3] == ['drone'] * 10


def test_stage_type_predicates_across_full_range():
    for wave in range(1, 101):
        bonus = waves.is_bonus_wave(wave)
        boss = waves.is_boss_wave(wave)
        assert not (bonus and boss), f"wave {wave} no puede ser bono y boss a la vez"

    bonus_waves = [w for w in range(1, 101) if waves.is_bonus_wave(w)]
    boss_waves = [w for w in range(1, 101) if waves.is_boss_wave(w)]
    assert bonus_waves == [5, 15, 25, 35, 45, 55, 65, 75, 85, 95]
    assert boss_waves == [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


def test_final_wave_is_100_and_is_a_boss_wave():
    assert waves.is_final_wave(100) is True
    assert waves.is_final_wave(99) is False
    assert waves.is_boss_wave(100) is True


def test_boss_scaling_grows_with_each_appearance():
    assert waves.boss_index(10) == 1
    assert waves.boss_index(100) == 10

    assert waves.boss_size(10) == 23
    assert waves.boss_size(100) == 50
    assert waves.boss_size(100) > waves.boss_size(10)

    assert waves.boss_bullet_speed(10) == 9
    assert waves.boss_bullet_speed(100) == 16  # tope
    assert waves.boss_bullet_speed(100) >= waves.boss_bullet_speed(10)

    assert waves.boss_swoop_interval(10) == 138
    assert waves.boss_swoop_interval(100) == 40  # piso de 40 (150 - 10*12 = 30, se clampa a 40)
    assert waves.boss_swoop_interval(100) < waves.boss_swoop_interval(10)


def test_make_enemies_boss_wave_returns_single_scaled_boss():
    enemies = waves.make_enemies(wave=20)
    assert len(enemies) == 1
    boss = enemies[0]
    assert boss.etype == 'boss'
    assert boss.size == waves.boss_size(20)
    assert boss.is_final is False


def test_make_enemies_final_wave_returns_bigger_marked_final_boss():
    enemies = waves.make_enemies(wave=100)
    boss = enemies[0]
    assert boss.is_final is True
    assert boss.size == waves.boss_size(100) + waves.FINAL_BOSS_EXTRA_SIZE
    assert boss.size > waves.boss_size(90)  # mas grande que cualquier boss regular anterior


def test_make_enemies_bonus_wave_returns_non_shooting_enemies():
    enemies = waves.make_enemies(wave=5)
    assert len(enemies) == 16
    assert all(e.no_shoot for e in enemies)
    assert all(e.etype in ('drone', 'bee') for e in enemies)
