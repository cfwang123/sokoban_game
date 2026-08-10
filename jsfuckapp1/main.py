#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""jsfuckapp1 — 运行纯 JSFuck 推箱子。

游戏逻辑全部在 ``sokoban.jsfuck.js``（仅含 ``[]()!+``）中。
本文件只启动 Node 执行该程序（对照 brainfuckapp1：解释器/宿主不写玩法）。

  python -X utf8 main.py
  python -X utf8 main.py --test
  python -X utf8 main.py --rebuild   # 从 game_src.js 重新编码（需 jsfuck_lib.js）
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
PURE = DIR / "sokoban.jsfuck.js"
SRC = DIR / "game_src.js"
LIB = DIR / "jsfuck_lib.js"
PURE_CHARS = re.compile(r"^[\[\]()!+\s]+$")


def run_game() -> int:
    if not PURE.is_file():
        print(f"missing {PURE.name}; run: python -X utf8 main.py --rebuild", file=sys.stderr)
        return 1
    try:
        return subprocess.call(["node", str(PURE)], cwd=str(DIR))
    except FileNotFoundError:
        print("need Node.js to run pure JSFuck (sokoban.jsfuck.js is valid JS)", file=sys.stderr)
        return 1


def is_pure_jsfuck(text: str) -> bool:
    body = "".join(ch for ch in text if not ch.isspace())
    if not body:
        return False
    return all(c in "[]()!+" for c in body)


def rebuild() -> int:
    if not SRC.is_file() or not LIB.is_file():
        print("need game_src.js and jsfuck_lib.js", file=sys.stderr)
        return 1
    script = r"""
const fs = require('fs');
const { JSFuck } = require('./jsfuck_lib.js');
const src = fs.readFileSync('./game_src.js', 'utf8');
const pure = JSFuck.encode(src, true, true);
if (!/^[\[\]()!+]+$/.test(pure)) {
  console.error('encode produced non-pure output');
  process.exit(1);
}
fs.writeFileSync('./sokoban.jsfuck.js', pure + '\n');
console.log('wrote sokoban.jsfuck.js', pure.length, 'chars');
if (fs.existsSync('./game_src_browser.js')) {
  const bsrc = fs.readFileSync('./game_src_browser.js', 'utf8');
  const bp = JSFuck.encode(bsrc, true, true);
  fs.writeFileSync('./sokoban.browser.jsfuck.js', bp + '\n');
  console.log('wrote sokoban.browser.jsfuck.js', bp.length, 'chars');
}
"""
    r = subprocess.run(
        ["node", "-e", script],
        cwd=str(DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    sys.stdout.write(r.stdout or "")
    if r.returncode != 0:
        sys.stderr.write(r.stderr or "")
        return r.returncode
    return 0


def run_tests() -> int:
    if not PURE.is_file():
        print("FAIL: missing sokoban.jsfuck.js")
        return 1
    text = PURE.read_text(encoding="utf-8")
    if not is_pure_jsfuck(text):
        print("FAIL: sokoban.jsfuck.js is not pure []()!+")
        return 1
    print(f"ok pure length={len(text.strip())}")

    # smoke: encode 1+1
    r = subprocess.run(
        [
            "node",
            "-e",
            "const {JSFuck}=require('./jsfuck_lib.js');"
            "const p=JSFuck.encode('return 1+1',true,false);"
            "if(!/^[\\[\\]()!+]+$/.test(p)) process.exit(2);"
            "if(eval(p)!==2) process.exit(3);"
            "console.log('ok encode');",
        ],
        cwd=str(DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0:
        print("FAIL encode smoke:\n", r.stdout, r.stderr)
        return 1
    print((r.stdout or "").strip())

    # non-interactive: feed q immediately
    r2 = subprocess.run(
        ["node", str(PURE)],
        cwd=str(DIR),
        input="q\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    out = (r2.stdout or "") + (r2.stderr or "")
    if "sokoban_jsfuck" not in out and "#######" not in out:
        print("FAIL run smoke:\n", out[:500])
        return 1
    if "#######" not in out:
        print("FAIL: board not printed")
        return 1
    print("ok run smoke")

    # one push then quit
    r3 = subprocess.run(
        ["node", str(PURE)],
        cwd=str(DIR),
        input="d\nq\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    out3 = r3.stdout or ""
    if "moves=1" not in out3:
        print("FAIL push smoke (expected moves=1):\n", out3[-400:])
        return 1
    print("ok push smoke")
    print("PASS")
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in ("--test", "-t"):
        return run_tests()
    if len(sys.argv) > 1 and sys.argv[1] in ("--rebuild",):
        return rebuild()
    return run_game()


if __name__ == "__main__":
    sys.exit(main())
