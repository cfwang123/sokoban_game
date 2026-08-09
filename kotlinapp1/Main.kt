/** kotlinapp1 — 推箱子终端版（教学）。 */

fun main() {
    val level = listOf(
        "#######",
        "#. . .#",
        "# $$$ #",
        "#.$@$.#",
        "# $$$ #",
        "#. . .#",
        "#######",
    )
    var state = GameState.fromRows(level, 0)
    println("sokoban_kotlin — wasd 移动, z 撤销, r 重置, q 退出")
    while (true) {
        println()
        print(state.renderAscii())
        print("moves=${state.moves}${if (state.won) " WIN!" else ""}\n> ")
        val line = readLine()?.trim() ?: break
        if (line.isEmpty()) continue
        when (line[0].lowercaseChar()) {
            'w' -> state.tryMove(0, -1)
            's' -> state.tryMove(0, 1)
            'a' -> state.tryMove(-1, 0)
            'd' -> state.tryMove(1, 0)
            'z' -> state.undo()
            'r' -> state = GameState.fromRows(level, 0)
            'q' -> break
        }
        if (state.won) println("Level clear!")
    }
}
