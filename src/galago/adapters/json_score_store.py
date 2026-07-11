import json
from dataclasses import asdict
from pathlib import Path

from ..domain.leaderboard import ScoreEntry


class JsonScoreStore:
    def __init__(self, path: Path):
        self._path = path

    def load(self) -> list[ScoreEntry]:
        try:
            raw = json.loads(self._path.read_text())
        except (OSError, json.JSONDecodeError):
            return []
        return [ScoreEntry(**entry) for entry in raw]

    def save(self, scores: list[ScoreEntry]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(e) for e in scores]
        self._path.write_text(json.dumps(data, indent=2))
