package com.whj.sokoban.game

data class Pos(val x: Int, val y: Int) {
    fun key(): String = "$x,$y"
    fun offset(dx: Int, dy: Int) = Pos(x + dx, y + dy)
    fun offset(dir: Direction) = offset(dir.dx, dir.dy)
}

data class HistoryEntry(
    val player: Pos,
    /** 推箱时记录 from/to；纯移动为 null */
    val boxFrom: Pos? = null,
    val boxTo: Pos? = null,
)

/**
 * 推箱子运行时状态（对应 html_app 的 state）
 */
class GameState private constructor(
    val walls: Set<String>,
    val goals: Set<String>,
    boxes: MutableSet<String>,
    player: Pos,
    val levelIndex: Int,
    val width: Int,
    val height: Int,
) {
    var player: Pos = player
        private set

    private val _boxes: MutableSet<String> = boxes
    val boxes: Set<String> get() = _boxes

    var moves: Int = 0
        private set

    var won: Boolean = false
        private set

    private val history = ArrayList<HistoryEntry>()

    fun isWall(x: Int, y: Int) = walls.contains("$x,$y")
    fun isWall(p: Pos) = walls.contains(p.key())
    fun isBox(x: Int, y: Int) = _boxes.contains("$x,$y")
    fun isBox(p: Pos) = _boxes.contains(p.key())
    fun isGoal(x: Int, y: Int) = goals.contains("$x,$y")
    fun isGoal(p: Pos) = goals.contains(p.key())

    /**
     * 尝试向 (dx,dy) 移动一步。
     * @return 是否成功移动
     */
    fun tryMove(dx: Int, dy: Int): Boolean {
        if (won) return false
        val next = player.offset(dx, dy)
        if (isWall(next)) return false

        if (isBox(next)) {
            val boxNext = next.offset(dx, dy)
            if (isWall(boxNext) || isBox(boxNext)) return false

            history.add(HistoryEntry(player = player, boxFrom = next, boxTo = boxNext))
            _boxes.remove(next.key())
            _boxes.add(boxNext.key())
            player = next
            moves++
            checkWin()
            return true
        }

        history.add(HistoryEntry(player = player, boxFrom = null, boxTo = null))
        player = next
        // 纯移动不计步数（与 html_app 一致）
        return true
    }

    fun tryMove(dir: Direction): Boolean = tryMove(dir.dx, dir.dy)

    /**
     * 撤销：跳过纯移动，只撤销最近一次推箱子（与 html_app 一致）
     */
    fun undo(): Boolean {
        if (won || history.isEmpty()) return false

        var entry: HistoryEntry? = null
        while (history.isNotEmpty()) {
            entry = history.removeAt(history.lastIndex)
            if (entry.boxFrom != null && entry.boxTo != null) break
            // 纯移动：恢复玩家位置
            player = entry.player
        }

        val e = entry
        if (e == null || e.boxFrom == null || e.boxTo == null) {
            return true
        }

        player = e.player
        _boxes.remove(e.boxTo.key())
        _boxes.add(e.boxFrom.key())
        moves = (moves - 1).coerceAtLeast(0)
        won = false
        return true
    }

    private fun checkWin() {
        for (b in _boxes) {
            if (!goals.contains(b)) {
                won = false
                return
            }
        }
        won = true
    }

    companion object {
        fun fromLevel(level: LevelData, levelIndex: Int): GameState {
            val walls = HashSet<String>()
            val goals = HashSet<String>()
            val boxes = HashSet<String>()
            var player: Pos? = null
            var maxX = 0
            var maxY = 0

            for (y in level.puzzle.indices) {
                val row = level.puzzle[y]
                maxY = maxOf(maxY, y)
                for (x in row.indices) {
                    maxX = maxOf(maxX, x)
                    val ch = row[x]
                    val key = "$x,$y"
                    when (ch) {
                        '#' -> walls.add(key)
                        '.' -> goals.add(key)
                        '$' -> boxes.add(key)
                        '*' -> {
                            boxes.add(key)
                            goals.add(key)
                        }
                        '@' -> player = Pos(x, y)
                        '+' -> {
                            player = Pos(x, y)
                            goals.add(key)
                        }
                        // '-', ' ', 等为空地
                    }
                }
            }

            val p = player ?: Pos(0, 0)
            return GameState(
                walls = walls,
                goals = goals,
                boxes = boxes,
                player = p,
                levelIndex = levelIndex,
                width = maxX + 1,
                height = maxY + 1,
            )
        }
    }
}
