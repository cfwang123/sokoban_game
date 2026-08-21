# FC / NES Sokoban (fcapp1)

> [中文版](README.ZH.md)

Ports `html_app` Sokoban to **NES/FC**. Project layout inspired by `game/fc_mario`.

- **Game logic in C** (cc65)
- Assembly only for: iNES header, Reset, NMI, CHR embed

ROM: `sokoban.nes` (NROM-256, ~40KB)

## Run

Open in any NES/FC emulator:

```
fcapp1/sokoban.nes
```

Suggested: Mesen, FCEUX, Nestopia, RetroArch.

## Controls

| Input | Action |
|-------|--------|
| **← →** (title) | select level |
| **Start / A** (title) | start |
| **D-pad** | move / push |
| **B** | undo (walk steps, then last box push) |
| **Select** | reset level |
| **Start** (in game) | open menu |
| **↑ ↓** (menu) | RESET / NEXT / ANS |
| **A / Start** (menu) | confirm |
| **B** (menu) | close menu |
| **B / Start** (playback) | cancel solution playback |
| **Start / A** (win) | next level |
| **B** (win) | title |

Menu items: **RESET** · **NEXT** · **ANS** (preset solution; beep if none).

HUD: `L` level · `M` box pushes · `G` boxes on goals / total

## Rebuild

Dependencies:

- [cc65](https://cc65.github.io/) V2.19+ (`cc65` / `ca65` / `ld65` on PATH, or `CC65_HOME`, or `fcapp1/tools/cc65/`)
- Python 3 (CHR + level data)
- Parent `levels.json`

```bat
cd fcapp1
build.bat
```

Pipeline:

1. `tools/make_chr.py` → `chr/tiles.chr`
2. `tools/gen_levels.py` → `src/levels.c` (from `../levels.json`, ≤20×18, max 80 levels)
3. cc65 compile `main.c` / `music.c` / `levels.c`
4. ca65 + ld65 → `sokoban.nes`

## Layout

```
fcapp1/
  sokoban.nes       ROM
  build.bat         one-shot build
  nrom256.cfg       ld65: 32KB PRG + 8KB CHR
  chr/tiles.chr     tiles
  src/
    main.c          main logic
    music.c         8-bit BGM + SFX
    levels.c        generated levels
    nes.h / game.h
    header.s        iNES
    reset.s         reset / RAM / main
    nmi.s           OAM DMA
    chr.s           CHR
  tools/
    make_chr.py
    gen_levels.py
```
