import argparse
import sys
from pathlib import Path

import pygame

from .adapters.json_score_store import JsonScoreStore
from .adapters.pygame_adapter.audio import PygameAudioPlayer
from .adapters.pygame_adapter.clock import PygameClock
from .adapters.pygame_adapter.input import PygameInputProvider
from .adapters.pygame_adapter.intro import run_intro
from .adapters.pygame_adapter.renderer import PygameRenderer
from .app.loop import GameApp
from .constants import FPS, H, W

SCORES_PATH = Path.home() / ".local" / "share" / "galago" / "scores.json"


def main():
    """Composition root: crea pygame + los adaptadores concretos y arranca el juego."""
    parser = argparse.ArgumentParser(description="Galago")
    parser.add_argument(
        "--wave", type=int, default=1,
        help="Stage inicial al arrancar una partida (util para probar bonos/boss sin jugar desde el 1)",
    )
    args = parser.parse_args()

    pygame.init()
    surface = pygame.display.set_mode((W, H))
    pygame.display.set_caption("HarnessOS — Galago")

    fonts = (
        pygame.font.SysFont("monospace", 52, bold=True),
        pygame.font.SysFont("monospace", 34, bold=True),
        pygame.font.SysFont("monospace", 20, bold=True),
    )

    clock = PygameClock()
    audio = PygameAudioPlayer()
    audio.play_music()
    renderer = PygameRenderer(surface, fonts)
    input_provider = PygameInputProvider()
    score_store = JsonScoreStore(SCORES_PATH)

    # --- Easter egg intro (flashes + retrato) ---
    if not run_intro(surface, clock, FPS):
        pygame.quit()
        sys.exit()

    GameApp(renderer, input_provider, audio, clock, score_store, fps=FPS, start_wave=args.wave).run()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
