# -*- coding: utf-8 -*-
"""Generate pure Befunge-93 playable Sokoban → sokoban.bf

Wide single-row program (interpreter grows the playfield). Loop via wrap-around.
Quit: writing '@' onto (0,0) so the next wrap hits halt.

Level:
  #####
  #.$@#
  #####
Keys: a/d move, q quit. Solution: a
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
W, H = 5, 3
MY, BY = 2, 5
LEVEL = ["#####", "#.$@#", "#####"]

# vars at (n, 1)
VY = 1
PX, PY, MV = 0, 1, 2
CH, DX, T = 3, 4, 5
NX, OK, CELL, IB = 6, 7, 8, 9
BXA, FREE, CP, CW = 10, 11, 12, 13
FILL, PCH, BCH = 14, 15, 16
FLAG = 17  # (FLAG, VY) first-run marker, char '0'/'1'


def pn(n: int) -> str:
    if n < 0:
        return "0" + pn(-n) + "-"
    if n <= 9:
        return str(n)
    for a in range(9, 1, -1):
        if n % a == 0 and 1 <= n // a <= 9:
            return f"{n // a}{a}*"
    q, r = divmod(n, 9)
    return pn(q) + "9*" + (f"{r}+" if r else "")


def V(a: int) -> str:
    return pn(a) + pn(VY)


def ld(a: int) -> str:
    return V(a) + "g"


def generate() -> str:
    px = py = 0
    for y, row in enumerate(LEVEL):
        for x, c in enumerate(row):
            if c in "@+":
                px, py = x, y

    P: list[str] = []
    e = P.append

    # first-run init if FLAG=='0'
    e(pn(FLAG) + pn(VY) + "g" + pn(48) + "-!" + V(T) + "p")
    e(ld(PX) + pn(px) + "\\-" + ld(T) + "*" + ld(PX) + "+" + V(PX) + "p")
    e(ld(PY) + pn(py) + "\\-" + ld(T) + "*" + ld(PY) + "+" + V(PY) + "p")
    e(ld(MV) + "0\\-" + ld(T) + "*" + ld(MV) + "+" + V(MV) + "p")
    e(pn(49) + pn(FLAG) + pn(VY) + "p")

    # print
    e(pn(10) + ",")
    for y in range(H):
        for x in range(W):
            e(pn(x) + pn(MY + y) + "g,")
        e(pn(10) + ",")
    e(ld(MV) + "." + pn(10) + "," + pn(ord(">")) + ",")
    e("~" + V(CH) + "p")

    # quit: if ch==q, write '@'(64) to (0,0) so wrap hits halt
    e(ld(CH) + pn(ord("q")) + "-!" + V(T) + "p")
    e("00g" + pn(64) + "\\-" + ld(T) + "*" + "00g+" + "00p")

    # also quit on EOF (~ gives 0)
    e(ld(CH) + "!" + V(T) + "p")  # 1 if ch==0
    e("00g" + pn(64) + "\\-" + ld(T) + "*" + "00g+" + "00p")

    # dx / en
    e(ld(CH) + pn(ord("a")) + "-!01-*" + ld(CH) + pn(ord("d")) + "-!+" + V(DX) + "p")
    e(ld(CH) + pn(ord("a")) + "-!" + ld(CH) + pn(ord("d")) + "-!+!!" + V(T) + "p")

    e(ld(PX) + ld(DX) + "+" + V(NX) + "p")
    e("0" + ld(NX) + "`!" + pn(W) + ld(NX) + "`*" + ld(T) + "*" + V(OK) + "p")
    e(ld(NX) + ld(PY) + pn(MY) + "+" + "g" + V(CELL) + "p")
    e(ld(CELL) + pn(35) + "-!!" + ld(OK) + "*" + V(OK) + "p")
    e(ld(CELL) + pn(36) + "-!" + ld(CELL) + pn(42) + "-!+!!" + V(IB) + "p")
    e(ld(NX) + ld(DX) + "+" + V(BXA) + "p")
    e(ld(BXA) + ld(PY) + pn(MY) + "+" + "g:" + pn(32) + "-!\\" + pn(46) + "-!+" + V(FREE) + "p")
    e(
        "0"
        + ld(BXA)
        + "`!"
        + pn(W)
        + ld(BXA)
        + "`*"
        + ld(OK)
        + "*"
        + ld(IB)
        + "*"
        + ld(FREE)
        + "*"
        + V(CP)
        + "p"
    )
    e(ld(CELL) + ":" + pn(32) + "-!\\" + pn(46) + "-!+" + ld(IB) + "!*" + ld(OK) + "*" + V(CW) + "p")

    e(ld(PX) + ld(PY) + pn(BY) + "+" + "g" + V(T) + "p")
    e(ld(T) + pn(46) + "-!" + ld(T) + pn(42) + "-!+" + ld(T) + pn(43) + "-!+!!")
    e(pn(14) + "*" + pn(32) + "+" + V(FILL) + "p")
    e(ld(NX) + ld(PY) + pn(BY) + "+" + "g" + V(T) + "p")
    e(ld(T) + pn(46) + "-!" + ld(T) + pn(42) + "-!+" + ld(T) + pn(43) + "-!+!!")
    e(pn(21) + "*" + pn(64) + "\\-" + V(PCH) + "p")
    e(ld(BXA) + ld(PY) + pn(BY) + "+" + "g" + V(T) + "p")
    e(ld(T) + pn(46) + "-!" + ld(T) + pn(42) + "-!+" + ld(T) + pn(43) + "-!+!!")
    e(pn(6) + "*" + pn(36) + "+" + V(BCH) + "p")

    def blend(xg: str, yg: str, na: int, ca: int) -> None:
        e(xg + yg + pn(MY) + "+" + "g" + V(na) + "g\\-" + V(ca) + "g*")
        e(xg + yg + pn(MY) + "+" + "g+" + xg + yg + pn(MY) + "+" + "p")

    blend(ld(PX), ld(PY), FILL, CW)
    blend(ld(NX), ld(PY), PCH, CW)
    e(ld(PX) + ld(NX) + "\\-" + ld(CW) + "*" + ld(PX) + "+" + V(PX) + "p")
    e(ld(MV) + ld(CW) + "+" + V(MV) + "p")
    blend(ld(PX), ld(PY), FILL, CP)
    blend(ld(NX), ld(PY), PCH, CP)
    blend(ld(BXA), ld(PY), BCH, CP)
    e(ld(PX) + ld(NX) + "\\-" + ld(CP) + "*" + ld(PX) + "+" + V(PX) + "p")
    e(ld(MV) + ld(CP) + "+" + V(MV) + "p")

    # end — IP wraps to 0 (program width = len)
    program = "".join(P)
    print("program length", len(program))

    # row0 = program; row1 = spaces with flag; maps below
    rows: list[str] = [program]
    flag_x = 17
    row1 = [" "] * max(len(program), flag_x + 1)
    row1[flag_x] = "0"
    rows.append("".join(row1))
    while len(rows) < MY + H:
        rows.append("")
    for y, row in enumerate(LEVEL):
        idx = MY + y
        while len(rows) <= idx:
            rows.append("")
        cells = list(rows[idx].ljust(W, " "))
        for x, c in enumerate(row):
            cells[x] = c
        rows[idx] = "".join(cells)
    for y, row in enumerate(LEVEL):
        idx = BY + y
        while len(rows) <= idx:
            rows.append("")
        cells = list(rows[idx].ljust(W, " "))
        for x, c in enumerate(row):
            cells[x] = c
        rows[idx] = "".join(cells)

    return "\n".join(rows) + "\n"


def main() -> None:
    text = generate()
    path = HERE / "sokoban.bf"
    path.write_text(text, encoding="utf-8")
    print("wrote", path, "size", len(text))


if __name__ == "__main__":
    main()
