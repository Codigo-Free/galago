from typing import Protocol


class AudioPlayer(Protocol):
    def play(self, name: str) -> None:
        ...

    def play_music(self) -> None:
        ...