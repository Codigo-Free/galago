from typing import Protocol


class GameClock(Protocol):
    def tick(self, fps: int) -> None:
        ...
