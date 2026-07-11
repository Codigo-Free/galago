from galago.domain import waves
from galago.domain.entities import Bullet
from galago.domain.session import BOSS_DEATH_SEQUENCE_FRAMES, GameRound
from galago.ports.input import InputState

IDLE = InputState()


def test_quit_signal_propagates_immediately():
    round_ = GameRound()
    events, signal = round_.step(InputState(quit=True))
    assert signal == 'quit'
    assert events == []


def test_player_bullet_kills_enemy_and_scores_points():
    round_ = GameRound()
    target = round_.enemies[0]
    round_.player.bullets.append(Bullet(target.x, target.y, -13, 'player'))

    events, signal = round_.step(IDLE)

    assert target.alive is False
    assert round_.player.score == target.pts
    assert 'boom' in events
    assert signal is None


def test_next_wave_signal_when_all_enemies_dead():
    round_ = GameRound()
    for e in round_.enemies:
        e.alive = False

    events, signal = round_.step(IDLE)

    assert signal == 'next_wave'


def test_dead_signal_when_enemy_reaches_bottom():
    round_ = GameRound()
    round_.player.lives = 3
    # Simula que la formación ya descendió muy por debajo del suelo tras
    # muchos rebotes; los enemigos "en formación" (vivos, sin swoop) siguen
    # esa posición en Enemy.update(), así que hay que mover la formación,
    # no el enemigo directamente (su y se recalcula cada frame).
    round_.formation.dy = 10_000.0

    events, signal = round_.step(IDLE)

    assert signal == 'dead'
    assert round_.player.lives == 0


def test_final_boss_spawns_minions_over_time():
    round_ = GameRound(wave=100)
    for _ in range(waves.MINION_SPAWN_INTERVAL):
        events, signal = round_.step(IDLE)
        if signal is not None:
            break

    assert len(round_.enemies) > 1  # el boss más al menos un refuerzo
    assert any(not e.is_final for e in round_.enemies)


def test_minion_spawning_caps_at_max():
    round_ = GameRound(wave=100)
    for _ in range(waves.MINION_SPAWN_INTERVAL * (waves.MAX_MINIONS + 3)):
        events, signal = round_.step(IDLE)
        if signal is not None:
            break

    active_minions = sum(1 for e in round_.enemies if not e.is_final and e.alive)
    assert active_minions <= waves.MAX_MINIONS


def test_minion_spawning_stops_once_boss_is_dead():
    round_ = GameRound(wave=100)
    # deja pasar suficientes frames para que se invoque al menos un refuerzo
    for _ in range(waves.MINION_SPAWN_INTERVAL + 5):
        events, signal = round_.step(IDLE)
        if signal is not None:
            break
    assert len(round_.enemies) > 1  # confirma que sí llegó a invocar

    boss = next(e for e in round_.enemies if e.is_final)
    boss.alive = False
    enemy_count_at_boss_death = len(round_.enemies)

    # con el refuerzo aún vivo el round sigue (no todos están muertos),
    # así que esto sí ejercita varios ciclos más de _maybe_spawn_minion
    for _ in range(waves.MINION_SPAWN_INTERVAL * 2):
        events, signal = round_.step(IDLE)
        if signal is not None:
            break

    assert len(round_.enemies) == enemy_count_at_boss_death  # ningún refuerzo nuevo tras la muerte del boss


def test_regular_boss_wave_never_spawns_minions():
    round_ = GameRound(wave=10)
    for _ in range(waves.MINION_SPAWN_INTERVAL * 2):
        events, signal = round_.step(IDLE)
        if signal is not None:
            break

    assert len(round_.enemies) == 1


def test_final_boss_survives_a_single_hit():
    round_ = GameRound(wave=100)
    boss = next(e for e in round_.enemies if e.is_final)
    round_.enemies = [boss]  # aisla del test a los refuerzos (posiciones al azar)
    round_.player.bullets.append(Bullet(boss.x, boss.y, -13, 'player'))

    events, signal = round_.step(IDLE)

    assert boss.alive is True
    assert boss.hp == waves.FINAL_BOSS_HP - 1
    assert round_.player.score == 0
    assert 'hit' in events
    assert signal is None


def test_final_boss_dies_after_enough_hits_and_scores_once():
    round_ = GameRound(wave=100)
    boss = next(e for e in round_.enemies if e.is_final)
    round_.enemies = [boss]

    for _ in range(waves.FINAL_BOSS_HP):
        round_.player.bullets.append(Bullet(boss.x, boss.y, -13, 'player'))
        round_.step(IDLE)

    assert boss.alive is False
    assert boss.hp <= 0
    assert round_.player.score == boss.pts  # sumó los puntos una sola vez, al morir


def test_final_boss_death_clears_remaining_minions_and_credits_score():
    round_ = GameRound(wave=100)
    boss = next(e for e in round_.enemies if e.is_final)
    minions = [e for e in round_.enemies if not e.is_final]
    assert minions  # confirma que arrancó con refuerzos (INITIAL_MINIONS)

    boss.hp = 1  # el próximo golpe lo mata
    round_.player.bullets.append(Bullet(boss.x, boss.y, -13, 'player'))

    events, signal = round_.step(IDLE)

    assert boss.alive is False
    assert all(not m.alive for m in minions)
    expected_score = boss.pts + sum(m.pts for m in minions)
    assert round_.player.score == expected_score
    assert 'boss_death' in events
    assert round_.screen_flash > 0.9  # se dispara al máximo, ya empezó a decaer este mismo frame


def test_final_boss_death_delays_next_wave_signal():
    round_ = GameRound(wave=100)
    boss = next(e for e in round_.enemies if e.is_final)
    round_.enemies = [boss]  # aisla del test a los refuerzos
    boss.hp = 1
    round_.player.bullets.append(Bullet(boss.x, boss.y, -13, 'player'))

    events, signal = round_.step(IDLE)
    assert signal is None  # golpe final: hay respiro antes de avisar next_wave

    signal = None
    for _ in range(BOSS_DEATH_SEQUENCE_FRAMES + 5):
        events, signal = round_.step(IDLE)
        if signal is not None:
            break

    assert signal == 'next_wave'
