package com.whj.sokoban

/**
 * Tool Window 内容示意。
 *
 * 真实插件中应继承 JPanel / 使用 Kotlin UI DSL，并引用
 * com.intellij.openapi.project.Project 与 JBScrollPane 等。
 * 为避免强制依赖 IDE SDK，此处用纯 Kotlin 描述状态与操作；
 * 对接 IntelliJ 时把 [boardText] 绑到 JTextArea 即可。
 */
class SokobanPanel {
    private var levelIndex = 0
    private var game = GameLogic.fromRows(DEMO_LEVELS[0], 0)

    val title: String
        get() = "推箱子  LV${levelIndex + 1}/${DEMO_LEVELS.size}  步${game.moves}" +
            if (game.won) "  过关" else ""

    val boardText: String
        get() = game.ascii() + "\n" +
            "WASD/方向 移动 | Z 撤销 | R 重置 | N/P 换关\n"

    fun move(dx: Int, dy: Int) {
        game.tryMove(dx, dy)
    }

    fun undo() = game.undo()

    fun reset() {
        game = GameLogic.fromRows(DEMO_LEVELS[levelIndex], levelIndex)
    }

    fun nextLevel() {
        levelIndex = (levelIndex + 1).coerceAtMost(DEMO_LEVELS.lastIndex)
        reset()
    }

    fun prevLevel() {
        levelIndex = (levelIndex - 1).coerceAtLeast(0)
        reset()
    }
}
