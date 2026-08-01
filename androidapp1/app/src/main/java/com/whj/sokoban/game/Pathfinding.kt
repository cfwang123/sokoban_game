package com.whj.sokoban.game

import java.util.ArrayDeque

/**
 * BFS 寻路：从玩家位置到目标格子，避开墙和箱子。
 * 返回方向序列；不可达返回 null；已在目标返回空列表。
 */
object Pathfinding {

    fun findPath(state: GameState, targetX: Int, targetY: Int): List<Direction>? {
        val start = state.player
        if (start.x == targetX && start.y == targetY) return emptyList()

        val blocked = HashSet<String>(state.walls.size + state.boxes.size)
        blocked.addAll(state.walls)
        blocked.addAll(state.boxes)

        val startKey = start.key()
        val targetKey = "$targetX,$targetY"

        val queue = ArrayDeque<Pos>()
        queue.add(start)
        val visited = HashSet<String>()
        visited.add(startKey)
        // key -> (fromKey, direction)
        val parent = HashMap<String, Pair<String, Direction>>()

        while (queue.isNotEmpty()) {
            val cur = queue.removeFirst()
            val curKey = cur.key()

            for (dir in Direction.entries) {
                val nx = cur.x + dir.dx
                val ny = cur.y + dir.dy
                val nKey = "$nx,$ny"
                if (blocked.contains(nKey) || visited.contains(nKey)) continue
                visited.add(nKey)
                parent[nKey] = curKey to dir

                if (nKey == targetKey) {
                    val path = ArrayList<Direction>()
                    var p = nKey
                    while (p != startKey) {
                        val info = parent[p] ?: return null
                        path.add(0, info.second)
                        p = info.first
                    }
                    return path
                }

                queue.add(Pos(nx, ny))
            }
        }
        return null
    }
}
