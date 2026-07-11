from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ..domain.leaderboard import InitialsEntry, ScoreEntry
    from ..domain.session import BonusRound, GameRound


class Renderer(Protocol):
    def render_title(self, t: int) -> None:
        ...

    def render_wave_banner(self, wave: int, label: "str | None" = None) -> None:
        ...

    def render_gameover(self, score: int, t: int) -> None:
        ...

    def render_victory(self, score: int, t: int) -> None:
        ...

    def render_playing(self, round_: "GameRound | BonusRound") -> None:
        ...

    def render_high_scores(self, scores: "list[ScoreEntry]", t: int) -> None:
        ...

    def render_initials_entry(self, entry: "InitialsEntry", score: int, t: int) -> None:
        ...
