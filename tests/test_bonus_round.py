from galago.domain.entities import Bullet
from galago.domain.session import BONUS_DURATION, BonusRound
from galago.ports.input import InputState

IDLE = InputState()


def test_bonus_round_never_signals_dead():
    round_ = BonusRound(wave=5, score=0)
    for _ in range(BONUS_DURATION + 10):
        events, signal = round_.step(IDLE)
        assert signal != 'dead'
        if signal is not None:
            break


def test_bonus_round_ends_in_next_wave_after_duration():
    round_ = BonusRound(wave=5, score=0)
    signal = None
    for _ in range(BONUS_DURATION + 10):
        events, signal = round_.step(IDLE)
        if signal is not None:
            break
    assert signal == 'next_wave'


def test_bonus_round_never_decrements_lives():
    round_ = BonusRound(wave=5, score=0, lives=3)
    for _ in range(BONUS_DURATION + 10):
        events, signal = round_.step(IDLE)
        if signal is not None:
            break
    assert round_.player.lives == 3


def test_bonus_round_scores_points_on_hit():
    round_ = BonusRound(wave=5, score=0)
    round_.step(IDLE)  # lanza y avanza un frame al primer enemigo

    target = round_.enemies[0]
    round_.player.bullets.append(Bullet(target.x, target.y, -13, 'player'))

    round_._resolve_player_bullets()

    assert target.alive is False
    assert round_.player.score == target.pts
