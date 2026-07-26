# Sokoban

> [中文版](README_zh.md)

A classic Sokoban puzzle game with **console**, **web**, and **console homebrew** ports.

## Features

- Classic Sokoban gameplay with many levels (`levels.json`)
- **C console** — lightweight terminal game
- **2D / 3D web** — browser play (3D uses three.js)
- **FC / NES** — `fcapp1/` (cc65 → `sokoban.nes`)
- **GBA** — `gbaapp1/` (bare-metal Mode 3 → `sokoban.gba`)
- **PSP** — `pspapp1/` (pspdev + sceGu → `EBOOT.PBP`)
- Pathfinding / answer playback where supported
- JSON level data for easy editing

## Project Structure

```
sokoban/
├── c_app/               # C console (Windows)
├── sokoban_linux/       # C console (Linux)
├── html_app/            # 2D web app
├── html_3dapp/          # 3D web app (three.js)
├── fcapp1/              # FC / NES homebrew
├── gbaapp1/             # GBA homebrew
├── pspapp1/             # PSP homebrew
├── scripts/             # Solvers and converters
├── levels.json          # Level definitions
└── documents/           # Screenshots, etc.
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

### FC / NES

See [fcapp1/README.md](fcapp1/README.md). Open `fcapp1/sokoban.nes` in any NES emulator.

```bat
cd fcapp1
build.bat
```

### GBA

See [gbaapp1/README.md](gbaapp1/README.md). Open `gbaapp1/sokoban.gba` in mGBA, etc.

```bat
cd gbaapp1
build.bat
```

### PSP

See [pspapp1/README.md](pspapp1/README.md). Open `pspapp1/EBOOT.PBP` in PPSSPP.

Recommended build: **WSL Ubuntu + ~/pspdev**

```bat
cd pspapp1
build_wsl.bat
```

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
