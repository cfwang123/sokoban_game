#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""aplapp1 - APL teaching: Python driver + APL source sketch."""
from __future__ import annotations

LEVEL = [
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
]


def key(x: int, y: int) -> str:
    return f"{x},{y}"


def from_rows(rows: list[str]):
    walls, goals, boxes = set(), set(), set()
    px = py = max_x = max_y = 0
    for y, row in enumerate(rows):
        max_y = y
        for x, ch in enumerate(row):
            max_x = max(max_x, x)
            k = key(x, y)
            if ch == "#":
                walls.add(k)
            elif ch == ".":
                goals.add(k)
            elif ch == "$":
                boxes.add(k)
            elif ch == "*":
                boxes.add(k)
                goals.add(k)
            elif ch == "@":
                px, py = x, y
            elif ch == "+":
                px, py = x, y
                goals.add(k)
    return {
        "walls": walls,
        "goals": goals,
        "boxes": boxes,
        "px": px,
        "py": py,
        "moves": 0,
        "won": False,
        "w": max_x + 1,
        "h": max_y + 1,
        "hist": [],
    }


def check_win(s):
    s["won"] = all(b in s["goals"] for b in s["boxes"])


def try_move(s, dx, dy):
    if s["won"]:
        return
    nx, ny = s["px"] + dx, s["py"] + dy
    nk = key(nx, ny)
    if nk in s["walls"]:
        return
    if nk in s["boxes"]:
        bx, by = nx + dx, ny + dy
        bk = key(bx, by)
        if bk in s["walls"] or bk in s["boxes"]:
            return
        s["hist"].append((s["px"], s["py"], nk, bk))
        s["boxes"].discard(nk)
        s["boxes"].add(bk)
        s["px"], s["py"] = nx, ny
        s["moves"] += 1
        check_win(s)
        return
    s["hist"].append((s["px"], s["py"], None, None))
    s["px"], s["py"] = nx, ny


def undo(s):
    if s["won"] or not s["hist"]:
        return
    while s["hist"]:
        hx, hy, bf, bt = s["hist"].pop()
        if bf is not None:
            s["px"], s["py"] = hx, hy
            s["boxes"].discard(bt)
            s["boxes"].add(bf)
            if s["moves"] > 0:
                s["moves"] -= 1
            s["won"] = False
            return
        s["px"], s["py"] = hx, hy


def render(s) -> str:
    lines = []
    for y in range(s["h"]):
        row = []
        for x in range(s["w"]):
            k = key(x, y)
            if s["px"] == x and s["py"] == y:
                row.append("+" if k in s["goals"] else "@")
            elif k in s["boxes"]:
                row.append("*" if k in s["goals"] else "$")
            elif k in s["walls"]:
                row.append("#")
            elif k in s["goals"]:
                row.append(".")
            else:
                row.append(" ")
        lines.append("".join(row))
    return "\n".join(lines) + "\n"


def main():
    print("sokoban_apl — wasd 移动, z 撤销, r 重置, q 退出")
    print("(Python 教学驱动；原生 APL 见 sokoban.apl)")
    s = from_rows(LEVEL)
    while True:
        print()
        print(render(s), end="")
        flag = " WIN!" if s["won"] else ""
        print(f"moves={s['moves']}{flag}")
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        ch = line[0].lower()
        if ch == "w":
            try_move(s, 0, -1)
        elif ch == "s":
            try_move(s, 0, 1)
        elif ch == "a":
            try_move(s, -1, 0)
        elif ch == "d":
            try_move(s, 1, 0)
        elif ch == "z":
            undo(s)
        elif ch == "r":
            s = from_rows(LEVEL)
        elif ch == "q":
            break
        if s["won"]:
            print("Level clear!")


if __name__ == "__main__":
    main()
