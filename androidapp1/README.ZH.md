# 推箱子 Android 版 (androidapp1)

> [English](README.md)


将 [`html_app`](../html_app) 2D 网页推箱子移植为原生 Android 应用。

[更新日志](CHANGELOG.md)

**当前版本：1.0.0**

## 功能

| 能力 | 说明 |
|------|------|
| 关卡 | 全部关卡（`assets/levels.json`，与仓库根目录 `levels.json` 同源） |
| 点击空地 | BFS 寻路，直接走到可达位置 |
| 点击箱子 | 相邻箱子向前推一格 |
| 虚拟方向键 | 点按一步，按住连发 |
| 撤销 / 重置 | 撤销只回退推箱步（与网页一致） |
| 查看答案 | 有 `solution` 的关卡可动画回放 / 停止 |
| 关卡切换 | 上一关、下一关、下拉选择 |
| 通关 | 遮罩提示 + 下一关 |
| 进度 | SharedPreferences 记住上次关卡 |

## 界面

- 顶部**单行图标工具栏**：上一关 · 关卡 · 步数 · 撤销 · 重置 · 答案 · 帮助 · 下一关（无横向滚动）
- 底部**图标方向键**
- 深色主题（对齐网页版配色）

## 技术概要

| 项 | 说明 |
|----|------|
| 包名 | `com.whj.sokoban` |
| 语言 | Kotlin |
| minSdk | 24（Android 7.0+） |
| targetSdk / compileSdk | 34 |
| 构建 | Gradle 8.4 + AGP 8.3.2 + ViewBinding |
| JDK | 17+ |

## 工程结构

```
androidapp1/
├── app/src/main/
│   ├── assets/levels.json
│   ├── java/com/whj/sokoban/
│   │   ├── MainActivity.kt
│   │   ├── game/              # GameState / Pathfinding / LevelRepository
│   │   └── ui/GameBoardView.kt
│   └── res/                   # 布局、图标、主题
├── CHANGELOG.md
├── build.gradle.kts
└── settings.gradle.kts
```

## 构建

需要 Android SDK、JDK 17+。在本机创建 `local.properties` 并设置 `sdk.dir`（该文件已在 `.gitignore` 中，勿提交）。

```bat
cd androidapp1
gradlew.bat assembleDebug
```

Debug APK：`app/build/outputs/apk/debug/app-debug.apk`

```bat
gradlew.bat assembleRelease
```

Release APK 文件名：`sokoban{versionName}.apk`（如 `sokoban1.0.0.apk`）。

安装到已连接设备：

```bat
adb install -r app\build\outputs\apk\debug\app-debug.apk
adb shell am start -n com.whj.sokoban/.MainActivity
```

## 同步关卡

若根目录 `levels.json` 更新，可覆盖拷贝到 assets：

```bat
copy /Y ..\levels.json app\src\main\assets\levels.json
```

## 参考

- 玩法与交互：[`../html_app`](../html_app)
- 仓库总览：[`../README.ZH.md`](../README.ZH.md)
