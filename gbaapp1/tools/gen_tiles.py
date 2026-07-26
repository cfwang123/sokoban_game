#!/usr/bin/env python3
"""Generate polished 16x16 RGB15 tiles for GBA Sokoban (no Pillow needed)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "src" / "tiles_data.c"
T = 16


def rgb15(r, g, b):
    """r,g,b in 0..31"""
    return (r & 31) | ((g & 31) << 5) | ((b & 31) << 10)


def clamp(v, lo=0, hi=31):
    return max(lo, min(hi, v))


def solid(c):
    return [[c] * T for _ in range(T)]


def shade(c, dr, dg, db):
    r = c & 31
    g = (c >> 5) & 31
    b = (c >> 10) & 31
    return rgb15(clamp(r + dr), clamp(g + dg), clamp(b + db))


def make_floor():
    base = rgb15(6, 10, 18)
    hi = rgb15(8, 13, 22)
    lo = rgb15(4, 7, 14)
    px = solid(base)
    for y in range(T):
        for x in range(T):
            if (x + y) & 1:
                px[y][x] = hi
            if x == 0 or y == 0:
                px[y][x] = shade(px[y][x], 2, 2, 2)
            if x == T - 1 or y == T - 1:
                px[y][x] = lo
    return px


def make_wall():
    # Stone brick with mortar and bevel
    mortar = rgb15(8, 8, 10)
    brick = rgb15(14, 14, 16)
    brick_hi = rgb15(20, 20, 22)
    brick_lo = rgb15(9, 9, 11)
    px = solid(mortar)
    # two rows of bricks offset
    for by in range(0, T, 8):
        off = 0 if (by // 8) % 2 == 0 else 4
        for bx in range(-off, T, 8):
            for y in range(by + 1, min(by + 7, T)):
                for x in range(max(bx + 1, 0), min(bx + 7, T)):
                    c = brick
                    if y == by + 1 or x == bx + 1:
                        c = brick_hi
                    if y == by + 6 or x == bx + 6:
                        c = brick_lo
                    px[y][x] = c
    return px


def make_goal():
    px = make_floor()
    # glowing red target plate
    for y in range(3, 13):
        for x in range(3, 13):
            dx, dy = x - 7.5, y - 7.5
            d2 = dx * dx + dy * dy
            if d2 < 16:
                px[y][x] = rgb15(28, 8, 10)
            elif d2 < 25:
                px[y][x] = rgb15(20, 4, 6)
            elif d2 < 36:
                px[y][x] = rgb15(12, 4, 8)
    # inner highlight
    for y in range(6, 10):
        for x in range(6, 10):
            if (x - 7.5) ** 2 + (y - 7.5) ** 2 < 4:
                px[y][x] = rgb15(31, 18, 18)
    return px


def make_box(on_goal=False):
    if on_goal:
        wood = rgb15(8, 22, 10)
        wood_hi = rgb15(14, 28, 14)
        wood_lo = rgb15(4, 14, 6)
        band = rgb15(28, 28, 10)
    else:
        wood = rgb15(22, 14, 6)
        wood_hi = rgb15(28, 20, 10)
        wood_lo = rgb15(14, 8, 3)
        band = rgb15(18, 10, 4)
    px = solid(rgb15(0, 0, 0))
    for y in range(1, 15):
        for x in range(1, 15):
            c = wood
            if y == 1 or x == 1:
                c = wood_hi
            if y == 14 or x == 14:
                c = wood_lo
            # wood grain
            if (y % 3) == 0:
                c = shade(c, -2, -1, 0)
            px[y][x] = c
    # metal bands
    for x in range(2, 14):
        px[4][x] = band
        px[11][x] = band
    for y in range(2, 14):
        px[y][4] = band
        px[y][11] = band
    # X mark
    for i in range(4, 12):
        px[i][i] = rgb15(6, 4, 2) if not on_goal else rgb15(2, 8, 2)
        px[i][15 - i] = rgb15(6, 4, 2) if not on_goal else rgb15(2, 8, 2)
    return px


def make_player():
    px = solid(0)  # transparent 0 — will use key color skip when blit
    # soft shadow
    for y in range(12, 15):
        for x in range(4, 12):
            px[y][x] = rgb15(2, 3, 6)
    # body capsule
    for y in range(5, 13):
        for x in range(4, 12):
            dx = x - 7.5
            if abs(dx) < 3.5:
                px[y][x] = rgb15(8, 18, 28)
    # head
    for y in range(2, 8):
        for x in range(4, 12):
            dx, dy = x - 7.5, y - 4.5
            if dx * dx + dy * dy < 12:
                px[y][x] = rgb15(28, 22, 16)
            if dx * dx + dy * dy < 7:
                px[y][x] = rgb15(30, 24, 18)
    # eyes
    px[4][6] = rgb15(4, 4, 8)
    px[4][9] = rgb15(4, 4, 8)
    px[5][6] = rgb15(31, 31, 31)
    px[5][9] = rgb15(31, 31, 31)
    # hat / hair
    for x in range(5, 11):
        px[2][x] = rgb15(6, 10, 22)
        px[3][x] = rgb15(8, 14, 26)
    # legs
    for y in range(12, 15):
        px[y][5] = rgb15(4, 6, 14)
        px[y][6] = rgb15(6, 10, 20)
        px[y][9] = rgb15(4, 6, 14)
        px[y][10] = rgb15(6, 10, 20)
    return px


def make_hud():
    px = solid(rgb15(4, 6, 12))
    for x in range(T):
        px[0][x] = rgb15(10, 14, 22)
        px[T - 1][x] = rgb15(2, 3, 6)
    return px


def make_void():
    return solid(rgb15(2, 2, 4))


def make_panel():
    # rounded dark panel for menus
    px = solid(rgb15(3, 5, 10))
    for y in range(T):
        for x in range(T):
            if x == 0 or y == 0:
                px[y][x] = rgb15(12, 16, 24)
            if x == T - 1 or y == T - 1:
                px[y][x] = rgb15(1, 2, 4)
    return px


tiles = {
    "void": make_void(),
    "floor": make_floor(),
    "wall": make_wall(),
    "goal": make_goal(),
    "box": make_box(False),
    "boxg": make_box(True),
    "player": make_player(),
    "hud": make_hud(),
    "panel": make_panel(),
}

names = list(tiles.keys())
lines = []
lines.append("/* Auto-generated by tools/gen_tiles.py */")
lines.append('#include "gba.h"')
lines.append('#include "gfx.h"')
lines.append("")
lines.append(f"const int GFX_TILE = {T};")
lines.append(f"const int GFX_TILE_COUNT = {len(names)};")
lines.append("")

for i, name in enumerate(names):
    lines.append(f"/* {i}: {name} */")
    lines.append(f"const u16 gfx_tile_{name}[{T * T}] = {{")
    px = tiles[name]
    row = []
    for y in range(T):
        for x in range(T):
            row.append(f"0x{px[y][x]:04X}")
            if len(row) == 8:
                lines.append("    " + ", ".join(row) + ",")
                row = []
    if row:
        lines.append("    " + ", ".join(row) + ",")
    lines.append("};")
    lines.append("")

lines.append("const u16 * const gfx_tiles[] = {")
for name in names:
    lines.append(f"    gfx_tile_{name},")
lines.append("};")
lines.append("")

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {OUT}: {len(names)} tiles {T}x{T}")
