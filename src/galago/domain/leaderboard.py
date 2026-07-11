from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreEntry:
    name: str
    score: int
    date: str  # ISO, ej. "2026-07-11" — calculado por quien llama, no aquí


def qualifies(scores: list[ScoreEntry], score: int, top_n: int) -> bool:
    return len(scores) < top_n or score > scores[-1].score


def add_score(scores: list[ScoreEntry], name: str, score: int, today: str, top_n: int) -> list[ScoreEntry]:
    new_entry = ScoreEntry(name=name, score=score, date=today)
    updated = sorted(scores + [new_entry], key=lambda e: e.score, reverse=True)
    return updated[:top_n]


class InitialsEntry:
    def __init__(self):
        self.letters = ['A', 'A', 'A']
        self.cursor = 0

    def move_cursor(self, dx: int) -> None:
        self.cursor = max(0, min(2, self.cursor + dx))

    def cycle_letter(self, dy: int) -> None:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        current = alphabet.index(self.letters[self.cursor])
        self.letters[self.cursor] = alphabet[(current + dy) % len(alphabet)]

    @property
    def name(self) -> str:
        return ''.join(self.letters)