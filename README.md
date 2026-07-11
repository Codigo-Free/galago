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
