import array
import random

import pygame

from .intro import PROJECT_ROOT

class PygameAudioPlayer:
    """Motor de sonido 8-bit/Chiptune procedural (sin assets de audio)."""

    MUSIC_PATH = PROJECT_ROOT / "assets" / "sounds" / "freesound_community-8bit-music-for-game-68698.mp3"

    def play_music(self):
        if not pygame.mixer.get_init() or not self.MUSIC_PATH.exists():
            return
        try:
            pygame.mixer.music.load(str(self.MUSIC_PATH))
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(loops=-1)
        except Exception:
            pass

    def __init__(self):
        self._sfx: dict[str, "pygame.mixer.Sound | None"] = {}
        self._load()

    def _init_audio(self) -> bool:
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            return True
        except Exception:
            return False

    def _make_square_wave(self, freq, duration_sec, vol=0.3):
        if not pygame.mixer.get_init() or freq <= 0:
            return None
        sample_rate = 22050
        n_samples = int(sample_rate * duration_sec)
        buf = array.array('h')
        period = sample_rate / freq
        amp = int(32767 * min(max(vol, 0.0), 1.0))

        for i in range(n_samples):
            val = amp if (i % period) < (period / 2) else -amp
            val = int(val * (1.0 - (i / n_samples)))
            buf.append(val)

        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _make_noise(self, duration_sec, vol=0.4):
        if not pygame.mixer.get_init():
            return None
        sample_rate = 22050
        n_samples = int(sample_rate * duration_sec)
        buf = array.array('h')
        amp = int(32767 * min(max(vol, 0.0), 1.0))

        for i in range(n_samples):
            val = random.randint(-amp, amp)
            fade = (1.0 - (i / n_samples)) ** 2
            buf.append(int(val * fade))

        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _load(self):
        if not self._init_audio():
            return
        self._sfx['shoot'] = self._make_square_wave(880, 0.08, vol=0.25)
        self._sfx['shoot_dual'] = self._make_square_wave(660, 0.09, vol=0.3)
        self._sfx['enemy_shoot'] = self._make_square_wave(300, 0.08, vol=0.15)
        self._sfx['boom'] = self._make_noise(0.25, vol=0.35)
        self._sfx['player_boom'] = self._make_noise(0.6, vol=0.6)
        self._sfx['capture'] = self._make_square_wave(180, 0.4, vol=0.4)
        self._sfx['powerup'] = self._make_square_wave(1200, 0.3, vol=0.4)
        self._sfx['hit'] = self._make_square_wave(500, 0.05, vol=0.2)
        self._sfx['boss_death'] = self._make_noise(1.0, vol=0.7)

    def play(self, name: str) -> None:
        snd = self._sfx.get(name)
        if snd:
            snd.play()
