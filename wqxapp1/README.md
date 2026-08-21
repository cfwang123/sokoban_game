# Sokoban · BBK Wenquxing (wqxapp1) — teaching project

> [中文版](README.ZH.md)

C teaching project for **BBK Wenquxing**-class e-dictionaries (layered HAL + game core).

[Changelog](CHANGELOG.md) · [Dev notes](docs/DEVELOPMENT.md)

**Current version: 1.0.0**

> **Note**  
> - Readable sources and project skeleton; **device firmware build is not required in this repo**.  
> - Historical Wenquxing SDKs/resolutions differ → `wqx/wqx_api.h` abstracts the device; bind vendor libs for real hardware.  
> - Gameplay aligned with `html_app` / `androidapp1` / `n81app1` (push rules, undo, solution playback, level memory).  
> - Demo level subset (~20 levels in `levels_data.c`).

---

## 1. Why C + HAL?

Typical e-dictionary era setup:

| Topic | Notes |
|-------|--------|
| Language | C (small RAM/ROM; toolchains are C-first) |
| Display | write framebuffer / rects; rare full GUI framework |
| Input | key-matrix scan in the main loop |
| Assets | levels/fonts compiled in; little filesystem use |

This project follows that split so you can compare with Android / Java ME / HTML ports.

---

## 2. Layout

```
wqxapp1/
├── README.md / README.ZH.md
├── CHANGELOG.md
├── Makefile              # teaching: list / optional host syntax check
├── docs/DEVELOPMENT.md
├── include/
│   ├── wqx/wqx_api.h     # device HAL contract (core teaching file)
│   ├── game.h
│   ├── pathfinding.h
│   ├── ui.h
│   ├── app.h
│   └── levels_data.h
├── src/
│   ├── main.c            # entry
│   ├── app.c             # main loop / keys / solution playback
│   ├── game.c            # push state machine
│   ├── pathfinding.c     # BFS
│   ├── ui.c              # status bar + board draw
│   ├── levels_data.c     # embedded levels
│   └── wqx_hal_stub.c    # stub when no vendor SDK
├── res/levels_demo.json
└── tools/gen_levels.py
```

### Reading order

1. `include/wqx/wqx_api.h`  
2. `src/app.c`  
3. `src/game.c` + `src/ui.c`  
4. `src/wqx_hal_stub.c`  

---

## 3. Features

| Feature | Implementation |
|---------|----------------|
| Move / push | logical direction keys |
| Undo | box pushes only |
| Reset / change level | RESET / PREV / NEXT |
| Solution playback | step through solution when present |
| Level memory | `wqx_nv_*` |

## Host helpers

```bat
cd wqxapp1
make help
make list
```
