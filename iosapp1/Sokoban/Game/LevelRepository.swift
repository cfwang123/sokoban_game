import Foundation

/// 从 App Bundle 加载 levels.json
///
/// iOS 资源约定：
/// - 在 Xcode 中把 `levels.json` 勾选进 Target → Copy Bundle Resources
/// - 运行时用 `Bundle.main.url(forResource:withExtension:)` 读取
enum LevelRepository {
    static func load() -> [LevelData] {
        guard let url = Bundle.main.url(forResource: "levels", withExtension: "json") else {
            // 演示工程未正确打包资源时的兜底：空列表
            print("[LevelRepository] levels.json not found in bundle")
            return []
        }
        do {
            let data = try Data(contentsOf: url)
            let decoded = try JSONDecoder().decode([LevelData].self, from: data)
            // 统一用数组下标作为关卡序号（与 android / 网页一致）
            return decoded.enumerated().map { index, lv in
                LevelData(id: index, name: lv.name, puzzle: lv.puzzle, solution: lv.solution)
            }
        } catch {
            print("[LevelRepository] decode failed: \(error)")
            return []
        }
    }
}
