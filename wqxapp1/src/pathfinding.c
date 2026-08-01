#include "pathfinding.h"

int path_find(const GameState *s, int tx, int ty, int *out_dirs, int out_cap) {
    int w = s->width;
    int h = s->height;
    int n = w * h;
    int start, target, qh, qt, i;
    unsigned char blocked[GAME_MAX_CELLS];
    unsigned char visited[GAME_MAX_CELLS];
    int parent[GAME_MAX_CELLS];
    int parent_dir[GAME_MAX_CELLS];
    int queue[GAME_MAX_CELLS];
    static const int DX[4] = {0, 0, -1, 1};
    static const int DY[4] = {-1, 1, 0, 0};

    if (s->player_x == tx && s->player_y == ty) {
        return 0;
    }
    if (tx < 0 || ty < 0 || tx >= w || ty >= h) {
        return -1;
    }
    for (i = 0; i < n; i++) {
        blocked[i] = (unsigned char)(s->walls[i] || s->boxes[i]);
        visited[i] = 0;
        parent[i] = -1;
    }
    target = ty * w + tx;
    if (blocked[target]) {
        return -1;
    }
    start = s->player_y * w + s->player_x;
    qh = 0;
    qt = 0;
    queue[qt++] = start;
    visited[start] = 1;

    while (qh < qt) {
        int cur = queue[qh++];
        int cx = cur % w;
        int cy = cur / w;
        int d;
        for (d = 0; d < 4; d++) {
            int nx = cx + DX[d];
            int ny = cy + DY[d];
            int ni;
            if (nx < 0 || ny < 0 || nx >= w || ny >= h) {
                continue;
            }
            ni = ny * w + nx;
            if (blocked[ni] || visited[ni]) {
                continue;
            }
            visited[ni] = 1;
            parent[ni] = cur;
            parent_dir[ni] = d;
            if (ni == target) {
                int len = 0;
                int rev[GAME_MAX_CELLS];
                int p = ni;
                while (p != start) {
                    rev[len++] = parent_dir[p];
                    p = parent[p];
                }
                if (len > out_cap) {
                    len = out_cap;
                }
                for (i = 0; i < len; i++) {
                    out_dirs[i] = rev[len - 1 - i];
                }
                return len;
            }
            queue[qt++] = ni;
        }
    }
    return -1;
}
