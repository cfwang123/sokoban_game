#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sqlapp1 - SQLite sokoban teaching: state in DB."""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
DB = DIR / "sokoban.db"

LEVEL = [
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
]


def connect() -> sqlite3.Connection:
    if DB.exists():
        DB.unlink()
    conn = sqlite3.connect(DB)
    conn.executescript((DIR / "schema.sql").read_text(encoding="utf-8"))
    load_level(conn)
    return conn


def load_level(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM cell")
    conn.execute("DELETE FROM player")
    conn.execute("DELETE FROM hist")
    conn.execute("UPDATE meta SET moves=0, won=0 WHERE id=1")
    px = py = 0
    for y, row in enumerate(LEVEL):
        for x, ch in enumerate(row):
            if ch == "#":
                kind = "wall"
            elif ch == ".":
                kind = "goal"
            elif ch == "$":
                kind = "box"
            elif ch == "*":
                kind = "box_goal"
            elif ch == "@":
                kind = "floor"
                px, py = x, y
            elif ch == "+":
                kind = "goal"
                px, py = x, y
            else:
                kind = "floor"
            conn.execute("INSERT INTO cell(x,y,kind) VALUES(?,?,?)", (x, y, kind))
    conn.execute("INSERT INTO player(id,x,y) VALUES(1,?,?)", (px, py))
    conn.commit()


def kind_at(conn: sqlite3.Connection, x: int, y: int) -> str | None:
    row = conn.execute("SELECT kind FROM cell WHERE x=? AND y=?", (x, y)).fetchone()
    return row[0] if row else None


def set_kind(conn: sqlite3.Connection, x: int, y: int, kind: str) -> None:
    conn.execute("UPDATE cell SET kind=? WHERE x=? AND y=?", (kind, x, y))


def render(conn: sqlite3.Connection) -> str:
    px, py = conn.execute("SELECT x,y FROM player WHERE id=1").fetchone()
    moves, won = conn.execute("SELECT moves,won FROM meta WHERE id=1").fetchone()
    rows = conn.execute(
        "SELECT x,y,kind FROM cell ORDER BY y,x"
    ).fetchall()
    if not rows:
        return ""
    max_x = max(r[0] for r in rows)
    max_y = max(r[1] for r in rows)
    grid = {(x, y): k for x, y, k in rows}
    lines = []
    for y in range(max_y + 1):
        line = []
        for x in range(max_x + 1):
            k = grid.get((x, y), "floor")
            if x == px and y == py:
                line.append("+" if k in ("goal", "box_goal") else "@")
            elif k == "wall":
                line.append("#")
            elif k == "box":
                line.append("$")
            elif k == "box_goal":
                line.append("*")
            elif k == "goal":
                line.append(".")
            else:
                line.append(" ")
        lines.append("".join(line))
    flag = " WIN!" if won else ""
    lines.append(f"moves={moves}{flag}")
    return "\n".join(lines) + "\n"


def try_move(conn: sqlite3.Connection, dx: int, dy: int) -> bool:
    won = conn.execute("SELECT won FROM meta WHERE id=1").fetchone()[0]
    if won:
        return False
    px, py = conn.execute("SELECT x,y FROM player WHERE id=1").fetchone()
    nx, ny = px + dx, py + dy
    dk = kind_at(conn, nx, ny)
    if dk is None or dk == "wall":
        return False
    if dk in ("box", "box_goal"):
        bx, by = nx + dx, ny + dy
        bk = kind_at(conn, bx, by)
        if bk is None or bk in ("wall", "box", "box_goal"):
            return False
        conn.execute(
            "INSERT INTO hist(px,py,bfx,bfy,btx,bty,is_push) VALUES(?,?,?,?,?,?,1)",
            (px, py, nx, ny, bx, by),
        )
        set_kind(conn, nx, ny, "goal" if dk == "box_goal" else "floor")
        set_kind(conn, bx, by, "box_goal" if bk == "goal" else "box")
        conn.execute("UPDATE player SET x=?, y=? WHERE id=1", (nx, ny))
        conn.execute("UPDATE meta SET moves = moves + 1 WHERE id=1")
        # win?
        left = conn.execute(
            "SELECT COUNT(*) FROM cell WHERE kind='box'"
        ).fetchone()[0]
        if left == 0:
            conn.execute("UPDATE meta SET won=1 WHERE id=1")
        conn.commit()
        return True
    conn.execute(
        "INSERT INTO hist(px,py,bfx,bfy,btx,bty,is_push) VALUES(?,?,NULL,NULL,NULL,NULL,0)",
        (px, py),
    )
    conn.execute("UPDATE player SET x=?, y=? WHERE id=1", (nx, ny))
    conn.commit()
    return True


def undo(conn: sqlite3.Connection) -> bool:
    won = conn.execute("SELECT won FROM meta WHERE id=1").fetchone()[0]
    if won:
        return False
    while True:
        row = conn.execute(
            "SELECT id,px,py,bfx,bfy,btx,bty,is_push FROM hist ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if not row:
            return False
        hid, px, py, bfx, bfy, btx, bty, is_push = row
        conn.execute("DELETE FROM hist WHERE id=?", (hid,))
        if is_push:
            conn.execute("UPDATE player SET x=?, y=? WHERE id=1", (px, py))
            # remove box from to
            tk = kind_at(conn, btx, bty)
            set_kind(conn, btx, bty, "goal" if tk == "box_goal" else "floor")
            fk = kind_at(conn, bfx, bfy)
            set_kind(conn, bfx, bfy, "box_goal" if fk == "goal" else "box")
            conn.execute(
                "UPDATE meta SET moves = CASE WHEN moves>0 THEN moves-1 ELSE 0 END, won=0 WHERE id=1"
            )
            conn.commit()
            return True
        conn.execute("UPDATE player SET x=?, y=? WHERE id=1", (px, py))
        conn.commit()


def main() -> None:
    conn = connect()
    print("sokoban_sql — wasd 移动, z 撤销, r 重置, q 退出")
    print("(SQLite DB:", DB, ")")
    while True:
        print()
        print(render(conn), end="")
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        ch = line[0].lower()
        if ch == "w":
            try_move(conn, 0, -1)
        elif ch == "s":
            try_move(conn, 0, 1)
        elif ch == "a":
            try_move(conn, -1, 0)
        elif ch == "d":
            try_move(conn, 1, 0)
        elif ch == "z":
            undo(conn)
        elif ch == "r":
            load_level(conn)
        elif ch == "q":
            break
        won = conn.execute("SELECT won FROM meta WHERE id=1").fetchone()[0]
        if won:
            print("Level clear!")


if __name__ == "__main__":
    main()
