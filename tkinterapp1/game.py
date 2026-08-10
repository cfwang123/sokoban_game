# -*- coding: utf-8 -*-
"""推箱子核心（Tkinter / PyQt 等 Python GUI 共用教学逻辑）。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple


def cell_key(x: int, y: int) -> str:
    return f"{x},{y}"


@dataclass
class Hist:
    player: Tuple[int, int]
    box_from: Optional[str] = None
    box_to: Optional[str] = None


@dataclass
class GameState:
    walls: Set[str] = field(default_factory=set)
    goals: Set[str] = field(default_factory=set)
    boxes: Set[str] = field(default_factory=set)
    player: Tuple[int, int] = (0, 0)
    moves: int = 0
    won: bool = False
    width: int = 0
    height: int = 0
    hist: List[Hist] = field(default_factory=list)

    @classmethod
    def from_rows(cls, rows: List[str]) -> "GameState":
        s = cls()
        max_x = max_y = 0
        for y, row in enumerate(rows):
            max_y = y
            for x, ch in enumerate(row):
                max_x = max(max_x, x)
                k = cell_key(x, y)
                if ch == "#":
                    s.walls.add(k)
                elif ch == ".":
                    s.goals.add(k)
                elif ch == "$":
                    s.boxes.add(k)
                elif ch == "*":
                    s.boxes.add(k)
                    s.goals.add(k)
                elif ch == "@":
                    s.player = (x, y)
                elif ch == "+":
                    s.player = (x, y)
                    s.goals.add(k)
        s.width = max_x + 1
        s.height = max_y + 1
        return s

    def try_move(self, dx: int, dy: int) -> bool:
        if self.won:
            return False
        px, py = self.player
        nx, ny = px + dx, py + dy
        nk = cell_key(nx, ny)
        if nk in self.walls:
            return False
        if nk in self.boxes:
            bx, by = nx + dx, ny + dy
            bk = cell_key(bx, by)
            if bk in self.walls or bk in self.boxes:
                return False
            self.hist.append(Hist(self.player, nk, bk))
            self.boxes.discard(nk)
            self.boxes.add(bk)
            self.player = (nx, ny)
            self.moves += 1
            self.won = all(b in self.goals for b in self.boxes)
            return True
        self.hist.append(Hist(self.player))
        self.player = (nx, ny)
        return True

    def undo(self) -> bool:
        if self.won or not self.hist:
            return False
        entry: Optional[Hist] = None
        while self.hist:
            entry = self.hist.pop()
            if entry.box_from is not None:
                break
            self.player = entry.player
        if entry is None or entry.box_from is None:
            return True
        self.player = entry.player
        assert entry.box_to is not None
        self.boxes.discard(entry.box_to)
        self.boxes.add(entry.box_from)
        if self.moves > 0:
            self.moves -= 1
        self.won = False
        return True


LEVEL = [
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
]
