from typing import Protocol

from ..domain.leaderboard import ScoreEntry


class ScoreStore(Protocol):
    def load(self) -> list[ScoreEntry]:
        ...

    def save(self, scores: list[ScoreEntry]) -> None:
        ...
