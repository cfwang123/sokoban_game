// 推箱子核心逻辑（Swift CLI 教学）

struct Hist {
    let px: Int
    let py: Int
    let boxFrom: String?
    let boxTo: String?
}

final class GameState {
    var walls = Set<String>()
    var goals = Set<String>()
    var boxes = Set<String>()
    var px = 0
    var py = 0
    var moves = 0
    var won = false
    var width = 0
    var height = 0
    var hist: [Hist] = []

    static func key(_ x: Int, _ y: Int) -> String { "\(x),\(y)" }

    static func fromRows(_ rows: [String], index: Int = 0) -> GameState {
        let s = GameState()
        var maxX = 0, maxY = 0
        for (y, row) in rows.enumerated() {
            maxY = y
            for (x, ch) in row.enumerated() {
                if x > maxX { maxX = x }
                let k = key(x, y)
                switch ch {
                case "#": s.walls.insert(k)
                case ".": s.goals.insert(k)
                case "$": s.boxes.insert(k)
                case "*":
                    s.boxes.insert(k)
                    s.goals.insert(k)
                case "@":
                    s.px = x; s.py = y
                case "+":
                    s.px = x; s.py = y
                    s.goals.insert(k)
                default: break
                }
            }
        }
        s.width = maxX + 1
        s.height = maxY + 1
        return s
    }

    func checkWin() {
        won = boxes.allSatisfy { goals.contains($0) }
    }

    @discardableResult
    func tryMove(dx: Int, dy: Int) -> Bool {
        if won { return false }
        let nx = px + dx, ny = py + dy
        let nk = GameState.key(nx, ny)
        if walls.contains(nk) { return false }
        if boxes.contains(nk) {
            let bx = nx + dx, by = ny + dy
            let bk = GameState.key(bx, by)
            if walls.contains(bk) || boxes.contains(bk) { return false }
            hist.append(Hist(px: px, py: py, boxFrom: nk, boxTo: bk))
            boxes.remove(nk)
            boxes.insert(bk)
            px = nx; py = ny
            moves += 1
            checkWin()
            return true
        }
        hist.append(Hist(px: px, py: py, boxFrom: nil, boxTo: nil))
        px = nx; py = ny
        return true
    }

    @discardableResult
    func undo() -> Bool {
        if won || hist.isEmpty { return false }
        while !hist.isEmpty {
            let e = hist.removeLast()
            if let bf = e.boxFrom, let bt = e.boxTo {
                px = e.px; py = e.py
                boxes.remove(bt)
                boxes.insert(bf)
                if moves > 0 { moves -= 1 }
                won = false
                return true
            }
            px = e.px; py = e.py
        }
        return true
    }

    func renderAscii() -> String {
        var out = ""
        for y in 0..<height {
            for x in 0..<width {
                let k = GameState.key(x, y)
                if px == x && py == y {
                    out.append(goals.contains(k) ? "+" : "@")
                } else if boxes.contains(k) {
                    out.append(goals.contains(k) ? "*" : "$")
                } else if walls.contains(k) {
                    out.append("#")
                } else if goals.contains(k) {
                    out.append(".")
                } else {
                    out.append(" ")
                }
            }
            out.append("\n")
        }
        return out
    }
}
