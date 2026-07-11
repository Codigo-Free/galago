from pathlib import Path

import pygame

from ...constants import H, W

# src/galago/adapters/pygame_adapter/intro.py -> raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[4]


def _find_portrait() -> str | None:
    candidates = [
        Path("/usr/local/share/harness/easter-egg/portrait.png"),
        Path("/usr/local/share/harness/easter-egg/portrait.jpg"),
    ]
    home = Path.home() / ".local/share/harness/easter-egg"
    for ext in ("png", "jpg", "jpeg", "webp"):
        candidates.append(home / f"portrait.{ext}")
    # Si no hay retrato del sistema/usuario, cae al logo versionado en la raíz del proyecto.
    candidates.append(PROJECT_ROOT / "portrait.png")
    for p in candidates:
        if p.exists():
            return str(p)
    return None


def run_intro(surface, clock, fps: int) -> bool:
    """3 flashes -> retrato -> fade a negro. Devuelve False si el usuario
    cierra la ventana o presiona Q/ESC durante la secuencia."""

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
        clock.tick(fps)

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
        clock.tick(fps)

    for alpha in range(0, 256, 10):
        if not pump(): return False
        fade.set_alpha(alpha)
        surface.fill((0, 0, 0))
        surface.blit(portrait, (px, py))
        surface.blit(fade, (0, 0))
        pygame.display.flip()
        clock.tick(fps)

    return True
