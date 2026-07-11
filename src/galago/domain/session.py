import random

from ..constants import H
from . import waves
from .capture import apply_capture_pull, check_beam_entry
from .collisions import (
    enemy_bullet_hits_player,
    enemy_reached_bottom,
    player_bullet_hits_enemy,
)
from .explosions import Explosion
from .formation import Formation
from .entities import Player

FLOOR_Y = H - 50


class GameRound:
    """Una partida (oleada en curso). Encapsula todas las reglas que antes
    vivían inline en run_game(): movimiento, formación, IA de ataque,
    colisiones, puntuación y condiciones de victoria/derrota."""

    def __init__(self, wave: int = 1, score: int = 0, lives: int = 3):
        self.wave = wave
        self.player = Player(score=score, lives=lives)
        self.enemies = waves.make_enemies(wave)
        self.formation = Formation(speed=waves.formation_speed(wave))
        if waves.is_boss_wave(wave):
            self.bullet_speed = waves.boss_bullet_speed(wave)
        else:
            self.bullet_speed = waves.bullet_speed(wave)
        self.swoop_cd = waves.initial_swoop_cooldown()
        self.explosions: list[Explosion] = []

    def step(self, input_state) -> tuple[list[str], str | None]:
        """Avanza un frame. Devuelve (eventos_de_sonido, señal) donde señal
        es None (continúa) | 'quit' | 'dead' | 'next_wave'."""
        events: list[str] = []

        if input_state.quit:
            return events, 'quit'

        # Poda las explosiones que ya terminaron de crecer en el frame
        # anterior (y que ya se dibujaron una última vez a tamaño máximo).
        self.explosions = [ex for ex in self.explosions if not ex.is_done]

        if input_state.shoot:
            events += self.player.shoot()

        if self.player.captured:
            if apply_capture_pull(self.player, self.enemies):
                return events, 'dead'
        else:
            self.player.update(input_state.move)

        self.formation.update(self.enemies)

        self.swoop_cd -= 1
        if self.swoop_cd <= 0:
            if waves.is_boss_wave(self.wave):
                self.swoop_cd = waves.boss_swoop_interval(self.wave)
            else:
                self.swoop_cd = waves.next_swoop_cooldown(self.wave)
            self._choose_attack()

        for e in self.enemies:
            events += e.update(self.formation.dx, self.formation.dy, bullet_speed=self.bullet_speed)

        check_beam_entry(self.player, self.enemies)

        events += self._resolve_player_bullets()
        events += self._resolve_enemy_bullets()

        for e in self.enemies:
            if enemy_reached_bottom(e, FLOOR_Y):
                self.player.lives = 0

        if self.player.lives <= 0:
            return events, 'dead'
        if all(not e.alive for e in self.enemies):
            return events, 'next_wave'

        for ex in self.explosions:
            ex.update()

        return events, None

    def _choose_attack(self):
        cands = [e for e in self.enemies if e.alive and not e.swooping]
        if not cands:
            return
        # 35% de probabilidad de que un Boss disponible intente el
        # secuestro cada vez que toca elegir ataque, en lugar de
        # depender de que la ruleta general elija primero un boss
        # entre todos los enemigos (lo hacía casi invisible).
        boss_cands = [e for e in cands if e.etype == 'boss' and not e.has_captured]
        if (boss_cands and not self.player.is_dual and not self.player.captured
                and random.random() < 0.35):
            random.choice(boss_cands).start_tractor_attack()
        else:
            random.choice(cands).start_swoop()

    def _resolve_player_bullets(self) -> list[str]:
        events: list[str] = []
        for pb in self.player.bullets[:]:
            for e in self.enemies:
                if player_bullet_hits_enemy(pb, e):
                    e.alive = False
                    self.player.score += e.pts

                    # ¡RESCATE DE LA NAVE SECUESTRADA!
                    if e.has_captured:
                        self.player.is_dual = True
                        events.append('powerup')
                        self.explosions.append(Explosion(int(e.x), int(e.y), 10.0, 70.0, 'rescue'))
                    else:
                        events.append('boom')

                    if pb in self.player.bullets:
                        self.player.bullets.remove(pb)
                    self.explosions.append(Explosion(int(e.x), int(e.y), 4.0, 32.0, e.etype))
                    break
        return events

    def _resolve_enemy_bullets(self) -> list[str]:
        events: list[str] = []
        for e in self.enemies:
            for b in e.bullets[:]:
                if enemy_bullet_hits_player(b, self.player) and self.player.hit():
                    events.append('player_boom')
                    e.bullets.remove(b)
                    self.explosions.append(
                        Explosion(int(self.player.x), int(self.player.y), 4.0, 50.0, 'player_hit')
                    )
        return events


BONUS_DURATION = 600        # 10s @ 60fps
BONUS_SPAWN_INTERVAL = 20   # frames entre cada enemigo lanzado


class BonusRound:
    """Etapa de bono estilo Galaga clásico: los enemigos vuelan en oleadas,
    nunca disparan y no pueden matar al jugador. Suma puntos por cada uno
    que se le pegue y siempre termina en 'next_wave' (nunca 'dead')."""

    def __init__(self, wave: int, score: int = 0, lives: int = 3):
        self.wave = wave
        self.player = Player(score=score, lives=lives)
        self._pending = waves.make_enemies(wave)  # todavía no lanzados
        self.enemies: list = []                    # ya lanzados / en vuelo
        self.explosions: list[Explosion] = []
        self._t = 0

    def step(self, input_state) -> tuple[list[str], str | None]:
        events: list[str] = []

        if input_state.quit:
            return events, 'quit'

        self.explosions = [ex for ex in self.explosions if not ex.is_done]

        if input_state.shoot:
            events += self.player.shoot()
        self.player.update(input_state.move)

        if self._t % BONUS_SPAWN_INTERVAL == 0 and self._pending:
            enemy = self._pending.pop(0)
            enemy.start_swoop()
            self.enemies.append(enemy)

        for e in self.enemies:
            events += e.update(0.0, 0.0)
            if e.alive and not e.swooping:
                e.start_swoop()  # relanza otra pasada mientras dure el bono

        events += self._resolve_player_bullets()

        self.enemies = [e for e in self.enemies if e.alive]

        self._t += 1
        finished_all = not self._pending and not self.enemies
        if self._t >= BONUS_DURATION or finished_all:
            return events, 'next_wave'

        for ex in self.explosions:
            ex.update()

        return events, None

    def _resolve_player_bullets(self) -> list[str]:
        events: list[str] = []
        for pb in self.player.bullets[:]:
            for e in self.enemies:
                if player_bullet_hits_enemy(pb, e):
                    e.alive = False
                    self.player.score += e.pts
                    events.append('boom')
                    if pb in self.player.bullets:
                        self.player.bullets.remove(pb)
                    self.explosions.append(Explosion(int(e.x), int(e.y), 4.0, 32.0, e.etype))
                    break
        return events
