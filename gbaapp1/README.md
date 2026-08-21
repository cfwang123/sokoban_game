# Sokoban · GBA (gbaapp1)

> [中文版](README.ZH.md)

Ports `html_app` / `fcapp1` Sokoban to a **Game Boy Advance** ROM.  
**Mode 3 true-color 16×16 tiles** + shadowed HUD font — much richer than FC 8×8 tiles.

Reference layout: bare-metal + EWRAM offscreen buffer (similar spirit to `game/gba/tower_gba`).

## Run

Open with mGBA / VBA-M / RetroArch:

```
gbaapp1/sokoban.gba
```

## Controls

| Key | Action |
|-----|--------|
| **← →** (title) | select level |
| **Start / A** (title) | start |
| **D-pad** | move / push (repeat supported) |
| **B** | undo |
| **Select** | reset level |
| **Start** (in game) | menu: RESET / NEXT / ANSWER |
| **A** (menu) | confirm |
| **B** (menu) | back |
| **A** (win) | next level |
| **B** (win) | title |
| **B/Start** (DEMO) | cancel solution playback |

## Visual legend

| Element | Look |
|---------|------|
| Wall | gray stone + corner shadow |
| Floor | deep blue tiles |
| Goal | red glowing disc |
| Box | wood + metal band + X |
| Box on goal | green wood box |
| Player | small sprite with face |

## Rebuild

Dependencies:

- `arm-none-eabi-gcc` (PATH, or `DEVKITARM` / `ARM_NONE_EABI_PREFIX`)
- Python 3
- Node.js (`gbafix.js`)

```bat
cd gbaapp1
build.bat
```

or:

```bash
make
```

## Layout

```
gbaapp1/
  sokoban.gba       ROM
  build.bat / Makefile
  gba.ld            linker script
  include/          gba.h game.h gfx.h ...
  src/              main/game/gfx/sound/crt0 + generated data
  tools/
    gen_tiles.py    16×16 tiles
    gen_levels.py   pack levels/solutions from ../levels.json
    gbafix.js       ROM header fix
```

## Tech notes

| Item | Detail |
|------|--------|
| CPU | ARM7TDMI @ 16.78 MHz |
| Display | Mode 3, 240×160, 15-bit color |
| Render | EWRAM offscreen + VBlank DMA flip |
| Logic | full C: push/undo/menu/solution/camera |
| Levels | ~60 by default (prefer those with solutions) |
| Audio | simple PSG square SFX |

### vs FC

| | FC (fcapp1) | GBA (gbaapp1) |
|--|-------------|---------------|
| Resolution | 256×240 tiles | 240×160 true color |
| Cell | 8×8 mono | **16×16 gradient/shadow** |
| Colors | 4 levels | **32768** |
| Camera | none | follow large levels |
| Buffer | direct VRAM | double-buffer, no flicker |
