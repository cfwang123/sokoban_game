# Sokoban

> [中文版](README_zh.md)

A classic Sokoban puzzle game with **console**, **web**, and **console homebrew** ports.

## Features

- Classic Sokoban gameplay with many levels (`levels.json`)
- **C console** — lightweight terminal game
- **2D / 3D web** — browser play (3D uses three.js)
- **Android** — `androidapp1/` (Kotlin, tap pathfinding + icon pad; [changelog](androidapp1/CHANGELOG.md))
- **iOS** — `iosapp1/` (SwiftUI teaching sources; no in-repo build required; [docs](iosapp1/README.md))
- **Nokia N81** — `n81app1/` (Java ME MIDP teaching demo; no build required; [docs](n81app1/README.md))
- **Wenquxing** — `wqxapp1/` (BBK e-dictionary C + HAL teaching project; no firmware build; [docs](wqxapp1/README.md))
- **Multi-stack teaching ports** — Flutter, Unity, Rust, Go, Zig, WeChat mini-game, HarmonyOS, ESP32, STM32, Arduino, Linux fbdev, Casio, DOS (see [TODO.md](TODO.md))
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
├── androidapp1/         # Android native app
├── iosapp1/             # iOS SwiftUI teaching demo
├── n81app1/             # Nokia N81 Java ME teaching demo
├── wqxapp1/             # BBK Wenquxing e-dictionary C teaching project
├── flutterapp1/         # Flutter
├── unityapp1/           # Unity C# scripts
├── rustapp1/            # Rust
├── goapp1/              # Go
├── zigapp1/             # Zig
├── wxgame1/             # WeChat mini-game
├── harmonyapp1/         # HarmonyOS ArkTS
├── esp32app1/           # ESP32 (ESP-IDF)
├── stm32app1/           # STM32
├── arduinoapp1/         # Arduino
├── linuxfbapp1/         # Linux framebuffer
├── casioapp1/           # Casio calculator abstraction
├── dosapp1/             # DOS
├── fcapp1/              # FC / NES homebrew
├── gbaapp1/             # GBA homebrew
├── pspapp1/             # PSP homebrew
├── scripts/             # Solvers and converters
├── TODO.md              # Multi-platform port checklist
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

### Android

See [androidapp1/README.md](androidapp1/README.md) · [changelog](androidapp1/CHANGELOG.md).

Requires Android SDK, JDK 17+, and `androidapp1/local.properties` with `sdk.dir` (do not commit that file).

```bat
cd androidapp1
gradlew.bat assembleDebug
```

Debug APK: `androidapp1/app/build/outputs/apk/debug/app-debug.apk`

### iOS (teaching demo)

See [iosapp1/README.md](iosapp1/README.md) · [changelog](iosapp1/CHANGELOG.md) · [dev cheat sheet](iosapp1/Sokoban/DEVELOPMENT.md).

Full SwiftUI sources showing how an iOS app is structured (and how it maps to Android). **Not required to compile in this repo.** On a Mac, create an Xcode App project and add `iosapp1/Sokoban/` to run.

### Nokia N81 (Java ME teaching demo)

See [n81app1/README.md](n81app1/README.md) · [changelog](n81app1/CHANGELOG.md) · [dev notes](n81app1/docs/DEVELOPMENT.md).

MIDP 2.0 MIDlet sources for feature-phone Java (lifecycle, `Canvas`, keypad). **Not required to compile in this repo.**

### Wenquxing (BBK e-dictionary, C teaching project)

See [wqxapp1/README.md](wqxapp1/README.md) · [changelog](wqxapp1/CHANGELOG.md) · [dev notes](wqxapp1/docs/DEVELOPMENT.md).

Portable C Sokoban with a `wqx_api` HAL for dictionary-class devices. **Not required to build device firmware in this repo.**

### Other teaching stacks

See **[TODO.md](TODO.md)**. Each folder has its own README (mostly demos/skeletons; full toolchains not required in-repo): Flutter, Unity, Rust, Go, Zig, WeChat mini-game, HarmonyOS, ESP32, STM32, Arduino, Linux fbdev, Casio, DOS.

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
