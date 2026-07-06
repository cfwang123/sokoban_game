# Sokoban

> [中文版](README_zh.md)

A classic Sokoban puzzle game implemented in both **C (console)** and **JavaScript (web)**.

## Features

- Classic Sokoban gameplay with multiple levels
- **C console version** — lightweight terminal-based game
- **Web version** — playable in browser with a clean UI
- Built-in **pathfinding AI** to help solve puzzles
- Level solving and batch-solving scripts
- Level data in JSON format for easy editing

## Project Structure

```
sokoban/
├── c_app/               # C console application
│   ├── main.c           # Entry point
│   ├── game.c/h         # Game logic
│   ├── levels.c/h       # Level management
│   ├── pathfinding.c/h  # A* pathfinding
│   ├── console_win.c    # Windows console rendering
│   ├── console.h        # Console abstraction
│   ├── lib/cjson/       # JSON parser (cJSON)
│   └── Makefile         # Build system
├── js/                  # Web version (JavaScript)
│   ├── game.js          # Game engine
│   ├── levels.js        # Level loader
│   ├── levels_data.js   # Built-in level data
│   ├── ai.js            # AI solver
│   └── pathfinding.js   # Pathfinding
├── scripts/             # Utility scripts
│   ├── solve_levels.js  # Batch solver
│   ├── convert_levels.js
│   └── ...
├── index.html           # Web entry point
├── style.css            # Web styles
└── levels.json          # Level definitions
```

## Screenshots

| C Console Version | Web Version |
|:---:|:---:|
| ![C Sokoban](documents/c_sokoban.png) | ![HTML Sokoban](documents/html_sokoban.png) |

## Getting Started

### Web Version

Open `index.html` in any modern browser. No server required.

### C Console Version

```bash
cd c_app
make
./sokoban.exe
```

Requires a C compiler (e.g., GCC / MinGW on Windows).

## Controls

### C Console Version

| Key              | Action          |
|------------------|----------------|
| Arrow keys / WASD | Move player    |
| Z                | Undo move      |
| R                | Reset level    |
| F1               | AI solve       |
| F2               | Select level   |
| Space            | Next level (when won) |
| PageUp           | Previous level |
| PageDown         | Next level     |
| Q / Esc          | Quit           |

### Web Version

| Key              | Action          |
|------------------|----------------|
| Arrow keys / WASD | Move player    |
| Z                | Undo move      |
| R                | Reset level    |
| F1               | View answer    |
| Space            | Next level (when won) |
| PageUp           | Previous level |
| PageDown         | Next level     |

## License

MIT
