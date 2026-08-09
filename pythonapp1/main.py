#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pythonapp1 — 推箱子终端版（教学）。"""

from game import GameState

LEVEL = [
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
]


def main() -> None:
    state = GameState.from_rows(LEVEL, 0)
    print("sokoban_python — wasd 移动, z 撤销, r 重置, q 退出")
    while True:
        print()
        print(state.render_ascii(), end="")
        flag = " WIN!" if state.won else ""
        print(f"moves={state.moves}{flag}")
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        ch = line[0].lower()
        if ch == "w":
            state.try_move(0, -1)
        elif ch == "s":
            state.try_move(0, 1)
        elif ch == "a":
            state.try_move(-1, 0)
        elif ch == "d":
            state.try_move(1, 0)
        elif ch == "z":
            state.undo()
        elif ch == "r":
            state = GameState.from_rows(LEVEL, 0)
        elif ch == "q":
            break
        if state.won:
            print("Level clear!")


if __name__ == "__main__":
    main()
