# 推箱子 (Sokoban)

> [English](README.md)

一个经典的推箱子益智游戏，提供控制台、网页与多种主机 homebrew 实现。

## 功能特点

- 经典推箱子玩法，内置多个关卡（`levels.json`）
- **C 控制台版** — 轻量级终端游戏
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
