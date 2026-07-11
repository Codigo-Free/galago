# Galago

A Galaga-style arcade shoot-'em-up written in Python with [pygame](https://www.pygame.org/), featuring the classic tractor-beam capture mechanic and a Tokyo Night color palette.

## Features

- Wave-based enemy formations (drones, bees, boss) with swooping attack patterns
- Boss tractor-beam capture/rescue mechanic — free your captured ship to unlock dual-fighter mode
- Procedurally generated 8-bit chiptune sound effects (no audio assets required)
- Bézier-curve enemy swoop paths and a scrolling starfield
- Optional intro screen with a portrait easter egg

## Requirements

- Python 3.10+
- [pygame](https://www.pygame.org/)

```bash
pip install pygame
```

## Run

```bash
python galago.py
```

## Controls

| Action | Keys |
|---|---|
| Move | Arrow keys / WASD |
| Shoot | Space / Up / W |
| Confirm / Restart | Enter |
| Quit | Q / Esc |

## Architecture

The game follows a pragmatic hexagonal (ports & adapters) layout under `src/galago/`:

- `domain/` — entities, collisions, formation movement, the boss capture state machine, scoring. Pure Python, zero `pygame` import.
- `ports/` — small `Protocol` interfaces (`Renderer`, `InputProvider`, `AudioPlayer`, `GameClock`) that the application layer depends on.
- `app/` — `GameApp`, the screen state machine (title → wave → playing → game over) driven purely through the ports.
- `adapters/pygame_adapter/` — the only place that imports `pygame`: rendering, input polling, procedural audio synthesis, and the clock.

`galago.py` at the repo root is a thin compatibility shim so `python galago.py` keeps working unchanged.

## Development

```bash
pip install -e ".[test]"
pytest
```

The domain layer (`src/galago/domain/`) has no dependency on `pygame` and its tests run even without `pygame` installed — that's what proves the decoupling actually holds.

## Credits

Construido en [HarnessOS](https://github.com/Codigo-Free/HarnessOS) con VS Code y Claude, por efrasoft@gmail.com.
