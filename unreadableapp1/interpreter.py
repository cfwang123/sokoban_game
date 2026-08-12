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


sys.setrecursionlimit(50000)

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


def _tokenize(pgm: str) -> list[int]:
    """Turn quote stream into command arity-ids (1..10)."""
    tokens: list[int] = []
    i = 0
    n = len(pgm)
    while i < n:
        if pgm[i] != "'":
            raise ParseError(f"expected ', got {pgm[i : i + 20]!r}")
        i += 1
        command = 0
        while i < n and pgm[i] != "'":
            if pgm[i] == '"':
                command += 1
            # other chars already stripped
            i += 1
        if not 1 <= command <= 10:
            raise ParseError(f"invalid command arity-id {command}")
        tokens.append(command)
    return tokens


def parse_program(text: str) -> List[Expr]:
    """Parse full program into root expressions (iterative, stack-safe)."""
    pgm = re.sub(r"[^\"']", "", text)
    tokens = _tokenize(pgm)
    roots: List[Expr] = []
    # stack frames: (command, args_collected, args_still_needed)
    stack: list[tuple[int, list[Expr], int]] = []
    pos = 0
    nt = len(tokens)

    def push_token(cmd: int) -> None:
        need = ARGNS[cmd]
        if need == 0:
            finish(Expr(cmd, []))
        else:
            stack.append((cmd, [], need))

    def finish(node: Expr) -> None:
        if not stack:
            roots.append(node)
            return
        cmd, args, need = stack[-1]
        args.append(node)
        need -= 1
        if need == 0:
            stack.pop()
            finish(Expr(cmd, args))
        else:
            stack[-1] = (cmd, args, need)

    while pos < nt or stack:
        if stack and stack[-1][2] == 0:
            # should not happen with finish logic
            cmd, args, _ = stack.pop()
            finish(Expr(cmd, args))
            continue
        if pos >= nt:
            if stack:
                raise ParseError("unexpected end of program (missing arguments)")
            break
        cmd = tokens[pos]
        pos += 1
        if not stack:
            push_token(cmd)
        else:
            # this token starts the next required child
            need_parent = stack[-1][2]
            if need_parent <= 0:
                raise ParseError("internal parse error")
            push_token(cmd)

    return roots


def parse_one(pgm: str) -> tuple[Expr, str]:
    """Compatibility helper: parse a single expression from a quote string."""
    exprs = parse_program(pgm)
    if not exprs:
        raise ParseError("empty program or too few arguments")
    # re-strip to find remainder is not tracked; full parse only
    return exprs[0], ""


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
