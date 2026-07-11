import random

from ..constants import W, H
from .math_utils import bezier_point

ETYPE_STATS = {
    # etype: (points, size)
    'drone': (10, 13),
    'bee':   (20, 15),
    'boss':  (50, 20),
}


class Bullet:
    def __init__(self, x, y, vy, owner):
        self.x = x
        self.y = float(y)
        self.vy = vy
        self.owner = owner  # 'player' | 'enemy'

    def update(self):
        self.y += self.vy


class Enemy:
    def __init__(self, col, row, etype, size_override: int | None = None):
        self.etype = etype
        self.pts, self.size = ETYPE_STATS[etype]
        if size_override is not None:
            self.size = size_override
        self.home_x = 90 + col * 66
        self.home_y = 100 + row * 52
        self.x = float(self.home_x)
        self.y = float(self.home_y)
        self.alive = True
        self.bullets: list[Bullet] = []
        self.swooping = False
        self.no_shoot = False  # True en etapas de bono: nunca dispara
        self.variant = 0  # 1..10 en bosses sucesivos: varía apariencia y patrón de vuelo
        self.is_final = False  # True solo en el boss del stage 100: look único + vuelo aleatorio
        self.hp = 1       # todos mueren de un impacto salvo que algo suba esto (ej. boss final)
        self.max_hp = 1
        self._phase = 0.0
        self._ox = self._oy = 0.0
        self._bezier: tuple | None = None
        self.shoot_cd = random.randint(120, 500)

        # --- Variables del Rayo Tractor ---
        self.has_captured = False
        self.tractor_state = 0  # 0: Normal, 1: Bajando, 2: Emitiendo, 3: Volviendo
        self.beam_timer = 0

    @property
    def is_beaming(self) -> bool:
        return self.tractor_state == 2

    def start_swoop(self):
        if not self.swooping and self.tractor_state == 0:
            self.swooping = True
            self._phase = 0.0
            self._ox = self.x
            self._oy = self.y

            # El patrón de vuelo varía con `variant` (0 para enemigos normales;
            # 1..10 para cada boss sucesivo) para que cada boss se sienta distinto.
            # El boss final (`is_final`) elige un patrón al azar en cada
            # picada, en vez de uno fijo — vuelo impredecible.
            pattern = random.randint(0, 2) if self.is_final else self.variant % 3
            if pattern == 1:
                sway_range, p1_y, p2_y = (220, 380), 140, 340   # S ancha y rápida
            elif pattern == 2:
                sway_range, p1_y, p2_y = (40, 100), 220, 420    # picada angosta y directa
            else:
                sway_range, p1_y, p2_y = (120, 220), 180, 380   # patrón clásico

            sway = random.uniform(*sway_range) * random.choice((-1, 1))
            p0 = (self.x, self.y)
            p1 = (self.x + sway, self.y + p1_y)
            p2 = (self.x - sway * 0.6, self.y + p2_y)
            p3 = (self.x + random.uniform(-40, 40), H + 60)
            self._bezier = (p0, p1, p2, p3)

    def start_tractor_attack(self):
        if not self.swooping and self.etype == 'boss' and self.tractor_state == 0:
            self.swooping = True
            self.tractor_state = 1
            self._ox = self.x
            self._oy = self.y

    def update(self, fm_dx, fm_dy, bullet_speed=7) -> list[str]:
        events: list[str] = []

        if self.swooping and self.tractor_state > 0:
            # --- LÓGICA DE SECUESTRO DEL BOSS ---
            if self.tractor_state == 1:  # Bajando al punto de disparo
                self.y += 3.5
                if self.y >= H - 280:
                    self.tractor_state = 2
                    self.beam_timer = 120  # 2 segundos emitiendo luz
                    events.append('capture')

            elif self.tractor_state == 2:  # Emitiendo rayo tractor
                self.beam_timer -= 1
                if self.beam_timer <= 0:
                    self.tractor_state = 3

            elif self.tractor_state == 3:  # Volviendo con o sin la nave
                dx = (self.home_x + fm_dx) - self.x
                dy = (self.home_y + fm_dy) - self.y
                self.x += dx * 0.05
                self.y += dy * 0.05
                if abs(dx) < 3 and abs(dy) < 3:
                    self.swooping = False
                    self.tractor_state = 0
                    self.x = self.home_x + fm_dx
                    self.y = self.home_y + fm_dy

        elif self.swooping:
            self._phase += 0.008
            if self._phase >= 1.0 or self._bezier is None:
                self.swooping = False
                self._bezier = None
                self.x = self.home_x + fm_dx
                self.y = self.home_y + fm_dy
            else:
                p0, p1, p2, p3 = self._bezier
                self.x, self.y = bezier_point(p0, p1, p2, p3, self._phase)
        else:
            self.x = self.home_x + fm_dx
            self.y = self.home_y + fm_dy

        self.shoot_cd -= 1
        if self.shoot_cd <= 0:
            self.shoot_cd = random.randint(200, 600)
            if self.alive and self.tractor_state == 0 and not self.no_shoot:
                self.bullets.append(Bullet(int(self.x), int(self.y) + 12, bullet_speed, 'enemy'))
                events.append('enemy_shoot')

        for b in self.bullets[:]:
            b.update()
            if b.y > H + 20:
                self.bullets.remove(b)

        return events


class Player:
    def __init__(self, score=0, lives=3):
        self.x = float(W // 2)
        self.y = float(H - 75)
        self.speed = 5.5
        self.bullets: list[Bullet] = []
        self.shoot_cd = 0
        self.score = score
        self.lives = lives
        self.inv = 0
        self.is_dual = False
        self.captured = False  # Para animación de secuestro

    def shoot(self) -> list[str]:
        if self.shoot_cd <= 0 and not self.captured:
            if self.is_dual:
                self.bullets.append(Bullet(int(self.x) - 16, int(self.y) - 22, -13, 'player'))
                self.bullets.append(Bullet(int(self.x) + 16, int(self.y) - 22, -13, 'player'))
                event = 'shoot_dual'
            else:
                self.bullets.append(Bullet(int(self.x), int(self.y) - 22, -13, 'player'))
                event = 'shoot'
            self.shoot_cd = 14
            return [event]
        return []

    def hit(self) -> bool:
        if self.inv == 0 and not self.captured:
            if self.is_dual:
                self.is_dual = False
                self.inv = 60
                return True
            else:
                self.lives -= 1
                self.inv = 140
                return True
        return False

    def reset_position(self):
        self.x = float(W // 2)
        self.y = float(H - 75)

    def update(self, dx):
        if not self.captured:
            margin = 40.0 if self.is_dual else 24.0
            self.x = max(margin, min(float(W - margin), self.x + dx * self.speed))

        if self.shoot_cd > 0:
            self.shoot_cd -= 1
        if self.inv > 0:
            self.inv -= 1
        for b in self.bullets[:]:
            b.update()
            if b.y < -10:
                self.bullets.remove(b)
