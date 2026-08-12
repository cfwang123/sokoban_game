#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate unreadableapp1/sokoban.unr (Unreadable Sokoban).

Builds an AST then emits once. Spec: https://esolangs.org/wiki/Unreadable

Policy: gameplay lives in Unreadable; Python only interprets.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

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
N = 49

# Variable layout (keep numbers small so rn(index) stays shallow)
MAP0 = 0
PX, PY, MOVES, WON, HN = 50, 51, 52, 53, 54
DX, DY, NX, NY = 55, 56, 57, 58
BX, BY, IX, TO, FR = 59, 60, 61, 62, 63
TL, TMP, FL, AC, RUN = 64, 65, 66, 67, 68
A, B, C, XX, YY = 70, 71, 72, 73, 74
H0, ESZ = 80, 5
TF, TW, TG, TB, TBG = 0, 1, 2, 3, 4

PRINT, INC, ONE, DO, WHILE, SET, GET, DEC, IF, IN = range(1, 11)


def tile(ch: str) -> int:
    return {" ": 0, "#": 1, ".": 2, "$": 3, "*": 4, "@": 0, "+": 2}[ch]


def player() -> tuple[int, int]:
    for y, r in enumerate(LEVEL):
        for x, c in enumerate(r):
            if c in "@+":
                return x, y
    return 1, 1


@dataclass
class E:
    c: int
    a: List["E"] = field(default_factory=list)
    _em: str | None = field(default=None, repr=False, compare=False)

    def emit(self) -> str:
        if self._em is None:
            self._em = "'" + ('"' * self.c) + "".join(x.emit() for x in self.a)
        return self._em


def e(c: int, *a: E) -> E:
    return E(c, list(a))


def u1() -> E:
    return e(ONE)


def ui(x: E) -> E:
    return e(INC, x)


def ud(x: E) -> E:
    return e(DEC, x)


_rc: dict[int, E] = {}


def rn(n: int) -> E:
    """Integer literal via ONE/INC/DEC (memoized AST nodes)."""
    if n in _rc:
        return _rc[n]
    if n == 0:
        r = ud(u1())
    elif n > 0:
        r = u1()
        for _ in range(n - 1):
            r = ui(r)
    else:
        r = u1()
        for _ in range(-n + 1):
            r = ud(r)
    _rc[n] = r
    return r


def do(*xs: E) -> E:
    """Sequence; balanced DO tree keeps depth O(log n)."""
    if not xs:
        return u1()
    if len(xs) == 1:
        return xs[0]
    mid = len(xs) // 2
    return e(DO, do(*xs[:mid]), do(*xs[mid:]))


def wh(c: E, b: E) -> E:
    return e(WHILE, c, b)


def st(i: E, v: E) -> E:
    return e(SET, i, v)


def gt(i: E) -> E:
    return e(GET, i)


def iff(c: E, t: E, f: E) -> E:
    return e(IF, c, t, f)


def pr(x: E) -> E:
    return e(PRINT, x)


def inn() -> E:
    return e(IN)


def L(i: int) -> E:
    return rn(i)


def G(i: int) -> E:
    return gt(rn(i))


def S(i: int, v: E) -> E:
    return st(rn(i), v)


def pc(ch: str) -> E:
    o = ord(ch)
    if o > 127:
        raise ValueError(f"non-ASCII char {ch!r} (ord={o}); use ASCII only")
    return pr(rn(o))


def ps(s: str) -> E:
    return do(*[pc(c) for c in s]) if s else u1()


def add(dst: int, src: int) -> E:
    return do(S(B, G(src)), wh(G(B), do(S(dst, ui(G(dst))), S(B, ud(G(B))))))


def ge(v: int, n: int) -> E:
    """FL = 1 iff G(v) >= n (destructive on TMP)."""
    xs: list[E] = [S(FL, u1()), S(TMP, G(v))]
    for _ in range(n):
        xs.append(iff(G(TMP), S(TMP, ud(G(TMP))), S(FL, L(0))))
    return do(*xs)


def eqv(v: int, val: int) -> E:
    """FL = 1 iff G(v) == val."""
    xs: list[E] = [S(FL, u1()), S(TMP, G(v))]
    for _ in range(val):
        xs.append(S(TMP, ud(G(TMP))))
    xs.append(wh(G(TMP), do(S(FL, L(0)), S(TMP, L(0)))))
    return do(*xs)


def eq2(a: int, b: int) -> E:
    """FL = 1 iff G(a) == G(b)."""
    return do(
        S(FL, u1()),
        S(TMP, G(a)),
        S(B, G(b)),
        wh(
            iff(G(TMP), iff(G(B), u1(), L(0)), L(0)),
            do(S(TMP, ud(G(TMP))), S(B, ud(G(B)))),
        ),
        iff(G(TMP), S(FL, L(0)), u1()),
        iff(G(B), S(FL, L(0)), u1()),
    )


def midx(x: int, y: int, o: int) -> E:
    """o = G(y)*W + G(x)."""
    return do(
        S(o, L(0)),
        S(TMP, G(y)),
        wh(G(TMP), do(*[S(o, ui(G(o))) for _ in range(W)], S(TMP, ud(G(TMP))))),
        S(TMP, G(x)),
        wh(G(TMP), do(S(o, ui(G(o))), S(TMP, ud(G(TMP))))),
    )


def lmap() -> E:
    return do(S(A, L(MAP0)), add(A, IX), S(TL, gt(G(A))))


def smap(v: E) -> E:
    return do(S(A, L(MAP0)), add(A, IX), st(G(A), v))


def pnum(v: int) -> E:
    V, T, D = 190, 191, 192
    return do(
        S(V, G(v)),
        S(T, L(0)),
        wh(
            do(ge(V, 10), G(FL)),
            do(*[S(V, ud(G(V))) for _ in range(10)], S(T, ui(G(T)))),
        ),
        iff(G(T), do(S(D, L(ord("0"))), add(D, T), pr(G(D))), u1()),
        do(S(D, L(ord("0"))), add(D, V), pr(G(D))),
    )


def cell() -> E:
    return do(
        midx(XX, YY, IX),
        lmap(),
        eq2(PX, XX),
        S(C, G(FL)),
        eq2(PY, YY),
        iff(G(C), iff(G(FL), S(FL, u1()), S(FL, L(0))), S(FL, L(0))),
        iff(
            G(FL),
            do(eqv(TL, TG), iff(G(FL), pc("+"), pc("@"))),
            do(
                eqv(TL, TW),
                iff(
                    G(FL),
                    pc("#"),
                    do(
                        eqv(TL, TG),
                        iff(
                            G(FL),
                            pc("."),
                            do(
                                eqv(TL, TB),
                                iff(
                                    G(FL),
                                    pc("$"),
                                    do(eqv(TL, TBG), iff(G(FL), pc("*"), pc(" "))),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )


def render() -> E:
    return do(
        S(YY, L(0)),
        wh(
            do(ge(YY, H), iff(G(FL), L(0), u1())),
            do(
                S(XX, L(0)),
                wh(
                    do(ge(XX, W), iff(G(FL), L(0), u1())),
                    do(cell(), S(XX, ui(G(XX)))),
                ),
                pc("\n"),
                S(YY, ui(G(YY))),
            ),
        ),
        ps("moves="),
        pnum(MOVES),
        iff(G(WON), ps(" WIN!"), u1()),
        pc("\n"),
        ps("> "),
    )


def cwin() -> E:
    return do(
        S(WON, u1()),
        S(IX, L(0)),
        wh(
            do(ge(IX, N), iff(G(FL), L(0), u1())),
            do(lmap(), eqv(TL, TB), iff(G(FL), S(WON, L(0)), u1()), S(IX, ui(G(IX)))),
        ),
    )


def hptr() -> E:
    return do(
        S(A, L(H0)),
        S(B, G(HN)),
        wh(G(B), do(*[S(A, ui(G(A))) for _ in range(ESZ)], S(B, ud(G(B))))),
    )


def phist(push: bool) -> E:
    xs = [hptr(), st(G(A), G(PX)), S(A, ui(G(A))), st(G(A), G(PY))]
    if push:
        xs += [
            S(A, ui(G(A))),
            st(G(A), G(FR)),
            S(A, ui(G(A))),
            st(G(A), G(TO)),
            S(A, ui(G(A))),
            st(G(A), u1()),
        ]
    else:
        xs += [
            S(A, ui(G(A))),
            st(G(A), L(0)),
            S(A, ui(G(A))),
            st(G(A), L(0)),
            S(A, ui(G(A))),
            st(G(A), L(0)),
        ]
    xs.append(S(HN, ui(G(HN))))
    return do(*xs)


def delta() -> E:
    # DX/DY encoding: 0=-, 1=0, 2=+
    return do(
        S(NX, G(PX)),
        S(NY, G(PY)),
        eqv(DX, 0),
        iff(G(FL), S(NX, ud(G(NX))), u1()),
        eqv(DX, 2),
        iff(G(FL), S(NX, ui(G(NX))), u1()),
        eqv(DY, 0),
        iff(G(FL), S(NY, ud(G(NY))), u1()),
        eqv(DY, 2),
        iff(G(FL), S(NY, ui(G(NY))), u1()),
    )


def inb(x: int, y: int) -> E:
    return do(
        ge(x, 0),
        iff(
            G(FL),
            do(
                ge(y, 0),
                iff(
                    G(FL),
                    do(
                        ge(x, 7),
                        iff(
                            G(FL),
                            S(FL, L(0)),
                            do(ge(y, 7), iff(G(FL), S(FL, L(0)), S(FL, u1()))),
                        ),
                    ),
                    S(FL, L(0)),
                ),
            ),
            S(FL, L(0)),
        ),
    )


def walk() -> E:
    return do(
        phist(False),
        S(PX, G(NX)),
        S(PY, G(NY)),
        S(MOVES, ui(G(MOVES))),
    )


def pbox() -> E:
    return do(
        S(FR, G(IX)),
        S(BX, G(NX)),
        S(BY, G(NY)),
        eqv(DX, 0),
        iff(G(FL), S(BX, ud(G(BX))), u1()),
        eqv(DX, 2),
        iff(G(FL), S(BX, ui(G(BX))), u1()),
        eqv(DY, 0),
        iff(G(FL), S(BY, ud(G(BY))), u1()),
        eqv(DY, 2),
        iff(G(FL), S(BY, ui(G(BY))), u1()),
        inb(BX, BY),
        iff(
            G(FL),
            do(
                midx(BX, BY, TO),
                S(IX, G(TO)),
                lmap(),
                eqv(TL, TF),
                S(C, G(FL)),
                eqv(TL, TG),
                iff(G(C), S(FL, u1()), iff(G(FL), S(FL, u1()), S(FL, L(0)))),
                iff(
                    G(FL),
                    do(
                        eqv(TL, TG),
                        iff(
                            G(FL),
                            do(S(IX, G(TO)), smap(L(TBG))),
                            do(S(IX, G(TO)), smap(L(TB))),
                        ),
                        S(IX, G(FR)),
                        lmap(),
                        eqv(TL, TBG),
                        iff(G(FL), smap(L(TG)), smap(L(TF))),
                        phist(True),
                        S(PX, G(NX)),
                        S(PY, G(NY)),
                        S(MOVES, ui(G(MOVES))),
                        cwin(),
                    ),
                    u1(),
                ),
            ),
            u1(),
        ),
    )


def tmove() -> E:
    return iff(
        G(WON),
        u1(),
        do(
            delta(),
            inb(NX, NY),
            iff(
                G(FL),
                do(
                    midx(NX, NY, IX),
                    lmap(),
                    eqv(TL, TW),
                    iff(
                        G(FL),
                        u1(),
                        do(
                            eqv(TL, TB),
                            S(C, G(FL)),
                            eqv(TL, TBG),
                            iff(
                                G(C),
                                S(FL, u1()),
                                iff(G(FL), S(FL, u1()), S(FL, L(0))),
                            ),
                            iff(G(FL), pbox(), walk()),
                        ),
                    ),
                ),
                u1(),
            ),
        ),
    )


def undo() -> E:
    return iff(
        G(HN),
        do(
            S(HN, ud(G(HN))),
            hptr(),
            S(PX, gt(G(A))),
            S(A, ui(G(A))),
            S(PY, gt(G(A))),
            S(A, ui(G(A))),
            S(FR, gt(G(A))),
            S(A, ui(G(A))),
            S(TO, gt(G(A))),
            S(A, ui(G(A))),
            S(FL, gt(G(A))),
            iff(
                G(FL),
                do(
                    S(IX, G(TO)),
                    lmap(),
                    eqv(TL, TBG),
                    iff(G(FL), smap(L(TG)), smap(L(TF))),
                    S(IX, G(FR)),
                    lmap(),
                    eqv(TL, TG),
                    iff(G(FL), smap(L(TBG)), smap(L(TB))),
                    iff(G(MOVES), S(MOVES, ud(G(MOVES))), u1()),
                    S(WON, L(0)),
                ),
                u1(),
            ),
        ),
        u1(),
    )


def dm(dx: int, dy: int) -> E:
    return do(S(DX, L(dx)), S(DY, L(dy)), tmove())


def map_reset(px0: int, py0: int) -> E:
    xs = []
    for y, row in enumerate(LEVEL):
        for x, ch in enumerate(row):
            xs.append(S(MAP0 + y * W + x, L(tile(ch))))
    xs += [
        S(PX, L(px0)),
        S(PY, L(py0)),
        S(MOVES, L(0)),
        S(WON, L(0)),
        S(HN, L(0)),
    ]
    return do(*xs)


def handle() -> E:
    px0, py0 = player()
    return do(
        S(AC, inn()),
        eqv(AC, ord("\r")),
        iff(G(FL), S(AC, inn()), u1()),
        eqv(AC, ord("\n")),
        iff(G(FL), S(AC, inn()), u1()),
        eqv(AC, ord("q")),
        iff(
            G(FL),
            S(RUN, L(0)),
            do(
                eqv(AC, ord("r")),
                iff(
                    G(FL),
                    map_reset(px0, py0),
                    do(
                        eqv(AC, ord("z")),
                        iff(
                            G(FL),
                            undo(),
                            do(
                                eqv(AC, ord("w")),
                                iff(
                                    G(FL),
                                    dm(1, 0),
                                    do(
                                        eqv(AC, ord("s")),
                                        iff(
                                            G(FL),
                                            dm(1, 2),
                                            do(
                                                eqv(AC, ord("a")),
                                                iff(
                                                    G(FL),
                                                    dm(0, 1),
                                                    do(
                                                        eqv(AC, ord("d")),
                                                        iff(G(FL), dm(2, 1), u1()),
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


def build() -> list[E]:
    px0, py0 = player()
    prog: list[E] = []
    for y, row in enumerate(LEVEL):
        for x, ch in enumerate(row):
            prog.append(S(MAP0 + y * W + x, L(tile(ch))))
    prog += [
        S(PX, L(px0)),
        S(PY, L(py0)),
        S(MOVES, L(0)),
        S(WON, L(0)),
        S(HN, L(0)),
        ps("sokoban_unreadable - wasd z r q\n"),
        ps("(Unreadable + Python interpreter)\n"),
        S(RUN, u1()),
        wh(
            G(RUN),
            do(render(), iff(G(WON), ps("Level clear!\n"), u1()), handle()),
        ),
        ps("bye\n"),
    ]
    return prog


def main() -> None:
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 5000))
    print("building AST...", flush=True)
    prog = build()
    print(f"exprs={len(prog)}, emitting...", flush=True)
    chunks: list[str] = []
    for i, ex in enumerate(prog):
        chunks.append(ex.emit())
        if (i + 1) % 20 == 0:
            print(f"  emitted {i + 1}/{len(prog)}", flush=True)
    src = "".join(chunks)
    bad = set(src) - set("'\"")
    if bad:
        raise SystemExit(f"bad chars {bad}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(src, encoding="utf-8")
    print(f"wrote {OUT} ({len(src)} chars)", flush=True)
    sys.path.insert(0, str(ROOT / "unreadableapp1"))
    from interpreter import parse_program

    print("parse check...", flush=True)
    pe = parse_program(src)
    print(f"parse OK roots={len(pe)}")


if __name__ == "__main__":
    main()
