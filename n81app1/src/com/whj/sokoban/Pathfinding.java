package com.whj.sokoban;

/**
 * BFS 寻路：从玩家走到目标格，避开墙和箱子。
 * <p>
 * 返回方向序列写入 {@code outDirs}，返回长度；不可达返回 -1。
 * J2ME 无泛型集合，用数组模拟队列。
 */
public final class Pathfinding {
    private Pathfinding() {}

    /**
     * @param outDirs 至少 width*height 长度，填入 Direction 常量
     * @return 路径长度，0 表示已在目标，-1 不可达
     */
    public static int findPath(GameState state, int targetX, int targetY, int[] outDirs) {
        if (state.playerX == targetX && state.playerY == targetY) {
            return 0;
        }
        int w = state.width;
        int h = state.height;
        int n = w * h;
        boolean[] blocked = new boolean[n];
        boolean[] visited = new boolean[n];
        int[] parent = new int[n];
        int[] parentDir = new int[n];
        int[] queue = new int[n];
        int qh = 0;
        int qt = 0;

        for (int i = 0; i < n; i++) {
            blocked[i] = state.walls[i] || state.boxes[i];
            parent[i] = -1;
        }

        int start = state.idx(state.playerX, state.playerY);
        int target = state.idx(targetX, targetY);
        if (targetX < 0 || targetY < 0 || targetX >= w || targetY >= h) {
            return -1;
        }
        if (blocked[target]) {
            return -1;
        }

        queue[qt++] = start;
        visited[start] = true;

        while (qh < qt) {
            int cur = queue[qh++];
            int cx = cur % w;
            int cy = cur / w;
            for (int d = 0; d < 4; d++) {
                int nx = cx + Direction.DX[d];
                int ny = cy + Direction.DY[d];
                if (nx < 0 || ny < 0 || nx >= w || ny >= h) {
                    continue;
                }
                int ni = ny * w + nx;
                if (blocked[ni] || visited[ni]) {
                    continue;
                }
                visited[ni] = true;
                parent[ni] = cur;
                parentDir[ni] = d;
                if (ni == target) {
                    // 回溯
                    int len = 0;
                    int p = ni;
                    int[] rev = new int[n];
                    while (p != start) {
                        rev[len++] = parentDir[p];
                        p = parent[p];
                    }
                    for (int i = 0; i < len; i++) {
                        outDirs[i] = rev[len - 1 - i];
                    }
                    return len;
                }
                queue[qt++] = ni;
            }
        }
        return -1;
    }
}
