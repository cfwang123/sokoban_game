# 推箱子 iOS 版 (iosapp1) — 教学演示

> [English](readme.md)


将 [`html_app`](../html_app) / [`androidapp1`](../androidapp1) 的推箱子逻辑用 **SwiftUI** 写成 iOS 应用源码，用于**演示 iOS 应用如何组织与开发**。

[更新日志](CHANGELOG.md)

**当前版本：1.0.0**

> **说明**  
> - 本目录提供完整、可读的 Swift 源码与资源，**不要求在本仓库内完成 Xcode 编译**。  
> - 在 Mac 上用 Xcode 按下文步骤新建工程并加入这些文件后，即可真机/模拟器运行。  
> - Windows 无法本地编译 iOS；结构与代码仍可阅读对照。

---

## 1. iOS 应用是怎么做出来的？

| 步骤 | 做什么 | 对应本工程 |
|------|--------|------------|
| 1. 安装工具 | Mac + [Xcode](https://developer.apple.com/xcode/)（含 iOS SDK、模拟器） | — |
| 2. 新建工程 | Xcode → File → New → Project → **App**；Interface: **SwiftUI**；Language: **Swift** | 入口见 `SokobanApp.swift` |
| 3. 写界面 | SwiftUI `View` 描述 UI；状态变化自动刷新 | `ContentView` / `GameBoardView` / `DPadView` |
| 4. 写逻辑 | 纯 Swift 类型，尽量与 UI 解耦 | `Game/` 下 `GameState`、`Pathfinding` 等 |
| 5. 加资源 | JSON、图片进 **Bundle** | `Resources/levels.json` |
| 6. 调试运行 | 选模拟器或真机 → Run (⌘R) | 需在 Xcode 中完成 |
| 7. 发布（可选） | 签名、Archive、App Store Connect | 本演示不做 |

与 **Android** 对照：

| 概念 | Android (`androidapp1`) | iOS (`iosapp1`) |
|------|-------------------------|-----------------|
| 工程构建 | Gradle (`build.gradle.kts`) | Xcode 工程 / SwiftPM |
| 入口 | `MainActivity` | `@main struct SokobanApp: App` |
| 布局 | XML + ViewBinding | SwiftUI `View` |
| 自定义绘制 | `GameBoardView` Canvas `onDraw` | SwiftUI `Canvas` |
| 状态刷新 | 手动 `invalidate` / 改 UI | `@Published` + `ObservableObject` |
| 持久化 | `SharedPreferences` | `UserDefaults` |
| 资源 | `assets/`、`res/` | Bundle / Asset Catalog |
| 系统图标 | Vector drawable | **SF Symbols**（`Image(systemName:)`） |

---

## 2. 在 Mac 上用本源码跑起来（可选）

1. 打开 Xcode → **Create a new Xcode project** → **iOS App**  
   - Product Name: `Sokoban`  
   - Interface: **SwiftUI**  
   - Language: **Swift**  
   - Bundle ID 自定，如 `com.example.sokoban`
2. 删除 Xcode 自动生成的示例 `ContentView` / `*App`（若与下列文件冲突）。
3. 将本仓库 `iosapp1/Sokoban/` 下全部 `.swift` 与 `Resources/levels.json` **拖入**工程，勾选 **Copy items if needed** 与你的 App Target。
4. 确认 `levels.json` 在 Target → **Build Phases → Copy Bundle Resources** 中。
5. 选 iPhone 模拟器 → **Run**。

最低系统建议：**iOS 16+**（使用了较新的 SwiftUI API；若目标更低可微调 `onChange` 等写法）。

---

## 3. 工程结构

```
iosapp1/
├── readme.zh.md              # 本说明（中文）
├── readme.md                 # English
├── CHANGELOG.md
├── .gitignore
└── Sokoban/
    ├── SokobanApp.swift      # @main 入口
    ├── ContentView.swift     # 主界面：工具栏 / 棋盘 / 方向键 / 通关
    ├── Info.plist            # 展示名、竖屏等（演示用）
    ├── Game/                 # 与 UI 解耦的游戏核心
    │   ├── Direction.swift
    │   ├── LevelData.swift
    │   ├── LevelRepository.swift
    │   ├── GameState.swift
    │   ├── Pathfinding.swift
    │   └── GameViewModel.swift   # ObservableObject，驱动界面
    ├── Views/
    │   ├── GameBoardView.swift   # Canvas 绘制 + 点击
    │   └── DPadView.swift        # 虚拟方向键
    └── Resources/
        └── levels.json           # 与仓库根目录 levels.json 同源
```

### 推荐阅读顺序

1. `SokobanApp.swift` — App 生命周期  
2. `ContentView.swift` — 界面如何拼起来  
3. `GameViewModel.swift` — 用户操作 → 改状态 → 刷新 UI  
4. `GameState.swift` / `Pathfinding.swift` — 与 Android/网页相同的玩法规则  
5. `GameBoardView.swift` — 自定义绘制与触摸坐标换算  

---

## 4. 功能（与 android / html 对齐）

| 能力 | 实现要点 |
|------|----------|
| 全部关卡 | `Bundle` 加载 `levels.json` |
| 点击空地 | `Pathfinding` BFS → 同步走完 |
| 点击相邻箱 | `tryMove` 推一格 |
| 虚拟方向键 | SF Symbol + 长按连发 |
| 撤销 / 重置 | 仅撤销推箱步 |
| 查看答案 | `Timer` 逐步回放 `solution` |
| 关卡记忆 | `UserDefaults` |
| 图标工具栏 | 单行，无横向滚动 |

---

## 5. 代码风格备忘（SwiftUI）

- **单向数据流**：`View` 只读 `ViewModel` 的 `@Published`，用户事件调用 `ViewModel` 方法。  
- **值类型 vs 引用类型**：关卡数据用 `struct`；可变盘面 `GameState` 用 `class` 便于原地修改。  
- **主线程 UI**：`@MainActor` 标在 `GameViewModel` 上，避免后台改 UI 状态。  
- **可访问性**：图标按钮设置 `accessibilityLabel`，VoiceOver 可读。  

---

## 6. 同步关卡

根目录 `levels.json` 更新后：

```bash
cp ../levels.json Sokoban/Resources/levels.json
```

---

## 参考

- 玩法：[`../html_app`](../html_app)  
- Android 对照：[`../androidapp1`](../androidapp1)  
- [SwiftUI 文档](https://developer.apple.com/documentation/swiftui)  
- [SF Symbols](https://developer.apple.com/sf-symbols/)  
