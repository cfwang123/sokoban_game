#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Befunge-93 dialect interpreter for pure sokoban.bf.

Instruction set matches classic Befunge-93; playfield is sized to the source
(classic 80×25 is too small for the full interactive program).
"""
from __future__ import annotations

import random
import sys
from typing import List, Optional, TextIO


def load_bf_text(raw: str) -> str:
    lines = []
    for line in raw.splitlines():
        if line.strip().startswith(";;"):
            continue
        lines.append(line)
    while lines and lines[0].strip() == "":
        lines.pop(0)
    return "\n".join(lines)


class Befunge93:
    def __init__(
        self,
        source: str = "",
        stdin: Optional[TextIO] = None,
        stdout: Optional[TextIO] = None,
        *,
        max_steps: int = 100_000_000,
        min_width: int = 80,
        min_height: int = 25,
    ) -> None:
        self.stdin = stdin if stdin is not None else sys.stdin
        self.stdout = stdout if stdout is not None else sys.stdout
        self.max_steps = max_steps
        self.min_width = min_width
        self.min_height = min_height
        self.stack: List[int] = []
        self.x = 0
        self.y = 0
        self.dx = 1
        self.dy = 0
        self.stringmode = False
        self.output: list[str] = []
        self.w = min_width
        self.h = min_height
        self.grid: List[List[int]] = [[ord(" ")] * self.w for _ in range(self.h)]
        if source:
            self.load(source)

    def load(self, source: str) -> None:
        lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        while lines and lines[-1] == "":
            lines.pop()
        if not lines:
            lines = [""]
        need_w = max(self.min_width, max(len(ln) for ln in lines))
        need_h = max(self.min_height, len(lines) + 40)
        self.w, self.h = need_w, need_h
        self.grid = [[ord(" ")] * self.w for _ in range(self.h)]
        for y, line in enumerate(lines):
            if y >= self.h:
                break
            for x, ch in enumerate(line):
                if x < self.w:
                    self.grid[y][x] = ord(ch)

    def push(self, v: int) -> None:
        self.stack.append(int(v))

    def pop(self) -> int:
        return self.stack.pop() if self.stack else 0

    def cell(self, x: int, y: int) -> int:
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.grid[y][x]
        return 0

    def put_cell(self, x: int, y: int, v: int) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            self.grid[y][x] = int(v) & 0xFF

    def _write(self, s: str) -> None:
        self.output.append(s)
        self.stdout.write(s)
        self.stdout.flush()

    def step(self) -> bool:
        c = self.grid[self.y][self.x]
        ch = chr(c) if 0 <= c < 128 else "?"

        if self.stringmode:
            if ch == '"':
                self.stringmode = False
            else:
                self.push(c)
        else:
            if ch == " ":
                pass
            elif ch in "0123456789":
                self.push(ord(ch) - ord("0"))
            elif ch == "+":
                a, b = self.pop(), self.pop()
                self.push(b + a)
            elif ch == "-":
                a, b = self.pop(), self.pop()
                self.push(b - a)
            elif ch == "*":
                a, b = self.pop(), self.pop()
                self.push(b * a)
            elif ch == "/":
                a, b = self.pop(), self.pop()
                self.push(0 if a == 0 else int(b / a))
            elif ch == "%":
                a, b = self.pop(), self.pop()
                self.push(0 if a == 0 else b % a)
            elif ch == "!":
                self.push(0 if self.pop() else 1)
            elif ch == "`":
                a, b = self.pop(), self.pop()
                self.push(1 if b > a else 0)
            elif ch == ">":
                self.dx, self.dy = 1, 0
            elif ch == "<":
                self.dx, self.dy = -1, 0
            elif ch == "^":
                self.dx, self.dy = 0, -1
            elif ch == "v":
                self.dx, self.dy = 0, 1
            elif ch == "?":
                self.dx, self.dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            elif ch == "_":
                self.dx, self.dy = ((1, 0) if self.pop() == 0 else (-1, 0))
            elif ch == "|":
                self.dx, self.dy = ((0, 1) if self.pop() == 0 else (0, -1))
            elif ch == '"':
                self.stringmode = True
            elif ch == ":":
                v = self.pop()
                self.push(v)
                self.push(v)
            elif ch == "\\":
                a, b = self.pop(), self.pop()
                self.push(a)
                self.push(b)
            elif ch == "$":
                self.pop()
            elif ch == ".":
                self._write(str(self.pop()))
            elif ch == ",":
                self._write(chr(self.pop() & 0xFF))
            elif ch == "#":
                self.x = (self.x + self.dx) % self.w
                self.y = (self.y + self.dy) % self.h
            elif ch == "g":
                y, x = self.pop(), self.pop()
                self.push(self.cell(x, y))
            elif ch == "p":
                y, x, v = self.pop(), self.pop(), self.pop()
                self.put_cell(x, y, v)
            elif ch == "&":
                buf = ""
                while True:
                    ch_in = self.stdin.read(1)
                    if ch_in == "":
                        break
                    if ch_in in "+-" and not buf:
                        buf += ch_in
                    elif ch_in.isdigit():
                        buf += ch_in
                    elif buf:
                        break
                try:
                    self.push(int(buf) if buf and buf not in "+-" else 0)
                except ValueError:
                    self.push(0)
            elif ch == "~":
                ch_in = self.stdin.read(1)
                self.push(ord(ch_in) if ch_in else 0)
            elif ch == "@":
                return False

        self.x = (self.x + self.dx) % self.w
        self.y = (self.y + self.dy) % self.h
        return True

    def run(self) -> str:
        for _ in range(self.max_steps):
            if not self.step():
                break
        else:
            raise RuntimeError(f"Befunge exceeded {self.max_steps} steps")
        return "".join(self.output)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: befunge93.py <file.bf>", file=sys.stderr)
        return 2
    with open(sys.argv[1], encoding="utf-8", errors="replace") as f:
        src = load_bf_text(f.read())
    Befunge93(src).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
