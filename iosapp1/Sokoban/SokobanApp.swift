import SwiftUI

/// App 入口（`@main`）
///
/// 教学要点：
/// - iOS 13+ 可用 SwiftUI App 生命周期，替代旧的 AppDelegate + SceneDelegate
/// - 一个 `WindowGroup` 对应一个窗口（iPhone 通常一个）
/// - 在 Xcode 新建工程时选 “App” + Interface: SwiftUI + Language: Swift
@main
struct SokobanApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
