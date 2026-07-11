from galago.constants import H, W
from galago.domain.capture import apply_capture_pull, check_beam_entry
from galago.domain.entities import Enemy, Player


def make_boss(x=100.0, y=100.0, tractor_state=0):
    boss = Enemy(col=0, row=0, etype='boss')
    boss.x, boss.y = x, y
    boss.tractor_state = tractor_state
    return boss


def test_apply_capture_pull_noop_when_player_not_captured():
    player = Player()
    boss = make_boss(tractor_state=1)
    game_over = apply_capture_pull(player, [boss])
    assert game_over is False
    assert boss.has_captured is False


def test_apply_capture_pull_eases_player_toward_beaming_enemy():
    player = Player()
    player.captured = True
    player.x, player.y = 0.0, 0.0
    boss = make_boss(x=100.0, y=100.0, tractor_state=2)

    apply_capture_pull(player, [boss])

    # se acerca un 8% de la distancia, pero no llega a menos de 30px todavia
    assert player.x == 8.0
    assert player.y == 8.0
    assert player.captured is True
    assert boss.has_captured is False


def test_apply_capture_pull_finalizes_when_close_enough():
    player = Player()
    player.captured = True
    player.lives = 3
    boss = make_boss(x=0.0, y=0.0, tractor_state=2)
    player.x, player.y = 1.0, 1.0  # a menos de 30px del boss

    game_over = apply_capture_pull(player, [boss])

    assert boss.has_captured is True
    assert boss.tractor_state == 3
    assert player.captured is False
    assert player.lives == 2
    assert player.inv == 180
    assert (player.x, player.y) == (float(W // 2), float(H - 75))
    assert game_over is False


def test_apply_capture_pull_signals_game_over_at_zero_lives():
    player = Player()
    player.captured = True
    player.lives = 1
    boss = make_boss(x=0.0, y=0.0, tractor_state=2)
    player.x, player.y = 1.0, 1.0

    game_over = apply_capture_pull(player, [boss])

    assert player.lives == 0
    assert game_over is True


def test_check_beam_entry_captures_player_inside_beam():
    player = Player()
    player.inv = 0
    boss = make_boss(x=100.0, y=100.0, tractor_state=2)
    player.x, player.y = 120.0, 130.0  # dentro del cono del rayo

    check_beam_entry(player, [boss])

    assert player.captured is True


def test_check_beam_entry_ignores_player_outside_beam_bounds():
    player = Player()
    player.inv = 0
    boss = make_boss(x=100.0, y=100.0, tractor_state=2)
    player.x, player.y = 300.0, 130.0  # fuera del ancho del rayo

    check_beam_entry(player, [boss])

    assert player.captured is False


def test_check_beam_entry_skips_when_player_invincible_or_dual():
    boss = make_boss(x=100.0, y=100.0, tractor_state=2)

    player = Player()
    player.inv = 10
    player.x, player.y = 120.0, 130.0
    check_beam_entry(player, [boss])
    assert player.captured is False

    player2 = Player()
    player2.is_dual = True
    player2.x, player2.y = 120.0, 130.0
    check_beam_entry(player2, [boss])
    assert player2.captured is False
