package com.whj.sokoban

/**
 * 无 IDE SDK 时的控制台宿主：验证 [GameLogic] / [SokobanPanel]。
 * Gradle: `./gradlew runConsole`（需本机 JDK）
 */
fun main() {
    val panel = SokobanPanel()
    println("jetbrainsext1 console — wasd z r n p q")
    val input = System.`in`.bufferedReader()
    while (true) {
        println()
        println(panel.title)
        print(panel.boardText)
        print("> ")
        val line = input.readLine() ?: break
        when (line.firstOrNull()?.lowercaseChar()) {
            'w' -> panel.move(0, -1)
            's' -> panel.move(0, 1)
            'a' -> panel.move(-1, 0)
            'd' -> panel.move(1, 0)
            'z' -> panel.undo()
            'r' -> panel.reset()
            'n' -> panel.nextLevel()
            'p' -> panel.prevLevel()
            'q' -> return
            else -> {}
        }
    }
}
