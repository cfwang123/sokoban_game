#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate brainfuckapp1/sokoban.bf (compact).

- Dispatch sets ACT / DX / DY; try_move & undo exist once.
- Map load/store unrolled once per call site (few sites).
- Hist select only copies registers (map I/O outside hist index loop).
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "brainfuckapp1" / "sokoban.bf"

LEVEL = [
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
]
W = H = 7

SCR_TOP = 15
RUN, CMD = 16, 17
PX, PY = 18, 19
MOVES, WON, HISTN = 20, 21, 22
DX, DY = 23, 24
NX, NY, BX, BY = 25, 26, 27, 28
IDX, TOI, FRI = 29, 30, 31
TILE, TMPV = 32, 33
ABORT, ISBOX, FLAG = 34, 35, 36
LOOP, ACT = 37, 38
MAP0 = 50
HIST0 = 200
ESZ = 5
MAXHIST = 32


def tile_of(ch: str) -> int:
    return {" ": 0, "#": 1, ".": 2, "$": 3, "*": 4, "@": 0, "+": 2}[ch]


def find_player() -> tuple[int, int]:
    for y, row in enumerate(LEVEL):
        for x, ch in enumerate(row):
            if ch in "@+":
                return x, y
    return 1, 1


class BF:
    def __init__(self) -> None:
        self.p = 0
        self.out: list[str] = []
        self.sp = SCR_TOP

    def emit(self, s: str) -> None:
        self.out.append(s)

    def go(self, c: int) -> None:
        d = c - self.p
        if d > 0:
            self.emit(">" * d)
        elif d < 0:
            self.emit("<" * (-d))
        self.p = c

    def clear(self, c: int) -> None:
        self.go(c)
        self.emit("[-]")

    def add(self, c: int, n: int) -> None:
        self.go(c)
        if n > 0:
            self.emit("+" * n)
        elif n < 0:
            self.emit("-" * (-n))

    def set(self, c: int, n: int) -> None:
        self.clear(c)
        if n:
            self.emit("+" * n)

    def alloc(self) -> int:
        if self.sp < 0:
            raise RuntimeError("scratch exhausted")
        c = self.sp
        self.sp -= 1
        return c

    def free(self, n: int = 1) -> None:
        self.sp += n

    def copy(self, src: int, dst: int) -> None:
        tmp = self.alloc()
        self.clear(dst)
        self.clear(tmp)
        self.go(src)
        self.emit("[-")
        self.go(dst)
        self.emit("+")
        self.go(tmp)
        self.emit("+")
        self.go(src)
        self.emit("]")
        self.go(tmp)
        self.emit("[-")
        self.go(src)
        self.emit("+")
        self.go(tmp)
        self.emit("]")
        self.free()

    def move_add(self, src: int, dst: int) -> None:
        """dst += src; src = 0. For applying DX (incl. 255 as -1)."""
        self.go(src)
        self.emit("[-")
        self.go(dst)
        self.emit("+")
        self.go(src)
        self.emit("]")

    def add_from(self, src: int, dst: int) -> None:
        """dst += src (preserve src)."""
        t = self.alloc()
        self.copy(src, t)
        self.move_add(t, dst)
        self.free()

    def eq(self, cell: int, val: int, res: int) -> None:
        t = self.alloc()
        self.copy(cell, t)
        self.set(res, 1)
        self.go(t)
        if val:
            self.emit("-" * val)
        self.emit("[[-]")
        self.go(res)
        self.emit("[-]")
        self.go(t)
        self.emit("]")
        self.free()

    def if_(self, cell: int, body) -> None:
        flag = self.alloc()
        self.copy(cell, flag)
        self.go(flag)
        self.emit("[")
        body()
        self.go(flag)
        self.emit("[-]")
        self.emit("]")
        self.p = flag
        self.free()

    def if_not(self, cell: int, body) -> None:
        inv = self.alloc()
        self.set(inv, 1)
        self.if_(cell, lambda: self.clear(inv))
        self.if_(inv, body)
        self.free()

    def putc(self, ch: str) -> None:
        t = self.alloc()
        self.set(t, ord(ch))
        self.go(t)
        self.emit(".")
        self.clear(t)
        self.free()

    def puts(self, s: str) -> None:
        for ch in s:
            self.putc(ch)

    def code(self) -> str:
        return "".join(self.out)


def build() -> str:
    g = BF()
    px0, py0 = find_player()

    def load_map(idx: int, dest: int) -> None:
        for i in range(W * H):
            f = g.alloc()
            g.eq(idx, i, f)
            g.go(f)
            g.emit("[")
            g.copy(MAP0 + i, dest)
            g.go(f)
            g.emit("[-]")
            g.emit("]")
            g.p = f
            g.free()

    def store_map(idx: int, src: int) -> None:
        for i in range(W * H):
            f = g.alloc()
            g.eq(idx, i, f)
            g.go(f)
            g.emit("[")
            g.copy(src, MAP0 + i)
            g.go(f)
            g.emit("[-]")
            g.emit("]")
            g.p = f
            g.free()

    def xy_idx(x: int, y: int, out: int) -> None:
        g.copy(y, out)
        t = g.alloc()
        g.clear(t)
        g.go(out)
        g.emit("[-")
        g.go(t)
        g.emit("+++++++")
        g.go(out)
        g.emit("]")
        g.go(t)
        g.emit("[-")
        g.go(out)
        g.emit("+")
        g.go(t)
        g.emit("]")
        g.add_from(x, out)
        g.free()

    def check_win() -> None:
        g.set(WON, 1)
        for i in range(W * H):
            f = g.alloc()
            g.eq(MAP0 + i, 3, f)
            g.if_(f, lambda: g.clear(WON))
            g.free()

    def hist_write(is_push: bool) -> None:
        """Append current PX,PY[,FRI,TOI] at HISTN+1."""
        g.add(HISTN, 1)
        ncell = g.alloc()
        g.copy(HISTN, ncell)
        for n in range(1, MAXHIST + 1):
            f = g.alloc()
            g.eq(ncell, n, f)
            b = HIST0 + (n - 1) * ESZ

            def body(base=b, psh=is_push) -> None:
                g.copy(PX, base)
                g.copy(PY, base + 1)
                g.set(base + 2, 1 if psh else 0)
                if psh:
                    g.copy(FRI, base + 3)
                    g.copy(TOI, base + 4)
                else:
                    g.clear(base + 3)
                    g.clear(base + 4)

            g.go(f)
            g.emit("[")
            body()
            g.go(f)
            g.emit("[-]")
            g.emit("]")
            g.p = f
            g.free()
        g.free()

    def hist_read_top() -> None:
        """Load entry HISTN into NX,NY,ISBOX,FRI,TOI."""
        ncell = g.alloc()
        g.copy(HISTN, ncell)
        for n in range(1, MAXHIST + 1):
            f = g.alloc()
            g.eq(ncell, n, f)
            b = HIST0 + (n - 1) * ESZ

            def body(base=b) -> None:
                g.copy(base, NX)
                g.copy(base + 1, NY)
                g.copy(base + 2, ISBOX)
                g.copy(base + 3, FRI)
                g.copy(base + 4, TOI)

            g.go(f)
            g.emit("[")
            body()
            g.go(f)
            g.emit("[-]")
            g.emit("]")
            g.p = f
            g.free()
        g.free()

    def try_move() -> None:
        g.clear(ABORT)
        g.if_(WON, lambda: g.set(ABORT, 1))
        g.copy(PX, NX)
        g.add_from(DX, NX)
        g.copy(PY, NY)
        g.add_from(DY, NY)
        xy_idx(NX, NY, IDX)
        load_map(IDX, TILE)
        f = g.alloc()
        g.eq(TILE, 1, f)
        g.if_(f, lambda: g.set(ABORT, 1))
        g.free()

        g.clear(ISBOX)
        for v in (3, 4):
            f = g.alloc()
            g.eq(TILE, v, f)
            g.if_(f, lambda: g.set(ISBOX, 1))
            g.free()

        def do_push() -> None:
            g.copy(NX, BX)
            g.add_from(DX, BX)
            g.copy(NY, BY)
            g.add_from(DY, BY)
            xy_idx(BX, BY, TOI)
            load_map(TOI, TMPV)
            for v in (1, 3, 4):
                ff = g.alloc()
                g.eq(TMPV, v, ff)
                g.if_(ff, lambda: g.set(ABORT, 1))
                g.free()

            def apply_push() -> None:
                g.copy(IDX, FRI)
                hist_write(True)
                ff = g.alloc()
                g.eq(TILE, 4, ff)
                g.set(TMPV, 0)
                g.if_(ff, lambda: g.set(TMPV, 2))
                g.free()
                store_map(FRI, TMPV)
                load_map(TOI, TILE)
                ff = g.alloc()
                g.eq(TILE, 2, ff)
                g.set(TMPV, 3)
                g.if_(ff, lambda: g.set(TMPV, 4))
                g.free()
                store_map(TOI, TMPV)
                g.copy(NX, PX)
                g.copy(NY, PY)
                g.add(MOVES, 1)
                check_win()

            g.if_not(ABORT, apply_push)

        def do_walk() -> None:
            def apply_walk() -> None:
                hist_write(False)
                g.copy(NX, PX)
                g.copy(NY, PY)

            g.if_not(ABORT, apply_walk)

        def handle() -> None:
            g.if_(ISBOX, do_push)
            g.if_not(ISBOX, do_walk)

        g.if_not(ABORT, handle)

    def undo() -> None:
        g.clear(ABORT)
        g.if_(WON, lambda: g.set(ABORT, 1))
        f = g.alloc()
        g.eq(HISTN, 0, f)
        g.if_(f, lambda: g.set(ABORT, 1))
        g.free()
        g.clear(FLAG)

        def one_step() -> None:
            hist_read_top()
            g.add(HISTN, -1)

            def push_undo() -> None:
                g.copy(NX, PX)
                g.copy(NY, PY)
                load_map(TOI, TILE)
                f3 = g.alloc()
                g.eq(TILE, 4, f3)
                g.set(TMPV, 0)
                g.if_(f3, lambda: g.set(TMPV, 2))
                g.free()
                store_map(TOI, TMPV)
                load_map(FRI, TILE)
                f3 = g.alloc()
                g.eq(TILE, 2, f3)
                g.set(TMPV, 3)
                g.if_(f3, lambda: g.set(TMPV, 4))
                g.free()
                store_map(FRI, TMPV)
                g.if_(MOVES, lambda: g.add(MOVES, -1))
                g.clear(WON)
                g.set(FLAG, 1)

            def walk_undo() -> None:
                g.copy(NX, PX)
                g.copy(NY, PY)

            g.if_(ISBOX, push_undo)
            g.if_not(ISBOX, walk_undo)

        g.set(LOOP, 1)
        g.go(LOOP)
        g.emit("[")
        g.clear(LOOP)
        stop = g.alloc()
        g.copy(ABORT, stop)
        g.if_(FLAG, lambda: g.set(stop, 1))
        f0 = g.alloc()
        g.eq(HISTN, 0, f0)
        g.if_(f0, lambda: g.set(stop, 1))
        g.free()
        cont = g.alloc()
        g.set(cont, 1)
        g.if_(stop, lambda: g.clear(cont))
        g.if_(cont, lambda: (one_step(), g.set(LOOP, 1)))
        g.free()
        g.free()
        g.go(LOOP)
        g.emit("]")
        g.p = LOOP

    def init() -> None:
        g.set(PX, px0)
        g.set(PY, py0)
        g.clear(MOVES)
        g.clear(WON)
        g.clear(HISTN)
        for y, row in enumerate(LEVEL):
            for x, ch in enumerate(row):
                g.set(MAP0 + y * W + x, tile_of(ch))

    def render() -> None:
        g.putc("\n")
        for y in range(H):
            for x in range(W):
                fx = g.alloc()
                fy = g.alloc()
                g.eq(PX, x, fx)
                g.eq(PY, y, fy)
                g.clear(FLAG)
                g.if_(fx, lambda: g.if_(fy, lambda: g.set(FLAG, 1)))
                g.free(2)

                def draw_player() -> None:
                    g.copy(MAP0 + y * W + x, TILE)
                    fg = g.alloc()
                    g.eq(TILE, 2, fg)
                    g.if_(fg, lambda: g.putc("+"))
                    g.if_not(fg, lambda: g.putc("@"))
                    g.free()

                def draw_tile() -> None:
                    g.copy(MAP0 + y * W + x, TILE)
                    for val, ch in ((0, " "), (1, "#"), (2, "."), (3, "$"), (4, "*")):
                        fv = g.alloc()
                        g.eq(TILE, val, fv)
                        g.if_(fv, lambda ch=ch: g.putc(ch))
                        g.free()

                g.if_(FLAG, draw_player)
                g.if_not(FLAG, draw_tile)
            g.putc("\n")

        g.puts("moves=")
        n, hun, ten, one = g.alloc(), g.alloc(), g.alloc(), g.alloc()
        g.copy(MOVES, n)
        g.clear(hun)
        g.clear(ten)
        g.clear(one)
        g.go(n)
        g.emit("[-")
        g.add(one, 1)
        f10 = g.alloc()
        g.eq(one, 10, f10)

        def on_ten() -> None:
            g.clear(one)
            g.add(ten, 1)
            f2 = g.alloc()
            g.eq(ten, 10, f2)
            g.if_(f2, lambda: (g.clear(ten), g.add(hun, 1)))
            g.free()

        g.if_(f10, on_ten)
        g.free()
        g.go(n)
        g.emit("]")
        g.p = n

        def put_digit(cell: int) -> None:
            d = g.alloc()
            g.copy(cell, d)
            g.add(d, ord("0"))
            g.go(d)
            g.emit(".")
            g.clear(d)
            g.free()

        g.if_(hun, lambda: put_digit(hun))
        any_ht = g.alloc()
        g.clear(any_ht)
        g.if_(hun, lambda: g.set(any_ht, 1))
        g.if_(ten, lambda: g.set(any_ht, 1))
        g.if_(any_ht, lambda: put_digit(ten))
        g.free()
        put_digit(one)
        g.free(4)
        g.if_(WON, lambda: g.puts(" WIN!"))
        g.putc("\n")
        g.puts("> ")

    def read_cmd() -> None:
        g.set(LOOP, 1)
        g.go(LOOP)
        g.emit("[")
        g.clear(LOOP)
        g.clear(CMD)
        g.go(CMD)
        g.emit(",")
        skip = g.alloc()
        g.clear(skip)
        for code in (0, 10, 13, 32):
            f = g.alloc()
            g.eq(CMD, code, f)
            g.if_(f, lambda: g.set(skip, 1))
            g.free()
        g.if_(skip, lambda: g.set(LOOP, 1))
        g.free()
        g.go(LOOP)
        g.emit("]")
        g.p = LOOP

    def dispatch() -> None:
        g.clear(ACT)
        g.clear(DX)
        g.clear(DY)

        def set_move(dx: int, dy: int) -> None:
            g.set(ACT, 1)
            g.set(DX, dx % 256)
            g.set(DY, dy % 256)

        for code, fn in [
            (ord("w"), lambda: set_move(0, -1)),
            (ord("W"), lambda: set_move(0, -1)),
            (ord("s"), lambda: set_move(0, 1)),
            (ord("S"), lambda: set_move(0, 1)),
            (ord("a"), lambda: set_move(-1, 0)),
            (ord("A"), lambda: set_move(-1, 0)),
            (ord("d"), lambda: set_move(1, 0)),
            (ord("D"), lambda: set_move(1, 0)),
            (ord("z"), lambda: g.set(ACT, 2)),
            (ord("Z"), lambda: g.set(ACT, 2)),
            (ord("r"), lambda: g.set(ACT, 3)),
            (ord("R"), lambda: g.set(ACT, 3)),
            (ord("q"), lambda: g.set(ACT, 4)),
            (ord("Q"), lambda: g.set(ACT, 4)),
        ]:
            f = g.alloc()
            g.eq(CMD, code, f)
            g.if_(f, fn)
            g.free()

        f = g.alloc()
        g.eq(ACT, 1, f)
        g.if_(f, try_move)
        g.free()
        f = g.alloc()
        g.eq(ACT, 2, f)
        g.if_(f, undo)
        g.free()
        f = g.alloc()
        g.eq(ACT, 3, f)
        g.if_(f, init)
        g.free()
        f = g.alloc()
        g.eq(ACT, 4, f)
        g.if_(f, lambda: g.clear(RUN))
        g.free()

    g.puts("sokoban_bf - wasd move, z undo, r reset, q quit\n")
    init()
    g.set(RUN, 1)
    g.go(RUN)
    g.emit("[")
    render()
    g.if_(WON, lambda: g.puts("Level clear!\n"))
    read_cmd()
    dispatch()
    g.go(RUN)
    g.emit("]")
    g.p = RUN
    g.puts("bye\n")
    return g.code()


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pure = "".join(ch for ch in build() if ch in "+-<>[],.")
    # Comments must NOT contain any of + - < > [ ] , . or they become code.
    header = (
        "Brainfuck Sokoban mini level generated\n"
        "Map at cell 50: 0 floor 1 wall 2 goal 3 box 4 boxgoal keys wasd z r q\n"
        "Run: python X utf8 main py\n"
    )
    lines = [pure[i : i + 100] for i in range(0, len(pure), 100)]
    OUT.write_text(header + "\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({len(pure)} cmds, ~{len(pure)/1e6:.2f}M)")


if __name__ == "__main__":
    main()
