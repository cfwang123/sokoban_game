#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unreadable interpreter (Python 3).

Language: https://esolangs.org/wiki/Unreadable
Based on Marinus's approved interpreter (logic; modernized for Py3).

Commands (after leading ``'``, count of ``"``):
  1 PRINT x      — write Unicode char x, return x
  2 INC x        — return x+1
  3 ONE          — return 1
  4 DO x y       — eval x then y; return y
  5 WHILE x y    — while x: y; return last y (or 0)
  6 SET x y      — vars[x] = y; return y
  7 GET x        — return vars[x] (0 if unset)
  8 DEC x        — return x-1
  9 IF x y z     — if x then y else z
 10 IN           — read one char as code point, or -1 on EOF
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from typing import Callable, List, Optional, TextIO


sys.setrecursionlimit(20000)

PRINT, INC, ONE, DO, WHILE, SET, GET, DEC, IF, IN = range(1, 11)
ARGNS = {
    PRINT: 1,
    INC: 1,
    ONE: 0,
    DO: 2,
    WHILE: 2,
    SET: 2,
    GET: 1,
    DEC: 1,
    IF: 3,
    IN: 0,
}


@dataclass
class Expr:
    command: int
    args: List["Expr"]

    def __str__(self) -> str:
        names = [
            "",
            "print",
            "inc",
            "1",
            "do",
            "while",
            "set",
            "get",
            "dec",
            "if",
            "in",
        ]
        if not self.args:
            return names[self.command]
        return f"({names[self.command]} " + " ".join(map(str, self.args)) + ")"


class ParseError(Exception):
    pass


def parse_one(pgm: str) -> tuple[Expr, str]:
    if not pgm:
        raise ParseError("empty program or too few arguments")
    if pgm[0] != "'":
        raise ParseError(f"expected ', got {pgm[:20]!r}")
    command = 0
    index = 1
    while index < len(pgm) and pgm[index] != "'":
        if pgm[index] == '"':
            command += 1
        index += 1
    if not 1 <= command <= 10:
        raise ParseError(f"invalid command arity-id {command}")
    rest = pgm[index:]
    args: List[Expr] = []
    for _ in range(ARGNS[command]):
        arg, rest = parse_one(rest)
        args.append(arg)
    return Expr(command, args), rest


def parse_program(text: str) -> List[Expr]:
    pgm = re.sub(r"[^\"']", "", text)
    rest = pgm
    exprs: List[Expr] = []
    while rest:
        exp, rest = parse_one(rest)
        exprs.append(exp)
    return exprs


class AutoArray:
    def __init__(self) -> None:
        self._a: list[int] = []

    def __getitem__(self, x: int) -> int:
        if x < 0:
            return 0
        if x < len(self._a):
            return self._a[x]
        return 0

    def __setitem__(self, x: int, val: int) -> None:
        if x < 0:
            return
        if x >= len(self._a):
            self._a.extend([0] * (x - len(self._a) + 1))
        self._a[x] = int(val)


class Interpreter:
    def __init__(
        self,
        exprs: List[Expr],
        *,
        stdin: Optional[TextIO] = None,
        stdout: Optional[TextIO] = None,
    ) -> None:
        self.pgm = exprs
        self.vars = AutoArray()
        self.stdin = stdin if stdin is not None else sys.stdin
        self.stdout = stdout if stdout is not None else sys.stdout
        self._line_buf = ""
        self._line_i = 0
        self.cmds: dict[int, Callable[..., int]] = {
            PRINT: self._print,
            INC: self._inc,
            ONE: self._one,
            DO: self._do,
            WHILE: self._while,
            SET: self._set,
            GET: self._get,
            DEC: self._dec,
            IF: self._if,
            IN: self._in,
        }

    def eval(self, expr: Expr) -> int:
        return self.cmds[expr.command](*expr.args)

    def run(self) -> None:
        for e in self.pgm:
            self.eval(e)

    def _print(self, x: Expr) -> int:
        v = self.eval(x)
        try:
            ch = chr(v) if v >= 0 else ""
        except (ValueError, OverflowError):
            ch = chr(v % 256) if v >= 0 else ""
        self.stdout.write(ch)
        self.stdout.flush()
        return v

    def _inc(self, x: Expr) -> int:
        return self.eval(x) + 1

    def _one(self) -> int:
        return 1

    def _do(self, x: Expr, y: Expr) -> int:
        self.eval(x)
        return self.eval(y)

    def _while(self, x: Expr, y: Expr) -> int:
        result = 0
        while self.eval(x):
            result = self.eval(y)
        return result

    def _set(self, x: Expr, y: Expr) -> int:
        r = self.eval(y)
        self.vars[self.eval(x)] = r
        return r

    def _get(self, x: Expr) -> int:
        return self.vars[self.eval(x)]

    def _dec(self, x: Expr) -> int:
        return self.eval(x) - 1

    def _if(self, x: Expr, y: Expr, z: Expr) -> int:
        if self.eval(x):
            return self.eval(y)
        return self.eval(z)

    def _in(self) -> int:
        # Prefer char-at-a-time; if stdin is line-buffered interactive, still OK
        ch = self.stdin.read(1)
        if ch == "":
            return -1
        return ord(ch)


def run_file(path: str, *, show: bool = False) -> None:
    text = open(path, encoding="utf-8").read()
    exprs = parse_program(text)
    if show:
        for e in exprs:
            print(e)
        return
    Interpreter(exprs).run()


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("Usage: interpreter.py [-show] program.unr", file=sys.stderr)
        return 2
    show = False
    if argv[0] == "-show":
        show = True
        argv = argv[1:]
    if not argv:
        return 2
    try:
        run_file(argv[0], show=show)
    except ParseError as e:
        print("parse error:", e, file=sys.stderr)
        return 1
    except Exception as e:
        print("runtime error:", e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
