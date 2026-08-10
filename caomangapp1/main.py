#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""草蟒运行时：仅做中文关键字 → Python 翻译并执行 .草蟒 源码。

游戏逻辑全部在 游戏.草蟒 / 主程序.草蟒，本文件不是推箱子实现。
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# 长词优先
KW = [
    ("否则如果", "elif"),
    ("不是", "is not"),
    ("不在", "not in"),
    ("传递", "pass"),
    ("定义", "def"),
    ("返回", "return"),
    ("导入", "import"),
    ("从", "from"),
    ("如果", "if"),
    ("否则", "else"),
    ("当", "while"),
    ("对于", "for"),
    ("在", "in"),
    ("尝试", "try"),
    ("抓住", "except"),
    ("跳出", "break"),
    ("继续", "continue"),
    ("印出", "print"),
    ("输入", "input"),
    ("真", "True"),
    ("假", "False"),
    ("无", "None"),
    ("且", "and"),
    ("或", "or"),
    ("非", "not"),
    ("是", "is"),
    ("全部", "all"),
    ("枚举", "enumerate"),
    ("范围", "range"),
    ("最大", "max"),
    ("长度", "len"),
    ("整数", "int"),
]


def translate(src: str) -> str:
    parts: list[tuple[str, str]] = []
    i, n = 0, len(src)
    buf: list[str] = []
    while i < n:
        c = src[i]
        if c in "\"'":
            if buf:
                parts.append(("code", "".join(buf)))
                buf = []
            quote = c
            j = i + 1
            while j < n:
                if src[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                if src[j] == quote:
                    j += 1
                    break
                j += 1
            # f-string: previous char f already in buf handled if we flush before
            parts.append(("str", src[i:j]))
            i = j
            continue
        buf.append(c)
        i += 1
    if buf:
        parts.append(("code", "".join(buf)))
    out: list[str] = []
    for kind, text in parts:
        if kind == "str":
            out.append(text)
            continue
        s = text
        for zh, en in KW:
            s = s.replace(zh, en)
        out.append(s)
    return "".join(out)


def load_caomang(path: Path, mod_name: str):
    raw = path.read_text(encoding="utf-8")
    py = translate(raw)
    mod = types.ModuleType(mod_name)
    mod.__file__ = str(path)
    sys.modules[mod_name] = mod
    exec(compile(py, str(path), "exec"), mod.__dict__)
    return mod


def main() -> None:
    load_caomang(ROOT / "游戏.草蟒", "游戏")
    main_path = ROOT / "主程序.草蟒"
    py = translate(main_path.read_text(encoding="utf-8"))
    g = {"__name__": "__main__", "__file__": str(main_path)}
    # 保留 argv
    exec(compile(py, str(main_path), "exec"), g)


if __name__ == "__main__":
    main()
