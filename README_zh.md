# 推箱子 (Sokoban)

> [English](README.md)

一个经典的推箱子益智游戏，提供控制台、网页与多种主机 homebrew 实现。

## 功能特点

- 经典推箱子玩法，内置多个关卡（`levels.json`）
- **C 控制台版** — 轻量级终端游戏
- **多语言终端版** — Python / PHP / Lua / Node.js / Ruby / Java / C# / Kotlin / Perl / R / Haskell / Rust / Go / Zig / C++ / …
- **古典与扩展语言终端版** — Lisp / Scheme / COBOL / Fortran / Pascal / Prolog / BASIC / Ada / Forth / Tcl / OCaml / Clojure / F# / Scala / Elixir / Erlang / Nim / …（完整清单见 [TODO.md](TODO.md)）
- **桌面图形 demo** — Pygame / Qt / Electron / SDL2 / Godot / raylib
- **2D / 3D 网页版** — 浏览器游玩（3D 基于 three.js）
- **Android** — `androidapp1/`（Kotlin，点击寻路 + 图标虚拟键；见 [更新日志](androidapp1/CHANGELOG.md)）
- **iOS** — `iosapp1/`（SwiftUI 教学演示源码，不要求在本仓库编译；见 [说明](iosapp1/README.md)）
- **Nokia N81** — `n81app1/`（Java ME MIDP 教学演示，不要求编译；见 [说明](n81app1/README.md)）
- **文曲星** — `wqxapp1/`（步步高文曲星类词典 C + HAL 教学工程，不要求编固件；见 [说明](wqxapp1/README.md)）
- **多技术栈教学工程** — 桌面/移动/嵌入式/掌机/编辑器与浏览器扩展等（见 [TODO.md](TODO.md)）
- **FC / NES** — `fcapp1/`（cc65，`sokoban.nes`）
- **GB / GBC** — `gbapp1/` · `gbcapp1/`（教学骨架，GBDK）
- **NDS** — `ndsapp1/`（双屏教学骨架，libnds）
- **GBA** — `gbaapp1/`（裸机 Mode 3，`sokoban.gba`）
- **PSP** — `pspapp1/`（pspdev + sceGu，`EBOOT.PBP`）
- 内置寻路 / 答案回放（视平台而定）
- 关卡数据 JSON，便于编辑与转换

## 项目结构

```
sokoban/
├── c_app/               # C 控制台（Windows）
├── sokoban_linux/       # C 控制台（Linux）
├── html_app/            # 2D 网页
├── html_3dapp/          # 3D 网页（three.js）
├── androidapp1/         # Android 原生版
├── iosapp1/             # iOS SwiftUI 教学演示
├── n81app1/             # Nokia N81 Java ME 教学演示
├── wqxapp1/             # 步步高文曲星 C 教学工程
├── flutterapp1/         # Flutter
├── unityapp1/           # Unity C# 脚本
├── rustapp1/            # Rust
├── goapp1/              # Go
├── zigapp1/             # Zig
├── pythonapp1/          # Python 终端
├── phpapp1/             # PHP 终端
├── luaapp1/             # Lua 终端
├── nodejsapp1/          # Node.js 终端
├── rubyapp1/            # Ruby 终端
├── javaapp1/            # Java 终端
├── csharpapp1/          # C# 终端
├── kotlinapp1/          # Kotlin 终端
├── perlapp1/            # Perl 终端
├── rapp1/               # R 终端
├── haskellapp1/         # Haskell 终端
├── lispapp1/            # Common Lisp 终端
├── schemeapp1/          # Scheme 终端
├── cobolapp1/           # COBOL 终端
├── fortranapp1/         # Fortran 终端
├── pascalapp1/          # Pascal 终端
├── prologapp1/          # Prolog 终端
├── basicapp1/           # FreeBASIC 终端
├── adaapp1/             # Ada 终端
├── forthapp1/           # Forth 终端
├── tclapp1/             # Tcl 终端
├── ocamlapp1/           # OCaml 终端
├── clojureapp1/         # Clojure 终端
├── fsharpapp1/          # F# 终端
├── scalaapp1/           # Scala 终端
├── elixirapp1/          # Elixir 终端
├── erlangapp1/          # Erlang 终端
├── nimapp1/             # Nim 终端
├── crystalapp1/         # Crystal 终端
├── dlangapp1/           # D 终端
├── swiftapp1/           # Swift CLI 终端
├── dartapp1/            # Dart CLI 终端
├── juliaapp1/           # Julia 终端
├── powershellapp1/      # PowerShell 终端
├── bashapp1/            # Bash 终端
├── awkapp1/             # AWK 终端
├── sqlapp1/             # SQL/SQLite 终端
├── cppapp1/             # C++ 终端
├── groovyapp1/          # Groovy 终端
├── vapp1/               # V 终端
├── odinapp1/            # Odin 终端
├── smalltalkapp1/       # Smalltalk 终端
├── modula2app1/         # Modula-2 终端
├── algolapp1/           # Algol 68 终端
├── iconapp1/            # Icon 终端
├── rexxapp1/            # REXX 终端
├── logoapp1/            # Logo 终端
├── aplapp1/             # APL 终端
├── factorapp1/          # Factor 终端
├── pygameapp1/          # Pygame（仿 html_app 2D）
├── qtapp1/              # Qt Widgets 桌面
├── electronapp1/        # Electron 桌面
├── sdlapp1/             # SDL2 桌面
├── godotapp1/           # Godot 4 桌面
├── raylibapp1/          # raylib 桌面
├── wxgame1/             # 微信小游戏
├── harmonyapp1/         # HarmonyOS ArkTS
├── esp32app1/           # ESP32 (ESP-IDF)
├── stm32app1/           # STM32
├── arduinoapp1/         # Arduino
├── linuxfbapp1/         # Linux 帧缓冲
├── casioapp1/           # Casio 计算器抽象
├── dosapp1/             # DOS
├── gbapp1/              # Game Boy 教学
├── gbcapp1/             # Game Boy Color 教学
├── ndsapp1/             # Nintendo DS 教学
├── vscodeext1/          # VS Code 扩展
├── vs2026ext1/          # Visual Studio 扩展教学
├── chromeext1/          # Chrome 扩展
├── edgeext1/            # Edge 扩展
├── firefoxext1/         # Firefox 扩展
├── vimext1/             # Vim 插件
├── nvimext1/            # Neovim Lua 插件
├── safariext1/          # Safari Web Extension
├── emacsext1/           # Emacs 插件
├── jetbrainsext1/       # JetBrains IDE 插件
├── fcapp1/              # FC / NES homebrew
├── gbaapp1/             # GBA homebrew
├── pspapp1/             # PSP homebrew
├── scripts/             # 求解与转换脚本
├── TODO.md              # 多平台移植清单
├── levels.json          # 关卡定义
└── documents/           # 截图等
```

## 截图

| C 控制台版 | 2D 网页版 | 3D 网页版 |
|:---:|:---:|:---:|
| ![C 推箱子](documents/c_sokoban.png) | ![HTML 推箱子](documents/html_sokoban.png) | ![3D 推箱子](documents/html_3d.png) |

## 快速开始

### 2D 网页版

直接用浏览器打开 `index.html` 即可，无需启动服务器。

### 3D 网页版

建议通过本地 HTTP 服务器打开 `html_3dapp/index.html`。

示例：

```bash
cd html_3dapp
python -m http.server 8765
```

然后访问 `http://localhost:8765/`。

### Android 版

见 [androidapp1/README.md](androidapp1/README.md) · [更新日志](androidapp1/CHANGELOG.md)。

需要 Android SDK、JDK 17+，并在 `androidapp1/local.properties` 中配置 `sdk.dir`（勿提交该文件）。

```bat
cd androidapp1
gradlew.bat assembleDebug
```

Debug APK：`androidapp1/app/build/outputs/apk/debug/app-debug.apk`

### iOS 版（教学演示）

见 [iosapp1/README.md](iosapp1/README.md) · [更新日志](iosapp1/CHANGELOG.md) · [开发速查](iosapp1/Sokoban/DEVELOPMENT.md)。

SwiftUI 完整源码，演示 iOS 工程组织与和 Android 的对照；**不要求在本仓库内编译**。在 Mac 上用 Xcode 新建 App 工程并导入 `iosapp1/Sokoban/` 即可运行。

### Nokia N81 版（Java ME 教学演示）

见 [n81app1/README.md](n81app1/README.md) · [更新日志](n81app1/CHANGELOG.md) · [开发速查](n81app1/docs/DEVELOPMENT.md)。

MIDP 2.0 MIDlet 源码，演示功能机 Java 生命周期、`Canvas` 绘制与键盘操作；**不要求在本仓库内编译**。

### 文曲星版（电子词典 C 教学工程）

见 [wqxapp1/README.md](wqxapp1/README.md) · [更新日志](wqxapp1/CHANGELOG.md) · [开发速查](wqxapp1/docs/DEVELOPMENT.md)。

面向步步高文曲星类词典的 C 工程分层（`wqx_api` HAL + 玩法核心）；**不要求编出真机固件**。

### 其它技术栈教学工程

进度与说明见 **[TODO.md](TODO.md)**。各目录均有独立 README（多数为演示/骨架，不强制本机工具链）：

| 目录 | 技术 |
|------|------|
| `flutterapp1/` | Flutter |
| `unityapp1/` | Unity C# |
| `rustapp1/` | Rust |
| `goapp1/` | Go |
| `zigapp1/` | Zig |
| `pythonapp1/` | Python 终端 |
| `phpapp1/` | PHP 终端 |
| `luaapp1/` | Lua 终端 |
| `nodejsapp1/` | Node.js 终端 |
| `rubyapp1/` | Ruby 终端 |
| `javaapp1/` | Java 终端 |
| `csharpapp1/` | C# 终端 |
| `kotlinapp1/` | Kotlin 终端 |
| `perlapp1/` | Perl 终端 |
| `rapp1/` | R 终端 |
| `haskellapp1/` | Haskell 终端 |
| `lispapp1/` | Common Lisp 终端 |
| `schemeapp1/` | Scheme 终端 |
| `cobolapp1/` | COBOL 终端 |
| `fortranapp1/` | Fortran 终端 |
| `pascalapp1/` | Pascal 终端 |
| `prologapp1/` | Prolog 终端 |
| `basicapp1/` | FreeBASIC 终端 |
| `adaapp1/` … `factorapp1/` | 古典/扩展语言（见 [TODO.md](TODO.md)） |
| `pygameapp1/` | Pygame（仿 2D 网页） |
| `qtapp1/` | Qt Widgets |
| `electronapp1/` | Electron |
| `sdlapp1/` | SDL2（SFML 可同理） |
| `godotapp1/` | Godot 4 |
| `raylibapp1/` | raylib |
| `wxgame1/` | 微信小游戏 |
| `harmonyapp1/` | HarmonyOS ArkTS |
| `esp32app1/` | ESP32 |
| `stm32app1/` | STM32 |
| `arduinoapp1/` | Arduino |
| `linuxfbapp1/` | Linux fbdev |
| `casioapp1/` | Casio 计算器 |
| `dosapp1/` | DOS |
| `gbapp1/` | Game Boy |
| `gbcapp1/` | Game Boy Color |
| `ndsapp1/` | Nintendo DS |
| `vscodeext1/` | VS Code 扩展（Webview） |
| `vs2026ext1/` | Visual Studio 扩展（Tool Window 示意） |
| `chromeext1/` | Chrome 扩展（MV3 popup） |
| `edgeext1/` | Edge 扩展（与 Chrome 同源） |
| `firefoxext1/` | Firefox 扩展 |
| `vimext1/` | Vim：`:Sokoban` |
| `nvimext1/` | Neovim Lua：`:Sokoban` |
| `safariext1/` | Safari 扩展（需 Xcode 包装） |
| `emacsext1/` | Emacs：`M-x sokoban` |
| `jetbrainsext1/` | IntelliJ 系 Tool Window 示意 |

### C 控制台版

```bash
cd c_app
make
./sokoban.exe
```

需要 C 编译器（Windows 下推荐 GCC / MinGW）。

### 多语言终端版

教学用迷你关卡，操作均为 WASD + z 撤销 + r 重置 + q 退出。

```bash
cd pythonapp1  && python -X utf8 main.py
cd phpapp1     && php main.php
cd luaapp1     && lua main.lua
cd nodejsapp1  && node main.js
cd rubyapp1    && ruby main.rb
cd javaapp1    && javac *.java && java Main
cd csharpapp1  && dotnet run
cd kotlinapp1  && kotlinc Game.kt Main.kt -include-runtime -d sokoban.jar && java -jar sokoban.jar
cd perlapp1    && perl main.pl
cd rapp1       && Rscript main.R
cd haskellapp1 && ghc Main.hs Game.hs -o sokoban && ./sokoban
# 古典 / 历史语言
cd lispapp1    && sbcl --script main.lisp
cd schemeapp1  && guile -l game.scm -s main.scm
cd cobolapp1   && cobc -x -free main.cbl game.cbl -o sokoban && ./sokoban
cd fortranapp1 && gfortran -O2 game.f90 main.f90 -o sokoban && ./sokoban
cd pascalapp1  && fpc -O2 main.pas && ./main
cd prologapp1  && swipl -q -s main.pl
cd basicapp1   && fbc -O 2 main.bas && ./main
# 更多古典 / 现代语言（摘要，完整见 TODO.md）
cd adaapp1         && gnatmake main.adb
cd tclapp1         && tclsh main.tcl
cd ocamlapp1       && ocamlc -o sokoban game.ml main.ml && ./sokoban
cd clojureapp1     && clj -M main.clj
cd fsharpapp1      && dotnet run
cd cppapp1         && g++ -std=c++17 -O2 main.cpp -o sokoban && ./sokoban
cd powershellapp1  && pwsh -File main.ps1
cd bashapp1        && bash main.sh
cd sqlapp1         && python -X utf8 main.py
cd juliaapp1       && julia main.jl
cd nimapp1         && nim c -r main.nim
cd dartapp1        && dart run main.dart
cd groovyapp1      && groovy main.groovy
# … 其余目录均有独立 README
```

### 桌面图形 demo

| 目录 | 运行要点 |
|------|----------|
| [pygameapp1](pygameapp1/README.md) | `pip install pygame` → `python main.py`（读全量 `levels.json`） |
| [qtapp1](qtapp1/README.md) | `qmake && make` |
| [electronapp1](electronapp1/README.md) | `npm install && npm start` |
| [sdlapp1](sdlapp1/README.md) | 需 SDL2 → `make` |
| [godotapp1](godotapp1/README.md) | Godot 4 打开 `project.godot` |
| [raylibapp1](raylibapp1/README.md) | 需 raylib → `make` |

### FC / NES 版

见 [fcapp1/README.md](fcapp1/README.md)。用任意 FC 模拟器打开 `fcapp1/sokoban.nes`。

```bat
cd fcapp1
build.bat
```

### GBA 版

见 [gbaapp1/README.md](gbaapp1/README.md)。用 mGBA 等打开 `gbaapp1/sokoban.gba`。

```bat
cd gbaapp1
build.bat
```

### PSP 版

见 [pspapp1/README.md](pspapp1/README.md)。用 PPSSPP 打开 `pspapp1/EBOOT.PBP`。

推荐 **WSL Ubuntu + ~/pspdev**：

```bat
cd pspapp1
build_wsl.bat
```

## 操作说明

### C 控制台版

| 按键             | 功能          |
|----------------|-------------|
| 方向键 / WASD    | 移动玩家       |
| Z              | 撤销上一步      |
| R              | 重置关卡       |
| F1             | AI 自动求解    |
| F2             | 选择关卡       |
| Space          | 下一关（通关后）  |
| PageUp         | 上一关        |
| PageDown       | 下一关        |
| Q / Esc        | 退出          |

### 2D 网页版

| 按键             | 功能          |
|----------------|-------------|
| 方向键 / WASD    | 移动玩家       |
| Z              | 撤销上一步      |
| R              | 重置关卡       |
| F1             | 查看答案       |
| Space          | 下一关（通关后）  |
| PageUp         | 上一关        |
| PageDown       | 下一关        |

### 3D 网页版

| 按键 / 鼠标       | 功能          |
|----------------|-------------|
| 方向键 / WASD    | 移动玩家       |
| Z              | 撤销上一步      |
| R              | 重置关卡       |
| F1             | 查看答案       |
| Space          | 下一关（通关后）  |
| PageUp         | 上一关        |
| PageDown       | 下一关        |
| 鼠标拖拽         | 旋转视角       |

## 许可证

MIT
