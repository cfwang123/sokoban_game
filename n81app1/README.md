# Sokoban Nokia N81 (n81app1) — teaching demo

> [中文版](README.ZH.md)

**Java ME / MIDP 2.0** Sokoban sources for **Nokia N81** (Symbian S60 3rd Edition FP1), as a **teaching demo of feature-phone Java app structure**.

[Changelog](CHANGELOG.md) · [Dev notes](docs/DEVELOPMENT.md)

**Current version: 1.0.0**

> **Note**  
> - Complete readable J2ME sources and manifest samples; **build/packaging is not required inside this repo**.  
> - Gameplay aligned with [`html_app`](../html_app) / [`androidapp1`](../androidapp1), trimmed for N81 **no touchscreen, numeric keypad**.  
> - Demo level subset (~35 levels in `LevelsData.java`).

---

## 1. Why Java ME?

2000s Nokia S60 phones supported **MIDlets** (Java ME) in addition to Symbian C++:

- One JAR can run on many MIDP 2.0 devices (still need resolution/key mapping).  
- Low barrier: Java SE syntax with a smaller API surface.  
- Ship as `.jad` (descriptor) + `.jar` (bytecode + resources).

N81: **CLDC 1.1 + MIDP 2.0**.

---

## 2. Layout

```
n81app1/
├── README.md / README.ZH.md
├── CHANGELOG.md
├── .gitignore
├── bin/
│   ├── MANIFEST.MF      # jar manifest template
│   └── Sokoban.jad      # install descriptor (update Jar-Size after pack)
├── docs/DEVELOPMENT.md  # lifecycle / keys / mapping tables
├── res/levels_demo.json # level subset used to generate Java
└── src/com/whj/sokoban/
    ├── SokobanMIDlet.java   # MIDlet entry
    ├── GameCanvas.java      # paint + keys
    ├── GameState.java       # rules
    ├── Pathfinding.java     # BFS
    ├── LevelsData.java      # level constants
    ├── Prefs.java           # RMS save
    └── Direction.java
```

### Suggested reading order

1. `docs/DEVELOPMENT.md` — platform background  
2. `SokobanMIDlet.java` — lifecycle and menu  
3. `GameCanvas.java` — `paint` / `keyPressed`  
4. `GameState.java` / `Pathfinding.java` — same rule ideas as Android  

---

## 3. Features

| Feature | On N81 |
|---------|--------|
| Move / push | D-pad or 2/4/6/8 |
| Undo | left softkey or 7 (box pushes only) |
| Reset | 0 |
| Change level | 1 / 3 or menu |
| Solution | `*` play / stop (levels with solution) |
| Help | `#` or menu |
| Tap pathfinding | **no touch** → menu “demo BFS” |
| Remember level | RMS `RecordStore` |

---

## 4. vs androidapp1 / iosapp1

See Chinese doc tables and `docs/DEVELOPMENT.md` for full mapping of lifecycle, input, and persistence across the three teaching ports.

## Optional build sketch

```bat
cd n81app1
python -X utf8 tools\gen_levels.py
```

```text
javac -bootclasspath <midp-classes> -source 1.3 -target 1.3 -d classes src/com/whj/sokoban/*.java
jar cvfm Sokoban.jar bin/MANIFEST.MF -C classes .
# then set MIDlet-Jar-Size in the .jad
```
