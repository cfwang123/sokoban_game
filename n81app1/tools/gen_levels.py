# -*- coding: utf-8 -*-
"""从 res/levels_demo.json 生成 LevelsData.java（可选维护脚本）。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "res" / "levels_demo.json"
out = ROOT / "src" / "com" / "whj" / "sokoban" / "LevelsData.java"
levels = json.loads(src.read_text(encoding="utf-8"))


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


lines = [
    "package com.whj.sokoban;",
    "",
    "/**",
    " * 关卡数据（教学演示子集，由 levels.json 导出）。",
    " * J2ME 常用做法：把资源编译进 class，避免运行时 JSON 解析库。",
    " */",
    "public final class LevelsData {",
    "    private LevelsData() {}",
    "",
    "    public static final int COUNT = " + str(len(levels)) + ";",
    "",
    "    public static String name(int index) {",
    "        return NAMES[index];",
    "    }",
    "",
    "    public static String[] puzzle(int index) {",
    "        return PUZZLES[index];",
    "    }",
    "",
    "    public static String solution(int index) {",
    "        return SOLUTIONS[index];",
    "    }",
    "",
    "    public static boolean hasSolution(int index) {",
    "        String s = SOLUTIONS[index];",
    "        return s != null && s.length() > 0;",
    "    }",
    "",
    "    private static final String[] NAMES = {",
]
for i, lv in enumerate(levels):
    comma = "," if i < len(levels) - 1 else ""
    lines.append('        "' + esc(lv.get("name", "")) + '"' + comma)
lines.append("    };")
lines.append("")
lines.append("    private static final String[][] PUZZLES = {")
for i, lv in enumerate(levels):
    lines.append("        { // " + str(i) + " " + esc(lv.get("name", "")))
    puzzle = lv["puzzle"]
    for j, row in enumerate(puzzle):
        c = "," if j < len(puzzle) - 1 else ""
        lines.append('            "' + esc(row) + '"' + c)
    c2 = "," if i < len(levels) - 1 else ""
    lines.append("        }" + c2)
lines.append("    };")
lines.append("")
lines.append("    private static final String[] SOLUTIONS = {")
for i, lv in enumerate(levels):
    sol = lv.get("solution") or ""
    comma = "," if i < len(levels) - 1 else ""
    lines.append('        "' + esc(sol) + '"' + comma)
lines.append("    };")
lines.append("}")

out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", out, "levels", len(levels))
