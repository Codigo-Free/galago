import math
import random

import pygame

from ...constants import H, W
from .palette import (
    BG, BULLET_COLOR, CYAN, DIM, EXPLOSION_COLOR, ETYPE_COLOR, GREEN, ORANGE, RED, WHITE, YELLOW,
)


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
    pygame.draw.polygon(surf, ETYPE_COLOR['drone'], pts)
    pygame.draw.polygon(surf, CYAN, pts, 2)
    pygame.draw.circle(surf, WHITE, (x, y), 4)


def draw_bee(surf, x, y, size=15):
    pygame.draw.ellipse(surf, ETYPE_COLOR['bee'], (x - 10, y - size, 20, size * 2))
    pygame.draw.ellipse(surf, YELLOW, (x - size, y - 7, size, 14))
    pygame.draw.ellipse(surf, YELLOW, (x,        y - 7, size, 14))
    pygame.draw.circle(surf, WHITE, (x, y), 5)


def draw_boss(surf, x, y, size=20):
    pygame.draw.ellipse(surf, ETYPE_COLOR['boss'], (x - size, y - size, size * 2, size * 2))
    pygame.draw.ellipse(surf, YELLOW, (x - 12, y - size // 2, 24, size))
    pygame.draw.circle(surf, WHITE, (x, y), 7)
    pygame.draw.line(surf, ORANGE, (x - 8,  y - size), (x - 14, y - size - 10), 2)
    pygame.draw.line(surf, ORANGE, (x + 8,  y - size), (x + 14, y - size - 10), 2)


ETYPE_DRAW = {
    'drone': draw_drone,
    'bee':   draw_bee,
    'boss':  draw_boss,
}


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


def _draw_bullet(surf, bullet):
    h = 14 if bullet.vy < 0 else 10
    pygame.draw.rect(surf, BULLET_COLOR[bullet.owner], (bullet.x - 2, int(bullet.y) - h // 2, 4, h))


def _draw_enemy(surf, enemy):
    if enemy.alive:
        ETYPE_DRAW[enemy.etype](surf, int(enemy.x), int(enemy.y), enemy.size)

        if enemy.has_captured:
            draw_ship(surf, int(enemy.x), int(enemy.y) - 24)

        if enemy.tractor_state == 2:
            beam_poly = [
                (enemy.x - 12, enemy.y + 15),
                (enemy.x + 12, enemy.y + 15),
                (enemy.x + 80, H),
                (enemy.x - 80, H),
            ]
            beam_surf = pygame.Surface((W, H), pygame.SRCALPHA)
            alpha = random.randint(80, 140)
            pygame.draw.polygon(beam_surf, (*CYAN, alpha), beam_poly)
            surf.blit(beam_surf, (0, 0))

    for b in enemy.bullets:
        _draw_bullet(surf, b)


def _draw_player(surf, player):
    if not player.captured and (player.inv % 8 < 4):
        if player.is_dual:
            draw_ship(surf, int(player.x) - 16, int(player.y))
            draw_ship(surf, int(player.x) + 16, int(player.y))
        else:
            draw_ship(surf, int(player.x), int(player.y))
    for b in player.bullets:
        _draw_bullet(surf, b)


def _draw_explosion(surf, explosion):
    pygame.draw.circle(surf, EXPLOSION_COLOR[explosion.source],
                       (explosion.x, explosion.y), int(explosion.r), 2)


class PygameRenderer:
    def __init__(self, surface, fonts):
        self._surface = surface
        self._f_big, self._f_med, self._f_sm = fonts
        self._stars = make_stars()

    def render_title(self, t: int) -> None:
        surface = self._surface
        surface.fill(BG)
        draw_stars(surface, self._stars)

        pulse = 0.6 + 0.4 * abs(math.sin(t * 0.04))
        title = self._f_big.render("HARNESS  OS", True, CYAN)
        sub = self._f_med.render("G  A  L  A  G  A", True,
                                  tuple(int(c * pulse) for c in YELLOW))
        blink = WHITE if t % 60 < 40 else DIM
        hint = self._f_sm.render("PRESS  ENTER  TO  PLAY  /  Q  QUIT", True, blink)
        ctrl = self._f_sm.render("ARROWS / WASD  move      SPACE  shoot", True, DIM)

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

    def render_gameover(self, score: int, t: int) -> None:
        surface = self._surface
        surface.fill(BG)
        draw_stars(surface, self._stars)
        blink = WHITE if t % 60 < 40 else DIM
        go = self._f_big.render("GAME  OVER", True, RED)
        sc = self._f_sm.render(f"Score: {score:06d}", True, WHITE)
        hint = self._f_sm.render("ENTER restart   Q quit", True, blink)
        surface.blit(go,   (W // 2 - go.get_width()   // 2, H // 2 - 80))
        surface.blit(sc,   (W // 2 - sc.get_width()   // 2, H // 2))
        surface.blit(hint, (W // 2 - hint.get_width() // 2, H // 2 + 60))
        pygame.display.flip()

    def render_wave_banner(self, wave: int) -> None:
        surface = self._surface
        surface.fill(BG)
        draw_stars(surface, self._stars)
        txt = self._f_big.render(f"WAVE  {wave}", True, CYAN)
        surface.blit(txt, (W // 2 - txt.get_width() // 2, H // 2 - 40))
        pygame.display.flip()

    def render_playing(self, round_) -> None:
        surface = self._surface
        surface.fill(BG)
        draw_stars(surface, self._stars)

        for e in round_.enemies:
            _draw_enemy(surface, e)
        _draw_player(surface, round_.player)
        for ex in round_.explosions:
            _draw_explosion(surface, ex)

        sc_t = self._f_sm.render(f"SCORE  {round_.player.score:06d}", True, WHITE)
        wv_t = self._f_sm.render(f"WAVE  {round_.wave}", True, CYAN)
        lv_t = self._f_sm.render("SHIP  " + "■ " * max(0, round_.player.lives), True, GREEN)
        surface.blit(sc_t, (20, 12))
        surface.blit(wv_t, (W // 2 - wv_t.get_width() // 2, 12))
        surface.blit(lv_t, (W - lv_t.get_width() - 20, 12))

        pygame.display.flip()
