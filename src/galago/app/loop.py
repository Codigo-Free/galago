from datetime import date

from ..constants import FPS
from ..domain.leaderboard import InitialsEntry, add_score, qualifies
from ..domain.session import GameRound
from ..ports.audio import AudioPlayer
from ..ports.clock import GameClock
from ..ports.input import InputProvider
from ..ports.renderer import Renderer
from ..ports.scores import ScoreStore


class GameApp:
    """Orquesta la máquina de estados de pantallas (título / oleada /
    jugando / game over) usando únicamente los puertos — no conoce pygame."""

    def __init__(self, renderer: Renderer, input_provider: InputProvider,
                 audio: AudioPlayer, clock: GameClock, score_store: ScoreStore,
                 fps: int = FPS, top_n: int = 10):
        self._renderer = renderer
        self._input = input_provider
        self._audio = audio
        self._clock = clock
        self._score_store = score_store
        self._fps = fps
        self._top_n = top_n
        self._scores = self._score_store.load()

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
                    if qualifies(self._scores, score, self._top_n):
                        name = self._screen_enter_initials(score)
                        if name is None:  # quit durante la captura de iniciales
                            return
                        self._scores = add_score(
                            self._scores, name, score, date.today().isoformat(), self._top_n,
                        )
                        self._score_store.save(self._scores)
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
            if inp.high_scores:
                self._screen_high_scores()
            self._renderer.render_title(t)
            self._clock.tick(self._fps)
            t += 1

    def _screen_high_scores(self) -> None:
        t = 0
        while True:
            inp = self._input.poll()
            if inp.quit or inp.enter:
                return
            self._renderer.render_high_scores(self._scores, t)
            self._clock.tick(self._fps)
            t += 1

    def _screen_enter_initials(self, score: int) -> str | None:
        entry = InitialsEntry()
        t = 0
        while True:
            inp = self._input.poll()
            if inp.quit:
                return None
            if inp.enter:
                return entry.name
            if inp.left:
                entry.move_cursor(-1)
            if inp.right:
                entry.move_cursor(1)
            if inp.up:
                entry.cycle_letter(1)
            if inp.down:
                entry.cycle_letter(-1)
            self._renderer.render_initials_entry(entry, score, t)
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
