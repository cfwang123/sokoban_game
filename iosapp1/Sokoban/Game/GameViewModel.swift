import Foundation
import Combine

/// 界面状态机：关卡、移动、答案回放、持久化
///
/// iOS 侧用 `ObservableObject` + `@Published` 驱动 SwiftUI 刷新，
/// 对应 Android 的 `MainActivity` 状态与回调。
@MainActor
final class GameViewModel: ObservableObject {
    @Published private(set) var levels: [LevelData] = []
    @Published private(set) var state: GameState?
    @Published private(set) var statusText: String = ""
    @Published private(set) var answerActive: Bool = false
    @Published private(set) var showWin: Bool = false
    /// 由界面绑定 alert；可写
    @Published var showHelp: Bool = false
    @Published var selectedLevelIndex: Int = 0

    private var animQueue: [Direction] = []
    private var animTimer: Timer?
    private var inputLocked: Bool = false

    private let lastLevelKey = "sokoban_last_level"
    private let animInterval: TimeInterval = 0.06

    init() {
        levels = LevelRepository.load()
        let last = UserDefaults.standard.integer(forKey: lastLevelKey)
        let idx = (last >= 0 && last < levels.count) ? last : 0
        loadLevel(idx)
    }

    // Timer 在 stop/clear 时清理；ViewModel 与界面同生命周期

    // MARK: - Level

    func loadLevel(_ index: Int) {
        guard !levels.isEmpty else { return }
        let i = min(max(0, index), levels.count - 1)
        stopAnswer(finished: true)
        clearAnim()
        state = GameState.from(level: levels[i], levelIndex: i)
        selectedLevelIndex = i
        showWin = false
        UserDefaults.standard.set(i, forKey: lastLevelKey)
        refreshStatus()
    }

    func resetLevel() {
        guard let s = state else { return }
        loadLevel(s.levelIndex)
    }

    func goPrevLevel() {
        guard let s = state else { return }
        if s.levelIndex > 0 { loadLevel(s.levelIndex - 1) }
    }

    func goNextLevel() {
        guard let s = state else { return }
        if s.levelIndex + 1 < levels.count {
            loadLevel(s.levelIndex + 1)
        } else {
            showWin = false
        }
    }

    // MARK: - Move

    func tryDirectionalMove(_ dir: Direction) {
        guard !inputLocked, !answerActive, let s = state, !s.won else { return }
        if s.tryMove(dir) {
            objectWillChange.send()
            refreshStatus()
            if s.won { showWin = true }
        }
    }

    func undo() {
        guard !inputLocked, !answerActive, let s = state, !s.won else { return }
        s.undo()
        objectWillChange.send()
        refreshStatus()
    }

    /// 棋盘点击：相邻箱推一格；空地 BFS 寻路
    func onCellTap(gridX: Int, gridY: Int) {
        guard !inputLocked, !answerActive, let s = state, !s.won else { return }

        if s.isBox(x: gridX, y: gridY) {
            let dx = gridX - s.player.x
            let dy = gridY - s.player.y
            if abs(dx) + abs(dy) == 1 {
                if s.tryMove(dx: dx, dy: dy) {
                    objectWillChange.send()
                    refreshStatus()
                    if s.won { showWin = true }
                }
            }
            return
        }

        if !s.isWall(x: gridX, y: gridY), !s.isBox(x: gridX, y: gridY) {
            guard let path = Pathfinding.findPath(state: s, targetX: gridX, targetY: gridY), !path.isEmpty else {
                return
            }
            for dir in path {
                s.tryMove(dir)
                if s.won { break }
            }
            objectWillChange.send()
            refreshStatus()
            if s.won { showWin = true }
        }
    }

    // MARK: - Answer playback

    func toggleAnswer() {
        if answerActive {
            stopAnswer(finished: false)
        } else {
            startAnswer()
        }
    }

    private func startAnswer() {
        guard let s = state, !s.won else { return }
        let level = levels[s.levelIndex]
        guard level.hasSolution, let sol = level.solution else {
            statusText = "本关暂无答案"
            return
        }
        let queue = parseSolution(sol)
        guard !queue.isEmpty else {
            statusText = "本关暂无答案"
            return
        }
        loadLevel(s.levelIndex)
        answerActive = true
        statusText = "执行答案中…（\(queue.count) 步）"
        startAnimQueue(queue)
    }

    private func stopAnswer(finished: Bool) {
        answerActive = false
        clearAnim()
        refreshStatus()
    }

    private func parseSolution(_ solution: String) -> [Direction] {
        solution.compactMap { Direction.from(code: $0) }
    }

    private func startAnimQueue(_ queue: [Direction]) {
        clearAnim()
        animQueue = queue
        inputLocked = true
        animTimer = Timer.scheduledTimer(withTimeInterval: animInterval, repeats: true) { [weak self] _ in
            Task { @MainActor in
                self?.tickAnim()
            }
        }
    }

    private func tickAnim() {
        guard !animQueue.isEmpty else {
            clearAnim()
            if answerActive { stopAnswer(finished: true) }
            return
        }
        let dir = animQueue.removeFirst()
        guard let s = state else { return }
        s.tryMove(dir)
        objectWillChange.send()
        if s.won {
            clearAnim()
            if answerActive { stopAnswer(finished: true) }
            showWin = true
            return
        }
        if animQueue.isEmpty {
            clearAnim()
            if answerActive { stopAnswer(finished: true) }
        }
    }

    private func clearAnim() {
        animTimer?.invalidate()
        animTimer = nil
        animQueue.removeAll()
        inputLocked = false
    }

    // MARK: - UI helpers

    func refreshStatus() {
        guard let s = state else {
            statusText = ""
            return
        }
        if answerActive { return }
        let hasSol = levels.indices.contains(s.levelIndex) && levels[s.levelIndex].hasSolution
        if s.won {
            statusText = "已过关"
        } else if hasSol {
            statusText = "本关有答案"
        } else {
            statusText = "本关暂无答案"
        }
    }

    var movesText: String {
        "\(state?.moves ?? 0)"
    }

    var levelPickerLabels: [String] {
        levels.enumerated().map { i, lv in
            "第\(i + 1)关 - \(lv.name)"
        }
    }

    var canViewAnswer: Bool {
        guard let s = state, !s.won else { return false }
        guard levels.indices.contains(s.levelIndex) else { return false }
        return levels[s.levelIndex].hasSolution
    }
}
