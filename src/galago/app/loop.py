from ..constants import FPS
from ..domain.session import GameRound
from ..ports.audio import AudioPlayer
from ..ports.clock import GameClock
from ..ports.input import InputProvider
from ..ports.renderer import Renderer


class GameApp:
    """Orquesta la máquina de estados de pantallas (título / oleada /
    jugando / game over) usando únicamente los puertos — no conoce pygame."""

    def __init__(self, renderer: Renderer, input_provider: InputProvider,
                 audio: AudioPlayer, clock: GameClock, fps: int = FPS):
        self._renderer = renderer
        self._input = input_provider
        self._audio = audio
        self._clock = clock
        self._fps = fps

    def run(self) -> None:
        while True:
            if not self._screen_title():
                return

            wave, score, lives = 1, 0, 3
            while True:
                round_ = GameRound(wave=wave, score=score, lives=lives)
                signal = self._play_round(round_)
                score, lives = round_.player.score, round_.player.lives

                if signal == 'quit':
                    return
                elif signal == 'next_wave':
                    wave += 1
                    if not self._screen_wave_banner(wave):
                        return
                else:  # 'dead'
                    if not self._screen_gameover(score):
                        break  # vuelve a la pantalla de título
                    wave, score, lives = 1, 0, 3

    def _screen_title(self) -> bool:
        t = 0
        while True:
            inp = self._input.poll()
            if inp.quit:
                return False
            if inp.enter or inp.space:
                return True
            self._renderer.render_title(t)
            self._clock.tick(self._fps)
            t += 1

    def _screen_gameover(self, score: int) -> bool:
        t = 0
        while True:
            inp = self._input.poll()
            if inp.quit:
                return False
            if inp.enter:
                return True
            self._renderer.render_gameover(score, t)
            self._clock.tick(self._fps)
            t += 1

    def _screen_wave_banner(self, wave: int) -> bool:
        for _ in range(120):
            inp = self._input.poll()
            if inp.quit:
                return False
            self._renderer.render_wave_banner(wave)
            self._clock.tick(self._fps)
        return True

    def _play_round(self, round_: GameRound) -> str:
        while True:
            self._clock.tick(self._fps)
            inp = self._input.poll()
            events, signal = round_.step(inp)
            for name in events:
                self._audio.play(name)
            if signal is not None:
                return signal
            self._renderer.render_playing(round_)
