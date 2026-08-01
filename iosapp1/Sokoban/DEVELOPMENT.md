# iOS 开发要点速查（配合源码阅读）

## App 入口

```swift
@main
struct SokobanApp: App {
    var body: some Scene {
        WindowGroup { ContentView() }
    }
}
```

- `@main`：进程入口，类似 `main()` / Android `Application`+启动 Activity。  
- `WindowGroup`：窗口场景；iPhone 单窗口即可。

## 状态与刷新

```swift
@MainActor
final class GameViewModel: ObservableObject {
    @Published private(set) var state: GameState?
}

struct ContentView: View {
    @StateObject private var model = GameViewModel()
    // model 变化 → body 重算
}
```

| 属性包装器 | 用途 |
|------------|------|
| `@StateObject` | View 拥有并创建的 `ObservableObject` |
| `@ObservedObject` | 外部传入的已有对象 |
| `@Published` | 属性变化时通知订阅者 |
| `@State` | 仅本 View 私有的轻量状态 |

## 资源加载

```swift
Bundle.main.url(forResource: "levels", withExtension: "json")
```

必须把文件加入 Target 的 **Copy Bundle Resources**，否则运行时找不到。

## 自定义绘制

`Canvas { context, size in ... }` ≈ Android `Canvas.onDraw` / HTML `<canvas>`。  
触摸用 `DragGesture(minimumDistance: 0)` 取 `location`，再换算格子坐标。

## 与 androidapp1 文件映射

| androidapp1 | iosapp1 |
|-------------|---------|
| `MainActivity.kt` | `ContentView.swift` + `GameViewModel.swift` |
| `GameState.kt` | `GameState.swift` |
| `Pathfinding.kt` | `Pathfinding.swift` |
| `LevelRepository.kt` | `LevelRepository.swift` |
| `GameBoardView.kt` | `Views/GameBoardView.swift` |
| `activity_main.xml` | `ContentView` 布局表达式 |
| `assets/levels.json` | `Resources/levels.json` |

## 真机调试注意

- 需 Apple ID 登录 Xcode → Signing & Capabilities。  
- 免费账号真机调试有期限；上架需开发者计划。  
- 本演示仓库**不包含**签名证书与 `.xcodeproj` 二进制细节，避免平台/路径绑定。  
