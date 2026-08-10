#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate unreadableapp1/sokoban.unr — playable Sokoban in Unreadable.

Spec: https://esolangs.org/wiki/Unreadable
Alphabet: only ' and \"
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "unreadableapp1" / "sokoban.unr"

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

MAP0 = 0
PX, PY = 50, 51
MOVES, WON, HISTN = 52, 53, 54
DX, DY, NX, NY = 55, 56, 57, 58
BX, BY, IDX, TOI = 59, 60, 61, 62
TILE, TMP, FLAG, ACT = 63, 64, 65, 66
FRI = 67
A, B, C, D = 210, 211, 212, 213
HIST0 = 100
ESZ = 5
RUN = 199

T_FLOOR, T_WALL, T_GOAL, T_BOX, T_BG = 0, 1, 2, 3, 4

PRINT, INC, ONE, DO, WHILE, SET, GET, DEC, IF, IN = range(1, 11)


def tile_of(ch: str) -> int:
    return {" ": 0, "#": 1, ".": 2, "$": 3, "*": 4, "@": 0, "+": 2}[ch]


def find_player() -> tuple[int, int]:
    for y, row in enumerate(LEVEL):
        for x, ch in enumerate(row):
            if ch in "@+":
                return x, y
    return 1, 1


def em(cmd: int, *args: str) -> str:
    return "'" + ('"' * cmd) + "".join(args)


def one() -> str:
    return em(ONE)


def inc(x: str) -> str:
    return em(INC, x)


def dec(x: str) -> str:
    return em(DEC, x)


def num(n: int) -> str:
    if n == 0:
        return dec(one())
    if n < 0:
        e = one()
        for _ in range(-n + 1):
            e = dec(e)
        return e
    e = one()
    for _ in range(n - 1):
        e = inc(e)
    return e


def do(*xs: str) -> str:
    if not xs:
        return one()
    r = xs[-1]
    for x in reversed(xs[:-1]):
        r = em(DO, x, r)
    return r


def while_(c: str, body: str) -> str:
    return em(WHILE, c, body)


def setv(i: str, v: str) -> str:
    return em(SET, i, v)


def getv(i: str) -> str:
    return em(GET, i)


def if_(c: str, t: str, e: str) -> str:
    return em(IF, c, t, e)


def pr(x: str) -> str:
    return em(PRINT, x)


def inp() -> str:
    return em(IN)


def lit(i: int) -> str:
    return num(i)


def g(i: int) -> str:
    return getv(lit(i))


def s(i: int, v: str) -> str:
    return setv(lit(i), v)


def pr_ch(ch: str) -> str:
    return pr(lit(ord(ch)))


def pr_str(text: str) -> str:
    return do(*[pr_ch(c) for c in text]) if text else one()


def add_into(dst: int, src: int, tmp: int = B) -> str:
    """dst += src (preserves src via tmp)."""
    return do(
        s(tmp, g(src)),
        while_(g(tmp), do(s(dst, inc(g(dst))), s(tmp, dec(g(tmp))))),
    )


def ge_const(var: int, n: int, flag: int = FLAG) -> str:
    """flag = 1 if vars[var] >= n."""
    steps: list[str] = [s(flag, one()), s(TMP, g(var))]
    for _ in range(n):
        steps.append(if_(g(TMP), s(TMP, dec(g(TMP))), s(flag, num(0))))
    return do(*steps)


def eq_val(expr: str, val: int, flag: int = FLAG) -> str:
    """flag = 1 iff expr == val (via subtract)."""
    steps: list[str] = [s(flag, one()), s(TMP, expr)]
    for _ in range(val):
        steps.append(s(TMP, dec(g(TMP))))
    steps.append(while_(g(TMP), do(s(flag, num(0)), s(TMP, num(0)))))
    return do(*steps)


def map_index(x_var: int, y_var: int, out: int) -> str:
    """out = y*W + x."""
    return do(
        s(out, num(0)),
        s(TMP, g(y_var)),
        while_(
            g(TMP),
            do(*[s(out, inc(g(out))) for _ in range(W)], s(TMP, dec(g(TMP)))),
        ),
        s(TMP, g(x_var)),
        while_(g(TMP), do(s(out, inc(g(out))), s(TMP, dec(g(TMP))))),
    )


def cell_addr() -> str:
    """A = MAP0 + IDX."""
    return do(s(A, lit(MAP0)), add_into(A, IDX))


def load_tile() -> str:
    return do(cell_addr(), s(TILE, getv(g(A))))


def store_tile(val: str) -> str:
    return do(cell_addr(), setv(g(A), val))


def print_number(var: int) -> str:
    V, T, DIG = 200, 201, 202
    return do(
        s(V, g(var)),
        s(T, num(0)),
        while_(
            do(ge_const(V, 10, FLAG), g(FLAG)),
            do(*[s(V, dec(g(V))) for _ in range(10)], s(T, inc(g(T)))),
        ),
        if_(
            g(T),
            do(s(DIG, lit(ord("0"))), add_into(DIG, T), pr(g(DIG))),
            one(),
        ),
        do(s(DIG, lit(ord("0"))), add_into(DIG, V), pr(g(DIG))),
    )


def render() -> str:
    chunks: list[str] = []
    for y in range(H):
        for x in range(W):
            i = y * W + x
            is_pl = do(
                eq_val(g(PX), x, FLAG),
                s(C, g(FLAG)),
                eq_val(g(PY), y, FLAG),
                if_(
                    g(C),
                    if_(g(FLAG), s(FLAG, one()), s(FLAG, num(0))),
                    s(FLAG, num(0)),
                ),
            )
            cell = g(MAP0 + i)
            print_pl = do(
                eq_val(cell, T_GOAL, TMP),
                if_(g(TMP), pr_ch("+"), pr_ch("@")),
            )
            print_tile = do(
                eq_val(cell, T_WALL, FLAG),
                if_(
                    g(FLAG),
                    pr_ch("#"),
                    do(
                        eq_val(cell, T_GOAL, FLAG),
                        if_(
                            g(FLAG),
                            pr_ch("."),
                            do(
                                eq_val(cell, T_BOX, FLAG),
                                if_(
                                    g(FLAG),
                                    pr_ch("$"),
                                    do(
                                        eq_val(cell, T_BG, FLAG),
                                        if_(g(FLAG), pr_ch("*"), pr_ch(" ")),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            )
            chunks.append(do(is_pl, if_(g(FLAG), print_pl, print_tile)))
        chunks.append(pr_ch("\n"))
    chunks.append(
        do(
            pr_str("moves="),
            print_number(MOVES),
            if_(g(WON), pr_str(" WIN!"), one()),
            pr_ch("\n"),
            pr_str("> "),
        )
    )
    return do(*chunks)


def check_win() -> str:
    parts = [s(WON, one())]
    for i in range(W * H):
        parts.append(
            do(
                eq_val(g(MAP0 + i), T_BOX, FLAG),
                if_(g(FLAG), s(WON, num(0)), one()),
            )
        )
    return do(*parts)


def hist_ptr() -> str:
    return do(
        s(A, lit(HIST0)),
        s(B, g(HISTN)),
        while_(
            g(B),
            do(*[s(A, inc(g(A))) for _ in range(ESZ)], s(B, dec(g(B)))),
        ),
    )


def push_hist(is_push: bool) -> str:
    steps = [hist_ptr(), setv(g(A), g(PX))]
    steps += [s(A, inc(g(A))), setv(g(A), g(PY))]
    if is_push:
        steps += [
            s(A, inc(g(A))),
            setv(g(A), g(FRI)),
            s(A, inc(g(A))),
            setv(g(A), g(TOI)),
            s(A, inc(g(A))),
            setv(g(A), one()),
        ]
    else:
        steps += [
            s(A, inc(g(A))),
            setv(g(A), num(0)),
            s(A, inc(g(A))),
            setv(g(A), num(0)),
            s(A, inc(g(A))),
            setv(g(A), num(0)),
        ]
    steps.append(s(HISTN, inc(g(HISTN))))
    return do(*steps)


def apply_delta() -> str:
    return do(
        s(NX, g(PX)),
        s(NY, g(PY)),
        eq_val(g(DX), 0, FLAG),
        if_(g(FLAG), s(NX, dec(g(NX))), one()),
        eq_val(g(DX), 2, FLAG),
        if_(g(FLAG), s(NX, inc(g(NX))), one()),
        eq_val(g(DY), 0, FLAG),
        if_(g(FLAG), s(NY, dec(g(NY))), one()),
        eq_val(g(DY), 2, FLAG),
        if_(g(FLAG), s(NY, inc(g(NY))), one()),
    )


def in_bounds(xv: int, yv: int) -> str:
    return do(
        ge_const(xv, 0, FLAG),
        if_(
            g(FLAG),
            do(
                ge_const(yv, 0, FLAG),
                if_(
                    g(FLAG),
                    do(
                        ge_const(xv, 7, FLAG),
                        if_(
                            g(FLAG),
                            s(FLAG, num(0)),
                            do(
                                ge_const(yv, 7, FLAG),
                                if_(g(FLAG), s(FLAG, num(0)), s(FLAG, one())),
                            ),
                        ),
                    ),
                    s(FLAG, num(0)),
                ),
            ),
            s(FLAG, num(0)),
        ),
    )


def load_map() -> str:
    return do(s(A, lit(MAP0)), add_into(A, IDX), s(TILE, getv(g(A))))


def store_map(val: str) -> str:
    return do(s(A, lit(MAP0)), add_into(A, IDX), setv(g(A), val))


def walk() -> str:
    return do(push_hist(False), s(PX, g(NX)), s(PY, g(NY)))


def push_box() -> str:
    return do(
        s(FRI, g(IDX)),
        s(BX, g(NX)),
        s(BY, g(NY)),
        eq_val(g(DX), 0, FLAG),
        if_(g(FLAG), s(BX, dec(g(BX))), one()),
        eq_val(g(DX), 2, FLAG),
        if_(g(FLAG), s(BX, inc(g(BX))), one()),
        eq_val(g(DY), 0, FLAG),
        if_(g(FLAG), s(BY, dec(g(BY))), one()),
        eq_val(g(DY), 2, FLAG),
        if_(g(FLAG), s(BY, inc(g(BY))), one()),
        in_bounds(BX, BY),
        if_(
            g(FLAG),
            do(
                map_index(BX, BY, TOI),
                s(IDX, g(TOI)),
                load_map(),
                eq_val(g(TILE), T_FLOOR, FLAG),
                s(C, g(FLAG)),
                eq_val(g(TILE), T_GOAL, FLAG),
                if_(
                    g(C),
                    s(FLAG, one()),
                    if_(g(FLAG), s(FLAG, one()), s(FLAG, num(0))),
                ),
                if_(
                    g(FLAG),
                    do(
                        eq_val(g(TILE), T_GOAL, FLAG),
                        if_(
                            g(FLAG),
                            do(s(IDX, g(TOI)), store_map(lit(T_BG))),
                            do(s(IDX, g(TOI)), store_map(lit(T_BOX))),
                        ),
                        s(IDX, g(FRI)),
                        load_map(),
                        eq_val(g(TILE), T_BG, FLAG),
                        if_(
                            g(FLAG),
                            store_map(lit(T_GOAL)),
                            store_map(lit(T_FLOOR)),
                        ),
                        push_hist(True),
                        s(PX, g(NX)),
                        s(PY, g(NY)),
                        s(MOVES, inc(g(MOVES))),
                        check_win(),
                    ),
                    one(),
                ),
            ),
            one(),
        ),
    )


def try_move() -> str:
    return if_(
        g(WON),
        one(),
        do(
            apply_delta(),
            in_bounds(NX, NY),
            if_(
                g(FLAG),
                do(
                    map_index(NX, NY, IDX),
                    load_map(),
                    eq_val(g(TILE), T_WALL, FLAG),
                    if_(
                        g(FLAG),
                        one(),
                        do(
                            eq_val(g(TILE), T_BOX, FLAG),
                            s(C, g(FLAG)),
                            eq_val(g(TILE), T_BG, FLAG),
                            if_(
                                g(C),
                                s(FLAG, one()),
                                if_(g(FLAG), s(FLAG, one()), s(FLAG, num(0))),
                            ),
                            if_(g(FLAG), push_box(), walk()),
                        ),
                    ),
                ),
                one(),
            ),
        ),
    )


def undo() -> str:
    return if_(
        g(HISTN),
        do(
            s(HISTN, dec(g(HISTN))),
            hist_ptr(),
            s(PX, getv(g(A))),
            s(A, inc(g(A))),
            s(PY, getv(g(A))),
            s(A, inc(g(A))),
            s(FRI, getv(g(A))),
            s(A, inc(g(A))),
            s(TOI, getv(g(A))),
            s(A, inc(g(A))),
            s(FLAG, getv(g(A))),
            if_(
                g(FLAG),
                do(
                    s(IDX, g(TOI)),
                    load_map(),
                    eq_val(g(TILE), T_BG, FLAG),
                    if_(
                        g(FLAG),
                        store_map(lit(T_GOAL)),
                        store_map(lit(T_FLOOR)),
                    ),
                    s(IDX, g(FRI)),
                    load_map(),
                    eq_val(g(TILE), T_GOAL, FLAG),
                    if_(
                        g(FLAG),
                        store_map(lit(T_BG)),
                        store_map(lit(T_BOX)),
                    ),
                    if_(g(MOVES), s(MOVES, dec(g(MOVES))), one()),
                    s(WON, num(0)),
                ),
                one(),
            ),
        ),
        one(),
    )


def reset(px0: int, py0: int) -> str:
    seq = []
    for y, row in enumerate(LEVEL):
        for x, ch in enumerate(row):
            seq.append(s(MAP0 + y * W + x, lit(tile_of(ch))))
    seq += [
        s(PX, lit(px0)),
        s(PY, lit(py0)),
        s(MOVES, num(0)),
        s(WON, num(0)),
        s(HISTN, num(0)),
    ]
    return do(*seq)


def dir_move(dxc: int, dyc: int) -> str:
    return do(s(DX, lit(dxc)), s(DY, lit(dyc)), try_move())


def handle() -> str:
    return do(
        s(ACT, inp()),
        eq_val(g(ACT), ord("\r"), FLAG),
        if_(g(FLAG), s(ACT, inp()), one()),
        eq_val(g(ACT), ord("\n"), FLAG),
        if_(g(FLAG), s(ACT, inp()), one()),
        eq_val(g(ACT), ord("q"), FLAG),
        if_(
            g(FLAG),
            s(RUN, num(0)),
            do(
                eq_val(g(ACT), ord("r"), FLAG),
                if_(
                    g(FLAG),
                    reset(*find_player()),
                    do(
                        eq_val(g(ACT), ord("z"), FLAG),
                        if_(
                            g(FLAG),
                            undo(),
                            do(
                                eq_val(g(ACT), ord("w"), FLAG),
                                if_(
                                    g(FLAG),
                                    dir_move(1, 0),
                                    do(
                                        eq_val(g(ACT), ord("s"), FLAG),
                                        if_(
                                            g(FLAG),
                                            dir_move(1, 2),
                                            do(
                                                eq_val(g(ACT), ord("a"), FLAG),
                                                if_(
                                                    g(FLAG),
                                                    dir_move(0, 1),
                                                    do(
                                                        eq_val(g(ACT), ord("d"), FLAG),
                                                        if_(
                                                            g(FLAG),
                                                            dir_move(2, 1),
                                                            one(),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )


def gen() -> str:
    px0, py0 = find_player()
    return do(
        reset(px0, py0),
        pr_str("sokoban_unreadable — wasd z r q\n"),
        pr_str("(Unreadable + Python interpreter)\n"),
        s(RUN, one()),
        while_(
            g(RUN),
            do(
                render(),
                if_(g(WON), pr_str("Level clear!\n"), one()),
                handle(),
            ),
        ),
        pr_str("bye\n"),
    )


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    src = gen()
    bad = set(src) - set("'\"")
    if bad:
        raise SystemExit(f"non-alphabet: {bad!r}")
    OUT.write_text(src, encoding="utf-8")
    print(f"wrote {OUT} ({len(src)} chars)")
    sys.path.insert(0, str(ROOT / "unreadableapp1"))
    from interpreter import parse_program

    exprs = parse_program(src)
    print(f"parsed OK, {len(exprs)} root expr(s)")


if __name__ == "__main__":
    main()
