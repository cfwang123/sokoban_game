# -*- coding: utf-8 -*-
"""从 res/levels_demo.json 生成 src/levels_data.c / include levels_data.h"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "res" / "levels_demo.json"
levels = json.loads(src.read_text(encoding="utf-8"))


def c_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


h_lines = [
    "/* 自动生成：演示关卡表（文曲星工程） */",
    "#ifndef WQX_LEVELS_DATA_H",
    "#define WQX_LEVELS_DATA_H",
    "",
    "#define WQX_LEVEL_COUNT " + str(len(levels)),
    "",
    "typedef struct {",
    "    const char *name;",
    "    const char *const *rows; /* NULL 结尾 */",
    "    const char *solution;    /* 可为空串 */",
    "} WqxLevel;",
    "",
    "extern const WqxLevel g_wqx_levels[WQX_LEVEL_COUNT];",
    "",
    "#endif",
    "",
]

c_lines = [
    "/* 自动生成：勿手改；重新生成: python tools/gen_levels.py */",
    '#include "levels_data.h"',
    "",
]

for i, lv in enumerate(levels):
    c_lines.append("static const char *const s_lv%d_rows[] = {" % i)
    for row in lv["puzzle"]:
        c_lines.append("    %s," % c_str(row))
    c_lines.append("    0")
    c_lines.append("};")
    c_lines.append("")

c_lines.append("const WqxLevel g_wqx_levels[WQX_LEVEL_COUNT] = {")
for i, lv in enumerate(levels):
    name = c_str(lv.get("name") or ("L%d" % (i + 1)))
    sol = c_str(lv.get("solution") or "")
    comma = "," if i < len(levels) - 1 else ""
    c_lines.append("    { %s, s_lv%d_rows, %s }%s" % (name, i, sol, comma))
c_lines.append("};")
c_lines.append("")

(ROOT / "include" / "levels_data.h").write_text("\n".join(h_lines), encoding="utf-8")
(ROOT / "src" / "levels_data.c").write_text("\n".join(c_lines), encoding="utf-8")
print("levels", len(levels))
