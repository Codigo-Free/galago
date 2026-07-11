#!/usr/bin/env python3
"""HarnessOS Easter Egg — Galago (entry point)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from galago.__main__ import main  # noqa: E402

if __name__ == "__main__":
    main()
