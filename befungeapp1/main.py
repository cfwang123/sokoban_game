#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
befungeapp1 — run pure Befunge Sokoban (sokoban.bf).

Python is only the interpreter (same policy as brainfuckapp1).

  python -X utf8 main.py
  python -X utf8 main.py --test
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

from befunge93 import Befunge93, load_bf_text

HERE = Path(__file__).resolve().parent
BF_FILE = HERE / "sokoban.bf"


def run_game() -> int:
    if not BF_FILE.is_file():
        print(f"missing {BF_FILE.name}", file=sys.stderr)
        return 1
    src = load_bf_text(BF_FILE.read_text(encoding="utf-8"))
    try:
        Befunge93(src).run()
    except RuntimeError as e:
        print(f"\nbefunge error: {e}", file=sys.stderr)
        return 1
    return 0


def run_tests() -> int:
    assert Befunge93('"!dlroW olleH">:#,_@', max_steps=10_000).run().startswith("Hello")
    assert Befunge93("88*1+,@", max_steps=1000).run() == "A"
    assert Befunge93('"A"22p22g,@', max_steps=1000).run() == "A"

    src = load_bf_text(BF_FILE.read_text(encoding="utf-8"))
    inp = io.StringIO("d\nq\n")
    out = io.StringIO()
    Befunge93(src, stdin=inp, stdout=out, max_steps=50_000_000).run()
    text = out.getvalue()
    assert "sokoban_befunge" in text, text[:200]
    assert "#######" in text
    assert "moves=" in text
    assert "*" in text
    print("PASS")
    return 0


def main() -> int:
    if "--test" in sys.argv or "-t" in sys.argv:
        return run_tests()
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__)
        return 0
    return run_game()


if __name__ == "__main__":
    raise SystemExit(main())
