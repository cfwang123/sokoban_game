#!/usr/bin/env python3
"""
FC Sokoban CHR — single BG palette, solid colors per type:
  color0 black | color1 gray WALL | color2 blue FLOOR | color3 gold BOX
(see reset.s palette $0F,$00,$21,$28)
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "chr" / "tiles.chr"


def empty():
    return [[0] * 8 for _ in range(8)]


def pack_tile(pixels):
    out = bytearray(16)
    for y in range(8):
        lo = hi = 0
        for x in range(8):
            c = pixels[y][x] & 3
            lo |= (c & 1) << (7 - x)
            hi |= ((c >> 1) & 1) << (7 - x)
        out[y] = lo
        out[y + 8] = hi
    return bytes(out)


def solid(c):
    return [[c] * 8 for _ in range(8)]


def from_rows(rows, m=None):
    if m is None:
        m = {".": 0, " ": 0, "0": 0, "1": 1, "2": 2, "3": 3}
    px = empty()
    for y, row in enumerate(rows[:8]):
        for x, ch in enumerate(row[:8]):
            px[y][x] = m.get(ch, 0)
    return px


FONT = {
    "A": ["01110", "10001", "11111", "10001", "10001"],
    "B": ["11110", "10001", "11110", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "11110", "10000", "11111"],
    "F": ["11111", "10000", "11110", "10000", "10000"],
    "G": ["01111", "10000", "10111", "10001", "01110"],
    "H": ["10001", "10001", "11111", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00001", "00001", "10001", "01110"],
    "K": ["10001", "10010", "11100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001"],
    "O": ["01110", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "11110", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10010", "01101"],
    "R": ["11110", "10001", "11110", "10010", "10001"],
    "S": ["01111", "10000", "01110", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10101", "11011", "10001"],
    "X": ["10001", "01010", "00100", "01010", "10001"],
    "Y": ["10001", "01010", "00100", "00100", "00100"],
    "Z": ["11111", "00010", "00100", "01000", "11111"],
    "0": ["01110", "10001", "10001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00010", "00100", "11111"],
    "3": ["11110", "00001", "00110", "00001", "11110"],
    "4": ["10001", "10001", "11111", "00001", "00001"],
    "5": ["11111", "10000", "11110", "00001", "11110"],
    "6": ["01110", "10000", "11110", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "00100"],
    "8": ["01110", "10001", "01110", "10001", "01110"],
    "9": ["01110", "10001", "01111", "00001", "01110"],
    " ": ["00000", "00000", "00000", "00000", "00000"],
    ">": ["10000", "11000", "11100", "11000", "10000"],
    "-": ["00000", "00000", "11111", "00000", "00000"],
    "/": ["00001", "00010", "00100", "01000", "10000"],
    ":": ["00000", "00100", "00000", "00100", "00000"],
    "!": ["00100", "00100", "00100", "00000", "00100"],
}


def glyph(ch, color=3):
    px = empty()
    key = ch.upper() if ch.isalpha() else ch
    rows = FONT.get(key)
    if not rows:
        return px
    for y, row in enumerate(rows):
        for x, bit in enumerate(row):
            if bit == "1":
                px[y + 1][x + 1] = color
    return px


bg = [empty() for _ in range(256)]
sp = [empty() for _ in range(256)]

# 0 void black
# 1 floor — solid blue (color 2 only, one flat color)
bg[1] = solid(2)

# 2 wall — solid gray (color 1 only)
bg[2] = solid(1)

# 3 goal — blue floor + black hole ring (target), gold outer ticks optional
bg[3] = from_rows(
    [
        "22222222",
        "22000022",
        "20000002",
        "20000002",
        "20000002",
        "20000002",
        "22000022",
        "22222222",
    ]
)

# 4 box — solid gold with black X
bg[4] = from_rows(
    [
        "33333333",
        "30000003",
        "30300303",
        "30033003",
        "30033003",
        "30300303",
        "30000003",
        "33333333",
    ]
)

# 5 box on goal — gold fill + thicker black X (still same gold)
bg[5] = from_rows(
    [
        "33333333",
        "33000033",
        "30300303",
        "30033003",
        "30033003",
        "30300303",
        "33000033",
        "33333333",
    ]
)

# 6 HUD bar dark gray
bg[6] = solid(1)

# 7 panel
bg[7] = solid(1)

# 8 light (floor blue) edge
bg[8] = solid(2)

# BG fonts (gold/white = color 3)
for i, ch in enumerate("0123456789"):
    bg[0x30 + i] = glyph(ch)
for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    bg[0x41 + i] = glyph(ch)
bg[0x2F] = glyph("/")
bg[0x3A] = glyph(":")
bg[0x21] = glyph("!")
bg[0x2D] = glyph("-")
bg[0x3E] = glyph(">")

# player sprite — solid body (palette SPR0: orange)
# color1=outline dark, 2=mid, 3=bright; avoid large transparent holes
# so character does not pick up blue floor through see-through pixels
sp[1] = from_rows(
    [
        ".111111.",
        "13333331",
        "13222231",
        "13233231",
        "13333331",
        "13333331",
        ".13..31.",
        ".1....1.",
    ]
)
for i, ch in enumerate("0123456789"):
    sp[0x10 + i] = glyph(ch)
for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    sp[0x21 + i] = glyph(ch)
sp[0x20] = empty()
sp[0x3E] = glyph(">")
sp[0x2D] = glyph("-")
sp[0x2F] = glyph("/")
sp[0x3A] = glyph(":")

data = bytearray()
for i in range(256):
    data += pack_tile(bg[i])
for i in range(256):
    data += pack_tile(sp[i])
assert len(data) == 8192
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_bytes(data)
print("Wrote", OUT)
