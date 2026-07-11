from galago.domain.entities import Bullet
from galago.domain.session import GameRound
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
