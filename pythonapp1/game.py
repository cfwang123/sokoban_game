"""推箱子核心逻辑（Python 教学）。"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


def key(x: int, y: int) -> str:
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
    level_index: int = 0
    hist: List[Hist] = field(default_factory=list)

    @classmethod
    def from_rows(cls, rows: List[str], index: int = 0) -> "GameState":
        s = cls(level_index=index)
        max_x = max_y = 0
        for y, row in enumerate(rows):
            max_y = y
            for x, ch in enumerate(row):
                max_x = max(max_x, x)
                k = key(x, y)
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
                # 空格 / '-' 为空地
        s.width = max_x + 1
        s.height = max_y + 1
        return s

    def try_move(self, dx: int, dy: int) -> bool:
        if self.won:
            return False
        px, py = self.player
        nx, ny = px + dx, py + dy
        nk = key(nx, ny)
        if nk in self.walls:
            return False
        if nk in self.boxes:
            bx, by = nx + dx, ny + dy
            bk = key(bx, by)
            if bk in self.walls or bk in self.boxes:
                return False
            self.hist.append(Hist(self.player, nk, bk))
            self.boxes.discard(nk)
            self.boxes.add(bk)
            self.player = (nx, ny)
            self.moves += 1
            self._check_win()
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

    def _check_win(self) -> None:
        self.won = all(b in self.goals for b in self.boxes)

    def render_ascii(self) -> str:
        lines: List[str] = []
        for y in range(self.height):
            row: List[str] = []
            for x in range(self.width):
                k = key(x, y)
                if self.player == (x, y):
                    row.append("+" if k in self.goals else "@")
                elif k in self.boxes:
                    row.append("*" if k in self.goals else "$")
                elif k in self.walls:
                    row.append("#")
                elif k in self.goals:
                    row.append(".")
                else:
                    row.append(" ")
            lines.append("".join(row))
        return "\n".join(lines) + "\n"


def find_path(state: GameState, tx: int, ty: int) -> Optional[List[Tuple[int, int]]]:
    """BFS 寻路，返回 (dx, dy) 列表。"""
    sx, sy = state.player
    if (sx, sy) == (tx, ty):
        return []
    blocked = set(state.walls) | set(state.boxes)
    start = key(sx, sy)
    target = key(tx, ty)
    q: deque = deque([(sx, sy)])
    visited = {start}
    parent: Dict[str, Tuple[str, int, int]] = {}
    dirs = ((0, -1), (0, 1), (-1, 0), (1, 0))
    while q:
        cx, cy = q.popleft()
        ck = key(cx, cy)
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            nk = key(nx, ny)
            if nk in blocked or nk in visited:
                continue
            visited.add(nk)
            parent[nk] = (ck, dx, dy)
            if nk == target:
                path: List[Tuple[int, int]] = []
                p = nk
                while p != start:
                    from_k, ddx, ddy = parent[p]
                    path.append((ddx, ddy))
                    p = from_k
                path.reverse()
                return path
            q.append((nx, ny))
    return None
