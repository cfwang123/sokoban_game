// swiftapp1 — Swift 推箱子终端版（教学）
// 运行: swift main.swift
// 或: swiftc Game.swift main.swift -o sokoban && ./sokoban

let level = [
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
]

var state = GameState.fromRows(level)
print("sokoban_swift — wasd 移动, z 撤销, r 重置, q 退出")

while true {
    print()
    print(state.renderAscii(), terminator: "")
    let flag = state.won ? " WIN!" : ""
    print("moves=\(state.moves)\(flag)")
    print("> ", terminator: "")
    guard let line = readLine() else { break }
    let t = line.trimmingCharacters(in: .whitespacesAndNewlines)
    if t.isEmpty { continue }
    let ch = Character(t.prefix(1).lowercased())
    switch ch {
    case "w": state.tryMove(dx: 0, dy: -1)
    case "s": state.tryMove(dx: 0, dy: 1)
    case "a": state.tryMove(dx: -1, dy: 0)
    case "d": state.tryMove(dx: 1, dy: 0)
    case "z": state.undo()
    case "r": state = GameState.fromRows(level)
    case "q": break
    default: break
    }
    if ch == "q" { break }
    if state.won { print("Level clear!") }
}
