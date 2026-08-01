import Foundation

struct Pos: Hashable, Equatable {
    var x: Int
    var y: Int

    func key() -> String { "\(x),\(y)" }

    func offset(dx: Int, dy: Int) -> Pos { Pos(x: x + dx, y: y + dy) }
    func offset(_ dir: Direction) -> Pos { offset(dx: dir.dx, dy: dir.dy) }
}

struct HistoryEntry {
    let player: Pos
    let boxFrom: Pos?
    let boxTo: Pos?
}

/// 推箱子运行时状态（对齐 html_app / androidapp1）
final class GameState {
    let walls: Set<String>
    let goals: Set<String>
    private(set) var boxes: Set<String>
    private(set) var player: Pos
    let levelIndex: Int
    let width: Int
    let height: Int
    private(set) var moves: Int = 0
    private(set) var won: Bool = false
    private var history: [HistoryEntry] = []

    private init(
        walls: Set<String>,
        goals: Set<String>,
        boxes: Set<String>,
        player: Pos,
        levelIndex: Int,
        width: Int,
        height: Int
    ) {
        self.walls = walls
        self.goals = goals
        self.boxes = boxes
        self.player = player
        self.levelIndex = levelIndex
        self.width = width
        self.height = height
    }

    func isWall(_ p: Pos) -> Bool { walls.contains(p.key()) }
    func isBox(_ p: Pos) -> Bool { boxes.contains(p.key()) }
    func isGoal(_ p: Pos) -> Bool { goals.contains(p.key()) }
    func isWall(x: Int, y: Int) -> Bool { walls.contains("\(x),\(y)") }
    func isBox(x: Int, y: Int) -> Bool { boxes.contains("\(x),\(y)") }
    func isGoal(x: Int, y: Int) -> Bool { goals.contains("\(x),\(y)") }

    @discardableResult
    func tryMove(dx: Int, dy: Int) -> Bool {
        if won { return false }
        let next = player.offset(dx: dx, dy: dy)
        if isWall(next) { return false }

        if isBox(next) {
            let boxNext = next.offset(dx: dx, dy: dy)
            if isWall(boxNext) || isBox(boxNext) { return false }
            history.append(HistoryEntry(player: player, boxFrom: next, boxTo: boxNext))
            boxes.remove(next.key())
            boxes.insert(boxNext.key())
            player = next
            moves += 1
            checkWin()
            return true
        }

        history.append(HistoryEntry(player: player, boxFrom: nil, boxTo: nil))
        player = next
        // 纯移动不计步数
        return true
    }

    @discardableResult
    func tryMove(_ dir: Direction) -> Bool {
        tryMove(dx: dir.dx, dy: dir.dy)
    }

    /// 撤销：跳过纯移动，只撤销最近一次推箱
    @discardableResult
    func undo() -> Bool {
        if won || history.isEmpty { return false }

        var entry: HistoryEntry?
        while !history.isEmpty {
            entry = history.removeLast()
            if entry?.boxFrom != nil, entry?.boxTo != nil { break }
            if let e = entry {
                player = e.player
            }
        }

        guard let e = entry, let from = e.boxFrom, let to = e.boxTo else {
            return true
        }
        player = e.player
        boxes.remove(to.key())
        boxes.insert(from.key())
        moves = max(0, moves - 1)
        won = false
        return true
    }

    private func checkWin() {
        for b in boxes {
            if !goals.contains(b) {
                won = false
                return
            }
        }
        won = true
    }

    static func from(level: LevelData, levelIndex: Int) -> GameState {
        var walls = Set<String>()
        var goals = Set<String>()
        var boxes = Set<String>()
        var player = Pos(x: 0, y: 0)
        var maxX = 0
        var maxY = 0

        for (y, row) in level.puzzle.enumerated() {
            maxY = max(maxY, y)
            for (x, ch) in row.enumerated() {
                maxX = max(maxX, x)
                let key = "\(x),\(y)"
                switch ch {
                case "#": walls.insert(key)
                case ".": goals.insert(key)
                case "$": boxes.insert(key)
                case "*":
                    boxes.insert(key)
                    goals.insert(key)
                case "@": player = Pos(x: x, y: y)
                case "+":
                    player = Pos(x: x, y: y)
                    goals.insert(key)
                default:
                    break
                }
            }
        }

        return GameState(
            walls: walls,
            goals: goals,
            boxes: boxes,
            player: player,
            levelIndex: levelIndex,
            width: maxX + 1,
            height: maxY + 1
        )
    }
}
