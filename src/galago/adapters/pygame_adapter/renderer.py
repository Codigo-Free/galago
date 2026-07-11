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


def draw_boss(surf, x, y, size=20, variant=0):
    # `variant` (0 = decorativo/normal, 1..10 = boss sucesivos) va oscureciendo
    # el color, poniendo el ojo rojo, y sumando pares de cuernos.
    darkness = min(variant, 10) / 10.0
    body_color = (
        int(ETYPE_COLOR['boss'][0] * (1 - darkness) + 40 * darkness),
        int(ETYPE_COLOR['boss'][1] * (1 - darkness)),
        int(ETYPE_COLOR['boss'][2] * (1 - darkness) + 30 * darkness),
    )
    eye_color = ETYPE_COLOR['boss'] if variant >= 5 else WHITE

    pygame.draw.ellipse(surf, body_color, (x - size, y - size, size * 2, size * 2))
    pygame.draw.ellipse(surf, YELLOW, (x - 12, y - size // 2, 24, size))
    pygame.draw.circle(surf, eye_color, (x, y), 7)

    horn_pairs = 1 + variant // 3
    for i in range(horn_pairs):
        offset = 8 + i * 10
        pygame.draw.line(surf, ORANGE, (x - offset, y - size), (x - offset - 6, y - size - 10 - i * 4), 2)
        pygame.draw.line(surf, ORANGE, (x + offset, y - size), (x + offset + 6, y - size - 10 - i * 4), 2)


def draw_final_boss(surf, x, y, size=65):
    """Boss del stage 100: mezcla de boss (cuerpo/ojo/cuernos), bee (alas) y
    drone (placas), en su versión más oscura y grande."""
    body_color = (30, 0, 20)  # mas oscuro que cualquier variant de draw_boss
    pygame.draw.ellipse(surf, body_color, (x - size, y - size, size * 2, size * 2))
    pygame.draw.ellipse(surf, YELLOW, (x - 12, y - size // 2, 24, size))

    # Alas estilo bee, a los costados del cuerpo
    wing_w = size // 2
    pygame.draw.ellipse(surf, ETYPE_COLOR['bee'], (x - size - wing_w, y - 10, wing_w, 20))
    pygame.draw.ellipse(surf, ETYPE_COLOR['bee'], (x + size, y - 10, wing_w, 20))

    # Placas estilo drone, arriba y abajo del cuerpo
    plate = size // 3
    for dy in (-size - plate // 2, size + plate // 2):
        pts = [(x, y + dy - plate), (x + plate, y + dy), (x, y + dy + plate), (x - plate, y + dy)]
        pygame.draw.polygon(surf, ETYPE_COLOR['drone'], pts)
        pygame.draw.polygon(surf, CYAN, pts, 2)

    # Ojo rojo grande y el máximo de cuernos
    pygame.draw.circle(surf, ETYPE_COLOR['boss'], (x, y), 9)
    for i in range(4):
        offset = 8 + i * 12
        pygame.draw.line(surf, ORANGE, (x - offset, y - size), (x - offset - 6, y - size - 12 - i * 4), 2)
        pygame.draw.line(surf, ORANGE, (x + offset, y - size), (x + offset + 6, y - size - 12 - i * 4), 2)


ETYPE_DRAW = {
    'drone': draw_drone,
    'bee':   draw_bee,
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


def _draw_health_bar(surf, enemy):
    if enemy.max_hp <= 1:
        return
    bar_w, bar_h = 70, 7
    x = int(enemy.x) - bar_w // 2
    y = int(enemy.y) - enemy.size - 22
    pygame.draw.rect(surf, DIM, (x, y, bar_w, bar_h))
    fill_w = int(bar_w * max(0, enemy.hp) / enemy.max_hp)
    fill_color = GREEN if enemy.hp > enemy.max_hp * 0.3 else RED
    pygame.draw.rect(surf, fill_color, (x, y, fill_w, bar_h))


def _draw_enemy(surf, enemy):
    if enemy.alive:
        if enemy.etype == 'boss' and enemy.is_final:
            draw_final_boss(surf, int(enemy.x), int(enemy.y), enemy.size)
        elif enemy.etype == 'boss':
            draw_boss(surf, int(enemy.x), int(enemy.y), enemy.size, enemy.variant)
        else:
            ETYPE_DRAW[enemy.etype](surf, int(enemy.x), int(enemy.y), enemy.size)

        _draw_health_bar(surf, enemy)

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
        title = self._f_big.render("HarnessOS", True, CYAN)
        sub = self._f_med.render("G  A  L  A  G  O", True,
                                  tuple(int(c * pulse) for c in YELLOW))
        blink = WHITE if t % 60 < 40 else DIM
        hint = self._f_sm.render("PRESS  ENTER  TO  PLAY  /  Q  QUIT", True, blink)
        ctrl = self._f_sm.render("ARROWS / WASD  move      SPACE  shoot", True, DIM)
        scores_hint = self._f_sm.render("H  high scores", True, DIM)

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
        surface.blit(scores_hint, (W // 2 - scores_hint.get_width() // 2, 546))

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

    def render_wave_banner(self, wave: int, label: str | None = None) -> None:
        surface = self._surface
        surface.fill(BG)
        draw_stars(surface, self._stars)
        text = label if label is not None else f"WAVE  {wave}"
        txt = self._f_big.render(text, True, CYAN)
        surface.blit(txt, (W // 2 - txt.get_width() // 2, H // 2 - 40))
        pygame.display.flip()

    def render_victory(self, score: int, t: int) -> None:
        surface = self._surface
        surface.fill(BG)
        draw_stars(surface, self._stars)
        pulse = 0.6 + 0.4 * abs(math.sin(t * 0.04))
        title = self._f_big.render("YOU  WIN", True,
                                    tuple(int(c * pulse) for c in YELLOW))
        sc = self._f_sm.render(f"Final Score: {score:06d}", True, WHITE)
        blink = WHITE if t % 60 < 40 else DIM
        hint = self._f_sm.render("ENTER / Q  volver al titulo", True, blink)
        surface.blit(title, (W // 2 - title.get_width() // 2, H // 2 - 80))
        surface.blit(sc,    (W // 2 - sc.get_width()    // 2, H // 2))
        surface.blit(hint,  (W // 2 - hint.get_width()  // 2, H // 2 + 60))
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

        if round_.screen_flash > 0.0:
            flash = pygame.Surface((W, H))
            flash.fill(WHITE)
            flash.set_alpha(int(255 * round_.screen_flash))
            surface.blit(flash, (0, 0))

        pygame.display.flip()

    def render_high_scores(self, scores, t: int) -> None:
        surface = self._surface
        surface.fill(BG)
        draw_stars(surface, self._stars)

        title = self._f_big.render("HIGH SCORES", True, CYAN)
        surface.blit(title, (W // 2 - title.get_width() // 2, 60))

        start_y = 160
        line_height = 34
        if not scores:
            empty = self._f_sm.render("Sin puntajes todavia", True, DIM)
            surface.blit(empty, (W // 2 - empty.get_width() // 2, start_y))
        else:
            for i, entry in enumerate(scores):
                line = f"{i + 1:>2}.  {entry.name:<3}  {entry.score:06d}   {entry.date}"
                text = self._f_sm.render(line, True, WHITE)
                surface.blit(text, (W // 2 - text.get_width() // 2, start_y + i * line_height))

        blink = WHITE if t % 60 < 40 else DIM
        hint = self._f_sm.render("ENTER / Q  volver", True, blink)
        surface.blit(hint, (W // 2 - hint.get_width() // 2, H - 60))

        pygame.display.flip()

    def render_initials_entry(self, entry, score: int, t: int) -> None:
        surface = self._surface
        surface.fill(BG)
        draw_stars(surface, self._stars)

        title = self._f_med.render("NEW HIGH SCORE!", True, YELLOW)
        sc = self._f_sm.render(f"Score: {score:06d}", True, WHITE)
        surface.blit(title, (W // 2 - title.get_width() // 2, 180))
        surface.blit(sc,    (W // 2 - sc.get_width()    // 2, 240))

        blink = t % 40 < 20
        spacing = 20
        rendered_letters = []
        total_width = 0
        for i, letter in enumerate(entry.letters):
            color = CYAN if (i == entry.cursor and blink) else WHITE
            surf = self._f_big.render(letter, True, color)
            rendered_letters.append(surf)
            total_width += surf.get_width() + spacing
        total_width -= spacing

        x = W // 2 - total_width // 2
        y = H // 2 - 20
        for surf in rendered_letters:
            surface.blit(surf, (x, y))
            x += surf.get_width() + spacing

        hint = self._f_sm.render("LEFT/RIGHT  move   UP/DOWN  letter   ENTER  confirm", True, DIM)
        surface.blit(hint, (W // 2 - hint.get_width() // 2, H // 2 + 80))

        pygame.display.flip()
