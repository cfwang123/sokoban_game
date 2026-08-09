/** 推箱子核心逻辑（Kotlin 教学）。 */
class GameState private constructor(
    val walls: MutableSet<String>,
    val goals: MutableSet<String>,
    val boxes: MutableSet<String>,
    var player: Pair<Int, Int>,
    var moves: Int,
    var won: Boolean,
    val width: Int,
    val height: Int,
    val levelIndex: Int,
    private val hist: MutableList<Hist>,
) {
    private data class Hist(
        val player: Pair<Int, Int>,
        val boxFrom: String? = null,
        val boxTo: String? = null,
    )

    companion object {
        fun fromRows(rows: List<String>, index: Int = 0): GameState {
            val walls = mutableSetOf<String>()
            val goals = mutableSetOf<String>()
            val boxes = mutableSetOf<String>()
            var player = 0 to 0
            var maxX = 0
            var maxY = 0
            for ((y, row) in rows.withIndex()) {
                maxY = y
                for ((x, ch) in row.withIndex()) {
                    if (x > maxX) maxX = x
                    val k = "$x,$y"
                    when (ch) {
                        '#' -> walls.add(k)
                        '.' -> goals.add(k)
                        '$' -> boxes.add(k)
                        '*' -> {
                            boxes.add(k); goals.add(k)
                        }
                        '@' -> player = x to y
                        '+' -> {
                            player = x to y; goals.add(k)
                        }
                    }
                }
            }
            return GameState(walls, goals, boxes, player, 0, false, maxX + 1, maxY + 1, index, mutableListOf())
        }
    }

    fun tryMove(dx: Int, dy: Int): Boolean {
        if (won) return false
        val (px, py) = player
        val nx = px + dx
        val ny = py + dy
        val nk = "$nx,$ny"
        if (nk in walls) return false
        if (nk in boxes) {
            val bx = nx + dx
            val by = ny + dy
            val bk = "$bx,$by"
            if (bk in walls || bk in boxes) return false
            hist.add(Hist(player, nk, bk))
            boxes.remove(nk)
            boxes.add(bk)
            player = nx to ny
            moves++
            checkWin()
            return true
        }
        hist.add(Hist(player))
        player = nx to ny
        return true
    }

    fun undo(): Boolean {
        if (won || hist.isEmpty()) return false
        var entry: Hist? = null
        while (hist.isNotEmpty()) {
            entry = hist.removeAt(hist.lastIndex)
            if (entry.boxFrom != null) break
            player = entry.player
        }
        if (entry?.boxFrom == null) return true
        player = entry.player
        boxes.remove(entry.boxTo!!)
        boxes.add(entry.boxFrom)
        if (moves > 0) moves--
        won = false
        return true
    }

    private fun checkWin() {
        won = boxes.all { it in goals }
    }

    fun renderAscii(): String {
        val sb = StringBuilder()
        for (y in 0 until height) {
            for (x in 0 until width) {
                val k = "$x,$y"
                sb.append(
                    when {
                        player == x to y -> if (k in goals) '+' else '@'
                        k in boxes -> if (k in goals) '*' else '$'
                        k in walls -> '#'
                        k in goals -> '.'
                        else -> ' '
                    }
                )
            }
            sb.append('\n')
        }
        return sb.toString()
    }
}
