from galago.domain.leaderboard import ScoreEntry, add_score, qualifies


def make_scores():
    return [
        ScoreEntry(name='AAA', score=300, date='2026-07-01'),
        ScoreEntry(name='BBB', score=200, date='2026-07-02'),
        ScoreEntry(name='CCC', score=100, date='2026-07-03'),
    ]


def test_qualifies_when_list_not_full():
    assert qualifies([], score=1, top_n=3) is True
    assert qualifies(make_scores()[:2], score=1, top_n=3) is True


def test_qualifies_when_list_full():
    scores = make_scores()
    assert qualifies(scores, score=150, top_n=3) is True   # supera al último (100)
    assert qualifies(scores, score=100, top_n=3) is False  # empata, no supera
    assert qualifies(scores, score=50, top_n=3) is False   # menor que el último


def test_add_score_inserts_sorts_and_truncates():
    scores = make_scores()
    updated = add_score(scores, name='ZZZ', score=250, today='2026-07-11', top_n=3)

    assert [e.score for e in updated] == [300, 250, 200]
    assert updated[1].name == 'ZZZ'
    assert updated[1].date == '2026-07-11'


def test_add_score_does_not_mutate_original_list():
    scores = make_scores()
    original_len = len(scores)

    add_score(scores, name='ZZZ', score=250, today='2026-07-11', top_n=3)

    assert len(scores) == original_len
