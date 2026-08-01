# -*- coding: utf-8 -*-
"""Export mini_levels.json into several language snippets used by ports."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MINI_JSON = ROOT / "scripts" / "mini_levels.json"
if not MINI_JSON.exists():
    MINI_JSON = ROOT / "tmp" / "mini_levels.json"
mini = json.loads(MINI_JSON.read_text(encoding="utf-8"))


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


# Dart
dart = ["// generated mini levels", "const miniLevels = <Map<String, dynamic>>["]
for lv in mini:
    rows = ", ".join(f'"{esc(r)}"' for r in lv["puzzle"])
    dart.append(
        f'  {{"name": "{esc(lv["name"])}", "puzzle": [{rows}], "solution": "{esc(lv.get("solution") or "")}"}},'
    )
dart.append("];")
dart.append("")
(ROOT / "flutterapp1" / "lib" / "game" / "mini_levels.dart").write_text("\n".join(dart), encoding="utf-8")

# JS
# 微信小游戏 CommonJS
js = [
    "// generated mini levels",
    "const MINI_LEVELS = " + json.dumps(mini, ensure_ascii=False, indent=2) + ";",
    "module.exports = { MINI_LEVELS };",
    "",
]
(ROOT / "wxgame1" / "js" / "levels_mini.js").write_text("\n".join(js), encoding="utf-8")
(ROOT / "scripts" / "mini_levels.json").write_text(
    json.dumps(mini, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

# C header style
c = [
    "/* generated mini levels */",
    "#ifndef MINI_LEVELS_H",
    "#define MINI_LEVELS_H",
    f"#define MINI_LEVEL_COUNT {len(mini)}",
    "typedef struct { const char *name; const char *const *rows; const char *solution; } MiniLevel;",
]
for i, lv in enumerate(mini):
    c.append(f"static const char *const ml{i}_rows[] = {{")
    for r in lv["puzzle"]:
        c.append(f'  "{esc(r)}",')
    c.append("  0")
    c.append("};")
c.append("static const MiniLevel g_mini_levels[MINI_LEVEL_COUNT] = {")
for i, lv in enumerate(mini):
    comma = "," if i + 1 < len(mini) else ""
    c.append(f'  {{ "{esc(lv["name"])}", ml{i}_rows, "{esc(lv.get("solution") or "")}" }}{comma}')
c.append("};")
c.append("#endif")
c_text = "\n".join(c) + "\n"
for sub in ["esp32app1/main", "stm32app1/Core/Inc", "arduinoapp1", "linuxfbapp1/src", "casioapp1/src", "dosapp1/src"]:
    p = ROOT / sub
    p.mkdir(parents=True, exist_ok=True)
    name = "mini_levels.h" if "Inc" in sub or sub.endswith("src") or sub == "arduinoapp1" or sub.endswith("main") else "mini_levels.h"
    (p / "mini_levels.h").write_text(c_text, encoding="utf-8")

print("exported", len(mini), "levels")
