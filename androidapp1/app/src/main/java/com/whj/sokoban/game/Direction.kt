package com.whj.sokoban.game

enum class Direction(val dx: Int, val dy: Int, val code: Char) {
    UP(0, -1, 'U'),
    DOWN(0, 1, 'D'),
    LEFT(-1, 0, 'L'),
    RIGHT(1, 0, 'R');

    companion object {
        fun fromCode(ch: Char): Direction? = when (ch.uppercaseChar()) {
            'U' -> UP
            'D' -> DOWN
            'L' -> LEFT
            'R' -> RIGHT
            else -> null
        }

        fun fromDelta(dx: Int, dy: Int): Direction? = entries.find { it.dx == dx && it.dy == dy }
    }
}
