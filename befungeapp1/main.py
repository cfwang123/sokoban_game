#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""befungeapp1 — pure Befunge-93 Sokoban (interpreter host only)."""
from __future__ import annotations

import sys
from pathlib import Path

from befunge93 import Befunge93, load_bf_text

HERE = Path(__file__).resolve().parent
BF = HERE / "sokoban.bf"


def main() -> int:
    if not BF.is_file():
        print("missing sokoban.bf — run: python -X utf8 gen_sokoban.py", file=sys.stderr)
        return 1
    src = load_bf_text(BF.read_text(encoding="utf-8"))
    print("sokoban_befunge — pure Befunge-93", flush=True)
    print("keys: a/d move, q quit  |  level: #.$@#  (solve: a)", flush=True)
    print(flush=True)
    try:
        Befunge93(src, max_steps=50_000_000).run()
    except KeyboardInterrupt:
        print()
    except RuntimeError as e:
        print(e, file=sys.stderr)
        return 1
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
