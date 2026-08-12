#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""unreadableapp1 — pure Unreadable Sokoban (Python host = interpreter only).

  python -X utf8 main.py
  python -X utf8 main.py --test
  python -X utf8 main.py --rebuild   # regenerate sokoban.unr
"""
from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

from interpreter import Interpreter, ParseError, parse_program

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
UNR = HERE / "sokoban.unr"
GEN = ROOT / "scripts" / "_gen_unreadable_sokoban.py"


def run_game() -> int:
    if not UNR.is_file():
        print("missing sokoban.unr — run: python -X utf8 main.py --rebuild", file=sys.stderr)
        return 1
    try:
        exprs = parse_program(UNR.read_text(encoding="utf-8"))
        Interpreter(exprs).run()
    except KeyboardInterrupt:
        print()
    except ParseError as e:
        print("parse error:", e, file=sys.stderr)
        return 1
    except Exception as e:
        print("runtime error:", e, file=sys.stderr)
        return 1
    return 0


def rebuild() -> int:
    if not GEN.is_file():
        print(f"missing generator {GEN}", file=sys.stderr)
        return 1
    r = subprocess.run(
        [sys.executable, "-X", "utf8", str(GEN)],
        cwd=str(ROOT),
    )
    return r.returncode


def _run_with_input(keys: str, timeout: float = 120.0) -> str:
    exprs = parse_program(UNR.read_text(encoding="utf-8"))
    inp = io.StringIO(keys)
    out = io.StringIO()
    Interpreter(exprs, stdin=inp, stdout=out).run()
    return out.getvalue()


def run_tests() -> int:
    if not UNR.is_file():
        print("FAIL: missing sokoban.unr")
        return 1
    text = UNR.read_text(encoding="utf-8")
    body = "".join(ch for ch in text if not ch.isspace())
    if not body or set(body) - set("'\""):
        print("FAIL: sokoban.unr is not pure quote Unreadable")
        return 1
    print(f"ok pure length={len(text)}")

    try:
        exprs = parse_program(text)
    except ParseError as e:
        print("FAIL parse:", e)
        return 1
    print(f"ok parse roots={len(exprs)}")

    # quit immediately
    out = _run_with_input("q\n")
    if "sokoban_unreadable" not in out:
        print("FAIL banner:\n", out[:400])
        return 1
    if "#######" not in out:
        print("FAIL board not printed:\n", out[:400])
        return 1
    if "bye" not in out:
        print("FAIL no bye:\n", out[-200:])
        return 1
    print("ok quit smoke")

    # one move right then quit
    out2 = _run_with_input("d\nq\n")
    if "moves=1" not in out2:
        print("FAIL push/move smoke (expected moves=1):\n", out2[-500:])
        return 1
    print("ok move smoke")

    # reset after move
    out3 = _run_with_input("d\nr\nq\n")
    if "moves=0" not in out3:
        print("FAIL reset smoke:\n", out3[-500:])
        return 1
    print("ok reset smoke")

    print("PASS")
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in ("--test", "-t"):
        return run_tests()
    if len(sys.argv) > 1 and sys.argv[1] in ("--rebuild",):
        return rebuild()
    return run_game()


if __name__ == "__main__":
    raise SystemExit(main())
