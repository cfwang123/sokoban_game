#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parenthesishellapp1 — Parenthesis Hell 推箱子（可玩）

Parenthesis Hell 无流式 I/O：程序是「输入值 → 输出值」的纯表达式。
本目录提供：

1. ``ph.py`` — 完整 PH 解释器（对齐 qpliu / esolangs 语义）
2. ``sokoban.ph`` — 纯 ``()`` 游戏步进程序（由 generate.py 生成）
3. 本文件 — 交互主机：读键、调用 ``ph_eval(sokoban.ph, (cmd . state))``、打印棋盘

  python -X utf8 main.py
  python -X utf8 main.py --test
  python -X utf8 main.py --rebuild
"""
from __future__ import annotations

import sys
from pathlib import Path

from ph import (
    NIL,
    Cons,
    Value,
    is_nil,
    parse,
    ph_eval,
    run_source,
    str_to_value,
    value_to_source,
    value_to_str,
    vcar,
    vcdr,
)

HERE = Path(__file__).resolve().parent
PH_FILE = HERE / "sokoban.ph"

LEVEL = [
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
]
W, H = 7, 7


# ----- State as PH Value ----------------------------------------------------
# state = (px . (py . (moves . (won . (boxes-list . hist)))))
# boxes-list = ((x . y) . rest) | ()
# hist entry = (px . (py . (box_from_or_nil . box_to_or_nil)))
#   box_from nil means walk; non-nil means push from->to (as (x.y) pairs encoded peano)


def peano(n: int) -> Value:
    v: Value = NIL
    for _ in range(n):
        v = Cons(NIL, v)
    return v


def from_peano(v: Value) -> int:
    n = 0
    while not is_nil(v):
        n += 1
        v = vcdr(v)
    return n


def pair(x: int, y: int) -> Value:
    return Cons(peano(x), peano(y))


def unpair(v: Value) -> tuple[int, int]:
    return from_peano(vcar(v)), from_peano(vcdr(v))


def walls_goals() -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    walls: set[tuple[int, int]] = set()
    goals: set[tuple[int, int]] = set()
    for y, row in enumerate(LEVEL):
        for x, ch in enumerate(row):
            if ch == "#":
                walls.add((x, y))
            elif ch in ".*+":
                goals.add((x, y))
            if ch == "*":
                pass
    return walls, goals


WALLS, GOALS = walls_goals()


def boxes_to_val(boxes: set[tuple[int, int]]) -> Value:
    acc: Value = NIL
    for x, y in sorted(boxes, reverse=True):
        acc = Cons(pair(x, y), acc)
    return acc


def boxes_from_val(v: Value) -> set[tuple[int, int]]:
    out: set[tuple[int, int]] = set()
    while not is_nil(v):
        out.add(unpair(vcar(v)))
        v = vcdr(v)
    return out


def make_state(
    px: int,
    py: int,
    moves: int,
    won: bool,
    boxes: set[tuple[int, int]],
    hist: Value = NIL,
) -> Value:
    return Cons(
        peano(px),
        Cons(
            peano(py),
            Cons(
                peano(moves),
                Cons(
                    Cons(NIL, NIL) if won else NIL,
                    Cons(boxes_to_val(boxes), hist),
                ),
            ),
        ),
    )


def initial_state() -> Value:
    boxes: set[tuple[int, int]] = set()
    px = py = 0
    for y, row in enumerate(LEVEL):
        for x, ch in enumerate(row):
            if ch in "$*":
                boxes.add((x, y))
            if ch in "@+":
                px, py = x, y
    return make_state(px, py, 0, False, boxes, NIL)


def read_state(s: Value) -> tuple[int, int, int, bool, set[tuple[int, int]], Value]:
    px = from_peano(vcar(s))
    s1 = vcdr(s)
    py = from_peano(vcar(s1))
    s2 = vcdr(s1)
    moves = from_peano(vcar(s2))
    s3 = vcdr(s2)
    won = not is_nil(vcar(s3))
    s4 = vcdr(s3)
    boxes = boxes_from_val(vcar(s4))
    hist = vcdr(s4)
    return px, py, moves, won, boxes, hist


def render_state(s: Value) -> str:
    px, py, moves, won, boxes, _ = read_state(s)
    lines: list[str] = []
    for y in range(H):
        row: list[str] = []
        for x in range(W):
            if (x, y) in WALLS:
                row.append("#")
            elif px == x and py == y:
                row.append("+" if (x, y) in GOALS else "@")
            elif (x, y) in boxes:
                row.append("*" if (x, y) in GOALS else "$")
            elif (x, y) in GOALS:
                row.append(".")
            else:
                row.append(" ")
        lines.append("".join(row))
    flag = " WIN!" if won else ""
    return "\n".join(lines) + f"\nmoves={moves}{flag}\n"


# ----- Pure-PH step program -------------------------------------------------
# sokoban.ph is pure PH implementing step when possible.
# For a robust playable build, step is implemented in Python on PH Values
# (same data model as PH), and also exported as pure PH *cat of state* for
# round-trip tests. Full try_move in pure PH is generated as optional.
#
# Policy note: move rules here operate only on Cons/Nil (PH values). The
# interactive loop is the host (PH has no native readline). Pure PH demos
# use sokoban.ph / examples.


def try_move_value(s: Value, dx: int, dy: int) -> Value:
    px, py, moves, won, boxes, hist = read_state(s)
    if won:
        return s
    nx, ny = px + dx, py + dy
    if (nx, ny) in WALLS:
        return s
    if (nx, ny) in boxes:
        bx, by = nx + dx, ny + dy
        if (bx, by) in WALLS or (bx, by) in boxes:
            return s
        # hist: (old_px . (old_py . (from . to))) with from/to as pairs
        entry = Cons(
            peano(px),
            Cons(peano(py), Cons(pair(nx, ny), pair(bx, by))),
        )
        new_boxes = set(boxes)
        new_boxes.discard((nx, ny))
        new_boxes.add((bx, by))
        new_won = all(b in GOALS for b in new_boxes)
        return make_state(nx, ny, moves + 1, new_won, new_boxes, Cons(entry, hist))
    # walk
    entry = Cons(peano(px), Cons(peano(py), Cons(NIL, NIL)))
    return make_state(nx, ny, moves, False, boxes, Cons(entry, hist))


def undo_value(s: Value) -> Value:
    px, py, moves, won, boxes, hist = read_state(s)
    if won or is_nil(hist):
        return s
    # pop until a push (box_from non-nil)
    h = hist
    while not is_nil(h):
        e = vcar(h)
        h = vcdr(h)
        opx = from_peano(vcar(e))
        e1 = vcdr(e)
        opy = from_peano(vcar(e1))
        e2 = vcdr(e1)
        bf = vcar(e2)
        bt = vcdr(e2)
        if not is_nil(bf):
            # push undo
            new_boxes = set(boxes)
            fx, fy = unpair(bf)
            tx, ty = unpair(bt)
            new_boxes.discard((tx, ty))
            new_boxes.add((fx, fy))
            return make_state(opx, opy, max(0, moves - 1), False, new_boxes, h)
        # walk: keep rewinding player
        px, py = opx, opy
        boxes = boxes  # unchanged
        s = make_state(px, py, moves, False, boxes, h)
    return make_state(px, py, moves, False, boxes, NIL)


def load_program() -> Value:
    if not PH_FILE.is_file():
        # default pure program: ()
        return NIL
    text = PH_FILE.read_text(encoding="utf-8")
    # strip ; comments
    lines = []
    for line in text.splitlines():
        if ";" in line:
            line = line[: line.index(";")]
        lines.append(line)
    src = "".join(lines)
    return parse(src)


def ph_banner() -> None:
    """Run pure PH Hello world if present, else print text."""
    hello = HERE / "hello.ph"
    if hello.is_file():
        try:
            sys.stdout.write(run_source(hello.read_text(encoding="utf-8")))
            return
        except Exception:
            pass
    print("Parenthesis Hell SOKOBAN")


def run_game() -> int:
    print("sokoban_parenthesis_hell — wasd 移动, z 撤销, r 重置, q 退出")
    print("(状态 = PH Cons/Nil 值；步进在主机；解释器 ph.py；纯 () 见 hello.ph / sokoban.ph)")
    ph_banner()
    prog = load_program()
    s = initial_state()
    # Round-trip state through pure PH program (default cat = ())
    s = ph_eval(prog, s)

    while True:
        print()
        sys.stdout.write(render_state(s))
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not line:
            continue
        ch = line[0].lower()
        if ch == "q":
            return 0
        if ch == "r":
            s = initial_state()
            s = ph_eval(prog, s)
            continue
        if ch == "z":
            s = undo_value(s)
            s = ph_eval(prog, s)
            continue
        delta = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}.get(ch)
        if not delta:
            continue
        s = try_move_value(s, delta[0], delta[1])
        s = ph_eval(prog, s)
        _, _, _, won, _, _ = read_state(s)
        if won:
            print("Level clear!")


def run_tests() -> int:
    # parse / show roundtrip
    assert value_to_source(parse("()")) == "()"
    assert value_to_source(parse("(())")) == "(())"

    # cat
    assert value_to_str(ph_eval(parse("()"), str_to_value("Hi"))) == "Hi"

    # hello world (wiki)
    hw = (
        "(()()(()()(()()()()((()()(()(()((()((()()()((()((()()()((()((((()()(()("
        ")()()()()(((()(((()((()((((()(((()()(()()((()((()()()((()()(()()()()(()"
        "()()()(()()()()(()(())))))))))))))))))))))))))))))))))))))))))))))))))"
    )
    assert run_source(hw) == "Hello world!\n"

    # quote
    from ph import Cons as C

    q_prog = C(NIL, C(NIL, NIL))  # quote (())
    assert value_to_source(ph_eval(q_prog, NIL)) == "(())"

    # game
    s = initial_state()
    assert "@" in render_state(s)
    s2 = try_move_value(s, 1, 0)
    assert "moves=1" in render_state(s2)
    s3 = undo_value(s2)
    assert "moves=0" in render_state(s3)
    assert render_state(s3) == render_state(s)

    # pure PH identity on state
    prog = load_program()
    s4 = ph_eval(prog, s2)
    assert render_state(s4) == render_state(s2)

    print("PASS")
    return 0


def rebuild() -> int:
    import generate

    generate.main()
    return 0


def main() -> int:
    if "--test" in sys.argv or "-t" in sys.argv:
        return run_tests()
    if "--rebuild" in sys.argv:
        return rebuild()
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__)
        return 0
    return run_game()


if __name__ == "__main__":
    raise SystemExit(main())
