# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- Run the game: `python galago.py` (works from the repo root without installing anything — the script inserts `src/` onto `sys.path` itself)
- Install for development: `pip install -e ".[test]"`
- Run all tests: `pytest`
- Run a single test: `pytest tests/test_capture.py::test_apply_capture_pull_finalizes_when_close_enough`
- The test suite in `tests/` covers only `domain/` and has **zero dependency on `pygame`**. It must keep passing in a virtualenv where `pygame` is not installed — that's the actual proof the domain/pygame boundary holds. Re-check this (e.g. in a throwaway pygame-free venv) whenever `domain/` changes.

## Architecture

Galago is a Galaga-style pygame arcade game built as a pragmatic hexagonal (ports & adapters) layout under `src/galago/`. The split exists specifically so gameplay rules can be extended and unit-tested without touching pygame, and pygame-specific concerns (rendering, audio synthesis, input) can change without risking game rules. Preserve that boundary in any change.

- `domain/` — **zero `pygame` import, enforced**. `entities.py` (`Player`, `Enemy`, `Bullet`), `formation.py` (formation marching/bounce-and-drop), `collisions.py` (pure hit-test predicates), `capture.py` + state fields on `Enemy` (the boss tractor-beam capture state machine), `waves.py` (per-wave difficulty scaling formulas, `make_enemies()`), `explosions.py`, and `session.py::GameRound` — the per-frame rules orchestrator (`GameRound.step()`), the single highest-value class in the codebase and the natural place to extend gameplay.
- `ports/` — four small `typing.Protocol` interfaces (`Renderer`, `InputProvider`, `AudioPlayer`, `GameClock`). No ABCs, no DTOs/mappers: adapters are expected to read domain types (`Player`, `Enemy`, `GameRound`, ...) directly. The port boundary exists only to keep pygame out of `domain`/`app`, not to hide domain types from adapters.
- `app/loop.py` — `GameApp` owns the screen state machine (title → wave banner → playing → game over, including the quirk that pressing quit on the game-over screen returns to the title screen rather than exiting) and drives it purely through the four ports above.
- `adapters/pygame_adapter/` — the **only** place allowed to `import pygame`: `renderer.py` + `palette.py` (drawing, colors, starfield, HUD), `input.py` (keyboard/event polling), `audio.py` (procedural 8-bit chiptune SFX, plus a bundled music track played via `pygame.mixer.music`), `clock.py` (thin wrapper), `intro.py` (the flashes + portrait fade bootstrap, called directly from `__main__.py` before `GameApp.run()` since it has no game-rule content and isn't worth routing through the ports).
- `galago.py` at the repo root is a thin compatibility shim (`sys.path` insert + import `galago.__main__:main`) so `python galago.py` keeps working without an editable install. `src/galago/__main__.py` is the real composition root that wires the concrete pygame adapters into `GameApp`.
- `assets/images/` and `assets/sounds/` hold binary media for the project (`portrait.png`, the intro/README logo; a bundled music track). Any adapter code that loads a bundled asset should resolve it via `src/galago/paths.py::resource_root()`, never a hardcoded absolute path — it returns the repo root when running from source and `sys._MEIPASS` when frozen into a PyInstaller executable (see `galago.spec` and `.github/workflows/build-executables.yml`).

### Design rules to keep when extending

- **Sound events, not direct calls**: domain methods (`Enemy.update()`, `Player.shoot()`) return `list[str]` event tags (e.g. `'capture'`, `'enemy_shoot'`, `'boom'`) instead of playing sounds directly. `GameRound.step()` collects them; `GameApp` forwards them to `AudioPlayer.play()`. Domain code never touches a port.
- **No visual state in domain**: `Bullet.owner` (`'player'`/`'enemy'`) and `Explosion.source` (an enemy `etype` or `'rescue'`/`'player_hit'`) replace raw RGB tuples. Adapters resolve these to colors via `palette.py`'s `BULLET_COLOR` / `EXPLOSION_COLOR` / `ETYPE_COLOR` maps.
- **Tractor-beam geometry is adapter-only**: the beam polygon is recomputed each frame in `renderer.py` from `enemy.x/y` whenever `enemy.tractor_state == 2`; it is not stored on the domain `Enemy`.
- **Explosion prune-then-grow ordering matters**: `GameRound.step()` prunes explosions that finished growing *last* frame at the *start* of the current step, then grows survivors at the end. This reproduces the original single-file game's behavior of drawing one final frame at max radius before an explosion disappears — don't collapse this into a single grow-and-remove pass without re-checking that timing.
- **Determinism in tests**: domain randomness (`random.random`/`random.choice`/`random.randint`, used in `Enemy`, `session.py`, `waves.py`) is controlled in tests via `pytest monkeypatch`, not by threading a `random.Random` instance through constructors.

## Behavioral contract

This structure replaced an earlier single 774-line `galago.py` (see the initial commit in git history) with the explicit goal of preserving gameplay byte-for-byte — visuals, audio, timings, and balance are not incidental side effects to accept during structural changes. When modifying `domain/`, prefer adding a test in `tests/` that pins the specific rule being changed rather than relying on manual playtesting alone.
