#!/usr/bin/env python3
"""HarnessOS Easter Egg — Galaga"""

import sys
import math
import random
from pathlib import Path
import pygame

W, H = 800, 700
FPS  = 60

# Tokyo Night palette
BG     = (13,  17,  23)
WHITE  = (192, 202, 224)
DIM    = (70,  80,  100)
GREEN  = (158, 206, 106)
RED    = (247, 118, 142)
BLUE   = (122, 162, 247)
YELLOW = (224, 175, 104)
CYAN   = (125, 207, 255)
PURPLE = (187, 154, 247)
ORANGE = (255, 158, 100)


# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------

def bezier_point(p0, p1, p2, p3, t):
    """Calcula un punto en una curva de Bézier cúbica (t va de 0.0 a 1.0)."""
    u = 1.0 - t
    tt = t * t
    uu = u * u
    uuu = uu * u
    ttt = tt * t

    x = uuu * p0[0] + 3 * uu * t * p1[0] + 3 * u * tt * p2[0] + ttt * p3[0]
    y = uuu * p0[1] + 3 * uu * t * p1[1] + 3 * u * tt * p2[1] + ttt * p3[1]
    return float(x), float(y)


# ---------------------------------------------------------------------------
# Audio System (8-bit Procedural Sound Engine)
# ---------------------------------------------------------------------------
import array

def init_audio():
    """Inicializa el mixer de Pygame para baja latencia."""
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        return True
    except Exception:
        return False

def make_square_wave(freq, duration_sec, vol=0.3):
    """Genera un sonido de onda cuadrada estilo 8-bit/Chiptune."""
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

def make_noise(duration_sec, vol=0.4):
    """Genera ruido blanco estilo 8-bit para explosiones."""
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

SFX = {}

def load_sfx():
    """Crea y almacena en memoria los sonidos arcade del juego."""
    if not init_audio():
        return
    SFX['shoot'] = make_square_wave(880, 0.08, vol=0.25)
    SFX['shoot_dual'] = make_square_wave(660, 0.09, vol=0.3)
    SFX['enemy_shoot'] = make_square_wave(300, 0.08, vol=0.15)
    SFX['boom'] = make_noise(0.25, vol=0.35)
    SFX['player_boom'] = make_noise(0.6, vol=0.6)
    SFX['capture'] = make_square_wave(180, 0.4, vol=0.4)
    SFX['powerup'] = make_square_wave(1200, 0.3, vol=0.4)

def play_sound(name):
    """Reproduce un sonido de forma segura si el audio está activo."""
    if name in SFX and SFX[name]:
        SFX[name].play()

# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def draw_ship(surf, x, y, size=None):
    pts = [
        (x,      y - 18),
        (x - 14, y + 12),
        (x,      y + 4),
        (x + 14, y + 12),
    ]
    pygame.draw.polygon(surf, GREEN, pts)
    pygame.draw.circle(surf, CYAN, (x, y - 3), 5)
    pygame.draw.rect(surf, (80, 200, 80), (x - 4, y + 12, 8, 5))


def draw_drone(surf, x, y, size=13):
    pts = [(x, y - size), (x + size, y), (x, y + size), (x - size, y)]
    pygame.draw.polygon(surf, BLUE, pts)
    pygame.draw.polygon(surf, CYAN, pts, 2)
    pygame.draw.circle(surf, WHITE, (x, y), 4)


def draw_bee(surf, x, y, size=15):
    pygame.draw.ellipse(surf, PURPLE, (x - 10, y - size, 20, size * 2))
    pygame.draw.ellipse(surf, YELLOW, (x - size, y - 7, size, 14))
    pygame.draw.ellipse(surf, YELLOW, (x,        y - 7, size, 14))
    pygame.draw.circle(surf, WHITE, (x, y), 5)


def draw_boss(surf, x, y, size=20):
    pygame.draw.ellipse(surf, RED, (x - size, y - size, size * 2, size * 2))
    pygame.draw.ellipse(surf, YELLOW, (x - 12, y - size // 2, 24, size))
    pygame.draw.circle(surf, WHITE, (x, y), 7)
    pygame.draw.line(surf, ORANGE, (x - 8,  y - size), (x - 14, y - size - 10), 2)
    pygame.draw.line(surf, ORANGE, (x + 8,  y - size), (x + 14, y - size - 10), 2)


# ---------------------------------------------------------------------------
# Game objects
# ---------------------------------------------------------------------------

class Bullet:
    def __init__(self, x, y, vy, color):
        self.x = x
        self.y = float(y)
        self.vy = vy
        self.color = color

    def update(self):
        self.y += self.vy

    def draw(self, surf):
        h = 14 if self.vy < 0 else 10
        pygame.draw.rect(surf, self.color, (self.x - 2, int(self.y) - h // 2, 4, h))


class Enemy:
    DEFS = {
        'drone': (BLUE,   10, 13, draw_drone),
        'bee':   (PURPLE, 20, 15, draw_bee),
        'boss':  (RED,    50, 20, draw_boss),
    }

    def __init__(self, col, row, etype):
        self.etype = etype
        self.color, self.pts, self.size, self._draw_fn = self.DEFS[etype]
        self.home_x = 90 + col * 66
        self.home_y = 100 + row * 52
        self.x = float(self.home_x)
        self.y = float(self.home_y)
        self.alive    = True
        self.bullets: list[Bullet] = []
        self.swooping = False
        self._phase   = 0.0
        self._ox = self._oy = 0.0
        self._bezier: tuple | None = None
        self.shoot_cd = random.randint(120, 500)

        # --- Variables del Rayo Tractor ---
        self.has_captured = False
        self.tractor_state = 0  # 0: Normal, 1: Bajando, 2: Emitiendo, 3: Volviendo
        self.beam_timer = 0
        self.beam_poly = []

    def start_swoop(self):
        if not self.swooping and self.tractor_state == 0:
            self.swooping = True
            self._phase = 0.0
            self._ox = self.x
            self._oy = self.y
            sway = random.uniform(120, 220) * random.choice((-1, 1))
            p0 = (self.x, self.y)
            p1 = (self.x + sway, self.y + 180)
            p2 = (self.x - sway * 0.6, self.y + 380)
            p3 = (self.x + random.uniform(-40, 40), H + 60)
            self._bezier = (p0, p1, p2, p3)

    def start_tractor_attack(self):
        if not self.swooping and self.etype == 'boss' and self.tractor_state == 0:
            self.swooping = True
            self.tractor_state = 1
            self._ox = self.x
            self._oy = self.y

    def update(self, fm_dx, fm_dy, bullet_speed=7):
        if self.swooping and self.tractor_state > 0:
            # --- LÓGICA DE SECUESTRO DEL BOSS ---
            if self.tractor_state == 1:  # Bajando al punto de disparo
                self.y += 3.5
                if self.y >= H - 280:
                    self.tractor_state = 2
                    self.beam_timer = 120  # 2 segundos emitiendo luz
                    play_sound('capture')
            
            elif self.tractor_state == 2:  # Emitiendo rayo tractor
                self.beam_timer -= 1
                self.beam_poly = [
                    (self.x - 12, self.y + 15),
                    (self.x + 12, self.y + 15),
                    (self.x + 80, H),
                    (self.x - 80, H)
                ]
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
            if self.alive and self.tractor_state == 0:
                self.bullets.append(Bullet(int(self.x), int(self.y) + 12, bullet_speed, RED))
                play_sound('enemy_shoot')

        for b in self.bullets[:]:
            b.update()
            if b.y > H + 20:
                self.bullets.remove(b)

    def draw(self, surf):
        if self.alive:
            self._draw_fn(surf, int(self.x), int(self.y), self.size)
            
            # Si tiene una nave secuestrada, la dibuja encima
            if self.has_captured:
                draw_ship(surf, int(self.x), int(self.y) - 24)
            
            # Dibuja el haz de luz transparente
            if self.tractor_state == 2 and len(self.beam_poly) == 4:
                beam_surf = pygame.Surface((W, H), pygame.SRCALPHA)
                alpha = random.randint(80, 140)
                pygame.draw.polygon(beam_surf, (*CYAN, alpha), self.beam_poly)
                surf.blit(beam_surf, (0, 0))

        for b in self.bullets:
            b.draw(surf)


class Player:
    def __init__(self, score=0, lives=3):
        self.x        = float(W // 2)
        self.y        = float(H - 75)
        self.speed    = 5.5
        self.bullets: list[Bullet] = []
        self.shoot_cd = 0
        self.score    = score
        self.lives    = lives
        self.inv      = 0
        self.is_dual  = False
        self.captured = False  # Para animación de secuestro

    def shoot(self):
        if self.shoot_cd <= 0 and not self.captured:
            if self.is_dual:
                self.bullets.append(Bullet(int(self.x) - 16, int(self.y) - 22, -13, GREEN))
                self.bullets.append(Bullet(int(self.x) + 16, int(self.y) - 22, -13, GREEN))
                play_sound('shoot_dual')
            else:
                self.bullets.append(Bullet(int(self.x), int(self.y) - 22, -13, GREEN))
                play_sound('shoot')
            self.shoot_cd = 14

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

    def draw(self, surf):
        if not self.captured and (self.inv % 8 < 4):
            if self.is_dual:
                draw_ship(surf, int(self.x) - 16, int(self.y))
                draw_ship(surf, int(self.x) + 16, int(self.y))
            else:
                draw_ship(surf, int(self.x), int(self.y))
        for b in self.bullets:
            b.draw(surf)


# ---------------------------------------------------------------------------
# Stars
# ---------------------------------------------------------------------------

def make_stars(n=130):
    return [
        [random.uniform(0, W), random.uniform(0, H),
         random.randint(100, 220), random.uniform(0.4, 2.0),
         random.randint(1, 2)]
        for _ in range(n)
    ]


def draw_stars(surf, stars):
    for s in stars:
        s[1] += s[3]
        if s[1] > H:
            s[1] = 0.0
            s[0] = random.uniform(0, W)
        c = s[2]
        pygame.draw.circle(surf, (c, c, min(255, c + 30)),
                           (int(s[0]), int(s[1])), s[4])


def make_enemies():
    layout = [('boss', 10), ('bee', 10), ('drone', 10), ('drone', 10)]
    return [Enemy(col, row, etype) for row, (etype, cols) in enumerate(layout) for col in range(cols)]


# ---------------------------------------------------------------------------
# Intro screen: 3 flashes → portrait → fade to black
# ---------------------------------------------------------------------------

def _find_portrait() -> str | None:
    candidates = [
        Path("/usr/local/share/harness/easter-egg/portrait.png"),
        Path("/usr/local/share/harness/easter-egg/portrait.jpg"),
    ]
    home = Path.home() / ".local/share/harness/easter-egg"
    for ext in ("png", "jpg", "jpeg", "webp"):
        candidates.append(home / f"portrait.{ext}")
    for p in candidates:
        if p.exists():
            return str(p)
    return None


def screen_intro(surface, clock) -> bool:
    def pump() -> bool:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_q, pygame.K_ESCAPE):
                return False
        return True

    for _ in range(3):
        surface.fill((255, 255, 255))
        pygame.display.flip()
        pygame.time.wait(90)
        if not pump(): return False
        surface.fill((0, 0, 0))
        pygame.display.flip()
        pygame.time.wait(90)
        if not pump(): return False

    path = _find_portrait()
    if not path:
        return True

    try:
        img = pygame.image.load(path).convert()
    except Exception:
        return True

    iw, ih = img.get_size()
    scale   = min(W / iw, H / ih)
    nw, nh  = int(iw * scale), int(ih * scale)
    portrait = pygame.transform.smoothscale(img, (nw, nh))
    px = (W - nw) // 2
    py = (H - nh) // 2

    fade = pygame.Surface((W, H))
    fade.fill((0, 0, 0))
    for alpha in range(255, -1, -10):
        if not pump(): return False
        fade.set_alpha(alpha)
        surface.fill((0, 0, 0))
        surface.blit(portrait, (px, py))
        surface.blit(fade, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)

    surface.fill((0, 0, 0))
    surface.blit(portrait, (px, py))
    pygame.display.flip()

    start = pygame.time.get_ticks()
    skip = False
    while pygame.time.get_ticks() - start < 3000 and not skip:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: return False
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_q, pygame.K_ESCAPE): return False
                skip = True
        clock.tick(FPS)

    for alpha in range(0, 256, 10):
        if not pump(): return False
        fade.set_alpha(alpha)
        surface.fill((0, 0, 0))
        surface.blit(portrait, (px, py))
        surface.blit(fade, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)

    return True


# ---------------------------------------------------------------------------
# Game screens
# ---------------------------------------------------------------------------

def screen_title(surface, clock, stars, fonts) -> bool:
    f_big, f_med, f_sm = fonts
    t = 0
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return True

        surface.fill(BG)
        draw_stars(surface, stars)

        pulse = 0.6 + 0.4 * abs(math.sin(t * 0.04))
        title = f_big.render("HARNESS  OS", True, CYAN)
        sub   = f_med.render("G  A  L  A  G  A", True,
                              tuple(int(c * pulse) for c in YELLOW))
        blink = WHITE if t % 60 < 40 else DIM
        hint  = f_sm.render("PRESS  ENTER  TO  PLAY  /  Q  QUIT", True, blink)
        ctrl  = f_sm.render("ARROWS / WASD  move      SPACE  shoot", True, DIM)

        surface.blit(title, (W // 2 - title.get_width() // 2, 180))
        surface.blit(sub,   (W // 2 - sub.get_width()   // 2, 268))

        cx = W // 2
        draw_ship(surface,  cx - 140, 370)
        draw_boss(surface,  cx,       355, 22)
        draw_ship(surface,  cx + 140, 370)
        draw_drone(surface, cx - 70,  380, 12)
        draw_bee(surface,   cx - 70,  420, 13)
        draw_drone(surface, cx + 70,  380, 12)
        draw_bee(surface,   cx + 70,  420, 13)

        surface.blit(hint, (W // 2 - hint.get_width() // 2, 470))
        surface.blit(ctrl, (W // 2 - ctrl.get_width() // 2, 508))

        pygame.display.flip()
        clock.tick(FPS)
        t += 1


def screen_gameover(surface, clock, stars, fonts, score) -> bool:
    f_big, _, f_sm = fonts
    t = 0
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False
                if ev.key == pygame.K_RETURN:
                    return True

        surface.fill(BG)
        draw_stars(surface, stars)
        blink = WHITE if t % 60 < 40 else DIM
        go   = f_big.render("GAME  OVER", True, RED)
        sc   = f_sm.render(f"Score: {score:06d}", True, WHITE)
        hint = f_sm.render("ENTER restart   Q quit", True, blink)
        surface.blit(go,   (W // 2 - go.get_width()   // 2, H // 2 - 80))
        surface.blit(sc,   (W // 2 - sc.get_width()   // 2, H // 2))
        surface.blit(hint, (W // 2 - hint.get_width() // 2, H // 2 + 60))
        pygame.display.flip()
        clock.tick(FPS)
        t += 1


def screen_wave(surface, clock, stars, fonts, wave) -> bool:
    f_big = fonts[0]
    for _ in range(120):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_q, pygame.K_ESCAPE):
                return False
        surface.fill(BG)
        draw_stars(surface, stars)
        txt = f_big.render(f"WAVE  {wave}", True, CYAN)
        surface.blit(txt, (W // 2 - txt.get_width() // 2, H // 2 - 40))
        pygame.display.flip()
        clock.tick(FPS)
    return True


def run_game(surface, clock, stars, fonts, wave=1, score=0, lives=3):
    """Returns (score, lives, signal) — signal: 'quit' | 'dead' | 'next_wave'"""
    _, _, f_hud = fonts
    player  = Player(score=score, lives=lives)
    enemies = make_enemies()

    fm_dx  = 0.0
    fm_dy  = 0.0
    fm_dir = 1
    fm_spd = min(2.0, 0.5 + (wave - 1) * 0.22)
    fm_drop = 22.0
    bullet_speed = min(11, 7 + (wave - 1))
    swoop_cd = random.randint(160, 340)
    explosions: list[dict] = []

    while True:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return player.score, player.lives, 'quit'
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_q):
                return player.score, player.lives, 'quit'

        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            player.shoot()
        
        # Si la nave es secuestrada, es succionada hacia el Boss
        if player.captured:
            for e in enemies:
                if e.tractor_state > 0:
                    player.x += (e.x - player.x) * 0.08
                    player.y += (e.y - player.y) * 0.08
                    if abs(player.y - e.y) < 30:
                        e.has_captured = True
                        e.tractor_state = 3
                        player.captured = False
                        player.lives -= 1
                        player.inv = 180
                        player.x = float(W // 2)
                        player.y = float(H - 75)
                        if player.lives <= 0:
                            return player.score, 0, 'dead'
                    break
        else:
            player.update(dx)

        alive_form = [e for e in enemies if e.alive and not e.swooping]
        if alive_form:
            xs = [e.home_x + fm_dx for e in alive_form]
            if max(xs) >= W - 55 and fm_dir == 1:
                fm_dir  = -1
                fm_dy  += fm_drop
            elif min(xs) <= 55 and fm_dir == -1:
                fm_dir  = 1
                fm_dy  += fm_drop
        fm_dx += fm_spd * fm_dir

        # Decidir ataque de enemigo (Normal vs Rayo Tractor)
        swoop_cd -= 1
        if swoop_cd <= 0:
            swoop_cd = max(70, random.randint(100, 280) - wave * 8)
            cands = [e for e in enemies if e.alive and not e.swooping]
            if cands:
                # 35% de probabilidad de que un Boss disponible intente el
                # secuestro cada vez que toca elegir ataque, en lugar de
                # depender de que la ruleta general elija primero un boss
                # entre todos los enemigos (lo hacía casi invisible).
                boss_cands = [e for e in cands if e.etype == 'boss' and not e.has_captured]
                if (boss_cands and not player.is_dual and not player.captured
                        and random.random() < 0.35):
                    random.choice(boss_cands).start_tractor_attack()
                else:
                    random.choice(cands).start_swoop()

        for e in enemies:
            e.update(fm_dx, fm_dy, bullet_speed=bullet_speed)

        # --- Detección de Captura por el Rayo Tractor ---
        if not player.captured and not player.is_dual and player.inv == 0:
            for e in enemies:
                if e.alive and e.tractor_state == 2:
                    # Comprobamos si el jugador está dentro de la luz del rayo
                    if player.y > e.y + 20 and abs(player.x - e.x) < 70:
                        player.captured = True
                        break

        # Balas de jugador vs Enemigos
        for pb in player.bullets[:]:
            for e in enemies:
                if e.alive and abs(pb.x - e.x) < e.size + 6 and abs(pb.y - e.y) < e.size + 6:
                    e.alive = False
                    player.score += e.pts
                    
                    # ¡RESCATE DE LA NAVE SECUESTRADA!
                    if e.has_captured:
                        player.is_dual = True
                        play_sound('powerup')
                        explosions.append({'x': int(e.x), 'y': int(e.y), 'r': 10.0, 'max': 70.0, 'color': GREEN})
                    else:
                        play_sound('boom')
                    
                    if pb in player.bullets:
                        player.bullets.remove(pb)
                    explosions.append({'x': int(e.x), 'y': int(e.y),
                                       'r': 4.0, 'max': 32.0, 'color': e.color})
                    break

        # Balas enemigas vs Jugador
        for e in enemies:
            for b in e.bullets[:]:
                hit = False
                if player.is_dual:
                    if (abs(b.x - (player.x - 16)) < 14 and abs(b.y - player.y) < 14) or \
                       (abs(b.x - (player.x + 16)) < 14 and abs(b.y - player.y) < 14):
                        hit = True
                else:
                    if abs(b.x - player.x) < 14 and abs(b.y - player.y) < 14:
                        hit = True

                if hit and player.hit():
                    play_sound('player_boom')
                    e.bullets.remove(b)
                    explosions.append({'x': int(player.x), 'y': int(player.y),
                                       'r': 4.0, 'max': 50.0, 'color': GREEN})

        for e in enemies:
            if e.alive and not e.swooping and e.y > H - 50:
                player.lives = 0

        if player.lives <= 0:
            return player.score, 0, 'dead'
        if all(not e.alive for e in enemies):
            return player.score, player.lives, 'next_wave'

        surface.fill(BG)
        draw_stars(surface, stars)
        for e in enemies:
            e.draw(surface)
        player.draw(surface)
        for ex in explosions[:]:
            ex['r'] += 2.5
            pygame.draw.circle(surface, ex['color'], (ex['x'], ex['y']), int(ex['r']), 2)
            if ex['r'] >= ex['max']:
                explosions.remove(ex)

        sc_t = f_hud.render(f"SCORE  {player.score:06d}", True, WHITE)
        wv_t = f_hud.render(f"WAVE  {wave}", True, CYAN)
        lv_t = f_hud.render("SHIP  " + "■ " * max(0, player.lives), True, GREEN)
        surface.blit(sc_t, (20, 12))
        surface.blit(wv_t, (W // 2 - wv_t.get_width() // 2, 12))
        surface.blit(lv_t, (W - lv_t.get_width() - 20, 12))
        pygame.display.flip()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    pygame.init()
    load_sfx()
    surface = pygame.display.set_mode((W, H))
    pygame.display.set_caption("HarnessOS — Galaga")
    clock = pygame.time.Clock()

    fonts = (
        pygame.font.SysFont("monospace", 52, bold=True),
        pygame.font.SysFont("monospace", 34, bold=True),
        pygame.font.SysFont("monospace", 20, bold=True),
    )
    stars = make_stars()

    # --- Easter egg intro (flashes + portrait) ---
    if not screen_intro(surface, clock):
        pygame.quit()
        sys.exit()

    # --- Game loop ---
    while True:
        if not screen_title(surface, clock, stars, fonts):
            break

        wave, score, lives = 1, 0, 3
        while True:
            result_score, result_lives, signal = run_game(
                surface, clock, stars, fonts,
                wave=wave, score=score, lives=lives,
            )
            score = result_score
            lives = result_lives

            if signal == 'quit':
                pygame.quit()
                sys.exit()
            elif signal == 'next_wave':
                wave += 1
                if not screen_wave(surface, clock, stars, fonts, wave):
                    pygame.quit()
                    sys.exit()
            else:  # dead
                if not screen_gameover(surface, clock, stars, fonts, score):
                    break
                wave, score, lives = 1, 0, 3

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()