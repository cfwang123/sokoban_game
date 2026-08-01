package com.whj.sokoban

/** 推箱子逻辑（与 html_app 对齐），供 Tool Window / 控制台共用。 */
class GameLogic private constructor(
    val walls: MutableSet<String>,
    val goals: MutableSet<String>,
    val boxes: MutableSet<String>,
    var playerX: Int,
    var playerY: Int,
    var width: Int,
    var height: Int,
    var levelIndex: Int,
) {
    var moves: Int = 0
        private set
    var won: Boolean = false
        private set

    private data class Hist(val px: Int, val py: Int, val from: String?, val to: String?, val push: Boolean)
    private val hist = ArrayList<Hist>()

    fun tryMove(dx: Int, dy: Int): Boolean {
        if (won) return false
        val nx = playerX + dx
        val ny = playerY + dy
        val nk = "$nx,$ny"
        if (walls.contains(nk)) return false
        if (boxes.contains(nk)) {
            val bk = "${nx + dx},${ny + dy}"
            if (walls.contains(bk) || boxes.contains(bk)) return false
            hist.add(Hist(playerX, playerY, nk, bk, true))
            boxes.remove(nk)
            boxes.add(bk)
            playerX = nx
            playerY = ny
            moves++
            won = boxes.all { goals.contains(it) }
            return true
        }
        hist.add(Hist(playerX, playerY, null, null, false))
        playerX = nx
        playerY = ny
        return true
    }

    fun undo() {
        if (won || hist.isEmpty()) return
        var e: Hist? = null
        while (hist.isNotEmpty()) {
            e = hist.removeAt(hist.lastIndex)
            if (e.push) break
            playerX = e.px
            playerY = e.py
        }
        val h = e ?: return
        if (!h.push) return
        playerX = h.px
        playerY = h.py
        boxes.remove(h.to!!)
        boxes.add(h.from!!)
        if (moves > 0) moves--
        won = false
    }

    fun ascii(): String {
        val sb = StringBuilder()
        for (y in 0 until height) {
            for (x in 0 until width) {
                val k = "$x,$y"
                sb.append(
                    when {
                        playerX == x && playerY == y -> if (goals.contains(k)) '+' else '@'
                        boxes.contains(k) -> if (goals.contains(k)) '*' else '$'
                        walls.contains(k) -> '#'
                        goals.contains(k) -> '.'
                        else -> ' '
                    },
                )
            }
            sb.append('\n')
        }
        return sb.toString()
    }

    companion object {
        fun fromRows(rows: List<String>, index: Int): GameLogic {
            val walls = mutableSetOf<String>()
            val goals = mutableSetOf<String>()
            val boxes = mutableSetOf<String>()
            var px = 0
            var py = 0
            var maxX = 0
            var maxY = 0
            for (y in rows.indices) {
                maxY = y
                val row = rows[y]
                for (x in row.indices) {
                    if (x > maxX) maxX = x
                    val k = "$x,$y"
                    when (row[x]) {
                        '#' -> walls.add(k)
                        '.' -> goals.add(k)
                        '$' -> boxes.add(k)
                        '*' -> {
                            boxes.add(k)
                            goals.add(k)
                        }
                        '@' -> {
                            px = x
                            py = y
                        }
                        '+' -> {
                            px = x
                            py = y
                            goals.add(k)
                        }
                    }
                }
            }
            return GameLogic(walls, goals, boxes, px, py, maxX + 1, maxY + 1, index)
        }
    }
}

val DEMO_LEVELS: List<List<String>> = listOf(
    listOf("###", "#@#", "#$#", "#.#", "###"),
    listOf("#####", "#.$@#", "#####"),
    listOf("###", "#.###", "#*$-#", "#--@#", "#####"),
)
