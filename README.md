# Sokoban

> [中文版](README_zh.md)

A classic Sokoban puzzle game implemented in **C (console)**, **JavaScript (2D web)**, and **three.js (3D web)**.

## Features

- Classic Sokoban gameplay with multiple levels
- **C console version** — lightweight terminal-based game
- **Web version** — playable in browser with a clean 2D UI
- **3D web version** — built with three.js, featuring a top-down default camera, mouse rotation, and stylized 3D warehouse visuals
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
├── js/                  # 2D web version (JavaScript)
│   ├── game.js          # Game engine
│   ├── levels.js        # Level loader
│   ├── levels_data.js   # Built-in level data
│   ├── ai.js            # AI solver
│   └── pathfinding.js   # Pathfinding
├── html_app/            # Standalone 2D web app
│   ├── index.html
│   ├── style.css
│   └── js/
├── html_3dapp/          # Standalone 3D web app (three.js)
│   ├── index.html
│   ├── style.css
│   └── js/
├── scripts/             # Utility scripts
│   ├── solve_levels.js  # Batch solver
│   ├── convert_levels.js
│   └── ...
├── index.html           # Web entry point
├── style.css            # Web styles
└── levels.json          # Level definitions
```

## Screenshots

| C Console Version | 2D Web Version | 3D Web Version |
|:---:|:---:|:---:|
| ![C Sokoban](documents/c_sokoban.png) | ![HTML Sokoban](documents/html_sokoban.png) | ![3D HTML Sokoban](documents/html_3d.png) |

## Getting Started

### 2D Web Version

Open `index.html` in any modern browser. No server required.

### 3D Web Version

Open `html_3dapp/index.html` in a modern browser through a local HTTP server.

Example:

```bash
cd html_3dapp
python -m http.server 8765
```

Then visit `http://localhost:8765/`.

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

### 2D Web Version

| Key              | Action          |
|------------------|----------------|
| Arrow keys / WASD | Move player    |
| Z                | Undo move      |
| R                | Reset level    |
| F1               | View answer    |
| Space            | Next level (when won) |
| PageUp           | Previous level |
| PageDown         | Next level     |

### 3D Web Version

| Key / Mouse       | Action          |
|-------------------|----------------|
| Arrow keys / WASD | Move player    |
| Z                 | Undo move      |
| R                 | Reset level    |
| F1                | View answer    |
| Space             | Next level (when won) |
| PageUp            | Previous level |
| PageDown          | Next level     |
| Mouse drag        | Rotate camera  |

## License

MIT
