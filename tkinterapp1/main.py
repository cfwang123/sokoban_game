#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tkinterapp1 — Tkinter 推箱子（标准库 GUI，教学）

运行（无需编译）:
  python -X utf8 main.py

键位: WASD / 方向键, Z 撤销, R 重置, Q/Esc 退出
"""
from __future__ import annotations

import tkinter as tk

from game import LEVEL, GameState, cell_key

CELL = 40
PAD = 16


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sokoban Tkinter")
        self.state = GameState.from_rows(LEVEL)
        w = PAD * 2 + self.state.width * CELL
        h = PAD * 2 + self.state.height * CELL + 28
        self.canvas = tk.Canvas(self, width=w, height=h, bg="#1a1a2e", highlightthickness=0)
        self.canvas.pack()
        self.bind("<Key>", self.on_key)
        self.draw()
        self.focus_force()

    def draw(self) -> None:
        c = self.canvas
        c.delete("all")
        s = self.state
        for y in range(s.height):
            for x in range(s.width):
                k = cell_key(x, y)
                x0, y0 = PAD + x * CELL, PAD + y * CELL
                x1, y1 = x0 + CELL, y0 + CELL
                if k in s.walls:
                    c.create_rectangle(x0, y0, x1, y1, fill="#4a4a6a", outline="")
                else:
                    c.create_rectangle(x0, y0, x1, y1, fill="#3a3a55", outline="#444466")
                    if k in s.goals:
                        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
                        c.create_oval(cx - 6, cy - 6, cx + 6, cy + 6, fill="#e94560", outline="")
                    if k in s.boxes:
                        on = k in s.goals
                        c.create_rectangle(
                            x0 + 4, y0 + 4, x1 - 4, y1 - 4,
                            fill="#2ecc71" if on else "#f39c12", outline="",
                        )
                if s.player == (x, y):
                    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
                    r = int(CELL * 0.35)
                    c.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#3498db", outline="")
        flag = " WIN" if s.won else ""
        c.create_text(
            8, PAD + s.height * CELL + 14,
            anchor="w", fill="white",
            text=f"moves={s.moves}{flag}  WASD Z R Q",
            font=("Segoe UI", 10),
        )

    def on_key(self, e: tk.Event) -> None:
        key = (e.keysym or "").lower()
        if key in ("w", "up"):
            self.state.try_move(0, -1)
        elif key in ("s", "down"):
            self.state.try_move(0, 1)
        elif key in ("a", "left"):
            self.state.try_move(-1, 0)
        elif key in ("d", "right"):
            self.state.try_move(1, 0)
        elif key == "z":
            self.state.undo()
        elif key == "r":
            self.state = GameState.from_rows(LEVEL)
        elif key in ("q", "escape"):
            self.destroy()
            return
        self.draw()


def main() -> None:
    App().mainloop()


if __name__ == "__main__":
    main()
