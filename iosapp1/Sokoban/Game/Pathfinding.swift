import Foundation

/// BFS 寻路：从玩家走到目标格，避开墙和箱子
enum Pathfinding {
    /// 不可达返回 `nil`；已在目标返回空数组
    static func findPath(state: GameState, targetX: Int, targetY: Int) -> [Direction]? {
        let start = state.player
        if start.x == targetX && start.y == targetY { return [] }

        var blocked = state.walls
        blocked.formUnion(state.boxes)

        let startKey = start.key()
        let targetKey = "\(targetX),\(targetY)"

        var queue: [Pos] = [start]
        var head = 0
        var visited: Set<String> = [startKey]
        // key -> (fromKey, direction)
        var parent: [String: (String, Direction)] = [:]

        while head < queue.count {
            let cur = queue[head]
            head += 1
            let curKey = cur.key()

            for dir in Direction.allCases {
                let nx = cur.x + dir.dx
                let ny = cur.y + dir.dy
                let nKey = "\(nx),\(ny)"
                if blocked.contains(nKey) || visited.contains(nKey) { continue }
                visited.insert(nKey)
                parent[nKey] = (curKey, dir)

                if nKey == targetKey {
                    var path: [Direction] = []
                    var p = nKey
                    while p != startKey {
                        guard let info = parent[p] else { return nil }
                        path.insert(info.1, at: 0)
                        p = info.0
                    }
                    return path
                }
                queue.append(Pos(x: nx, y: ny))
            }
        }
        return nil
    }
}
