from galago.domain.leaderboard import InitialsEntry


def test_starts_with_default_letters_and_cursor_at_zero():
    entry = InitialsEntry()
    assert entry.letters == ['A', 'A', 'A']
    assert entry.cursor == 0
    assert entry.name == 'AAA'


def test_move_cursor_clamps_at_bounds():
    entry = InitialsEntry()

    entry.move_cursor(-1)  # ya está en 0, no debe bajar de ahí
    assert entry.cursor == 0

    entry.move_cursor(1)
    entry.move_cursor(1)
    assert entry.cursor == 2

    entry.move_cursor(1)  # ya está en 2, no debe subir de ahí
    assert entry.cursor == 2


def test_cycle_letter_wraps_around_forward():
    entry = InitialsEntry()
    for _ in range(26):  # una vuelta completa al alfabeto
        entry.cycle_letter(1)
    assert entry.letters[0] == 'A'


def test_cycle_letter_wraps_around_backward():
    entry = InitialsEntry()
    entry.cycle_letter(-1)
    assert entry.letters[0] == 'Z'


def test_cycle_letter_only_affects_letter_at_cursor():
    entry = InitialsEntry()
    entry.move_cursor(1)
    entry.cycle_letter(2)
    assert entry.letters == ['A', 'C', 'A']


def test_name_property_joins_letters():
    entry = InitialsEntry()
    entry.letters = ['J', 'A', 'M']
    assert entry.name == 'JAM'
