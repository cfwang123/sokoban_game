#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
brainfuckapp1 — run sokoban.bf with a small Brainfuck interpreter.

Usage:
  python -X utf8 main.py
"""
from __future__ import annotations

import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
BF_FILE = DIR / "sokoban.bf"


def load_program(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return "".join(c for c in text if c in "+-<>[],.")


def build_jump_table(prog: str) -> dict[int, int]:
    stack: list[int] = []
    jmp: dict[int, int] = {}
    for i, c in enumerate(prog):
        if c == "[":
            stack.append(i)
        elif c == "]":
            if not stack:
                raise RuntimeError(f"unmatched ] at {i}")
            j = stack.pop()
            jmp[j] = i
            jmp[i] = j
    if stack:
        raise RuntimeError(f"unmatched [ at {stack[-1]}")
    return jmp


def run(prog: str) -> None:
    jmp = build_jump_table(prog)
    tape = bytearray(30000)
    p = 0
    ip = 0
    n = len(prog)
    # line buffer for interactive input (like other *app1 CLIs)
    buf = ""
    bi = 0

    def read_byte() -> int:
        nonlocal buf, bi
        while bi >= len(buf):
            try:
                line = sys.stdin.readline()
            except KeyboardInterrupt:
                return 0
            if line == "":
                return 0  # EOF
            buf = line
            bi = 0
        ch = buf[bi]
        bi += 1
        return ord(ch) & 255

    out = sys.stdout
    while ip < n:
        c = prog[ip]
        if c == ">":
            p += 1
            if p >= len(tape):
                tape.extend(bytearray(len(tape)))
        elif c == "<":
            p -= 1
            if p < 0:
                raise RuntimeError("tape pointer moved left of 0")
        elif c == "+":
            tape[p] = (tape[p] + 1) & 255
        elif c == "-":
            tape[p] = (tape[p] - 1) & 255
        elif c == ".":
            out.write(chr(tape[p]))
            out.flush()
        elif c == ",":
            tape[p] = read_byte()
        elif c == "[":
            if tape[p] == 0:
                ip = jmp[ip]
        elif c == "]":
            if tape[p] != 0:
                ip = jmp[ip]
        ip += 1


def main() -> None:
    if not BF_FILE.is_file():
        print(f"missing {BF_FILE.name}", file=sys.stderr)
        sys.exit(1)
    prog = load_program(BF_FILE)
    if not prog:
        print("empty Brainfuck program", file=sys.stderr)
        sys.exit(1)
    try:
        run(prog)
    except RuntimeError as e:
        print(f"\nbf error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
