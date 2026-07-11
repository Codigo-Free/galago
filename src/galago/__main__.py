import sys

import pygame

from .adapters.pygame_adapter.audio import PygameAudioPlayer
from .adapters.pygame_adapter.clock import PygameClock
from .adapters.pygame_adapter.input import PygameInputProvider
from .adapters.pygame_adapter.intro import run_intro
from .adapters.pygame_adapter.renderer import PygameRenderer
from .app.loop import GameApp
from .constants import FPS, H, W


def main():
    """Composition root: crea pygame + los adaptadores concretos y arranca el juego."""
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

    # --- Easter egg intro (flashes + retrato) ---
    if not run_intro(surface, clock, FPS):
        pygame.quit()
        sys.exit()

    GameApp(renderer, input_provider, audio, clock, fps=FPS).run()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
