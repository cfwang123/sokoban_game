/* pathfinding.c — BFS 寻路（移植自 pathfinding.js） */
#include "pathfinding.h"

#include <stdlib.h>
#include <string.h>

typedef struct {
    int x, y;
} Point;

typedef struct {
    int from;     /* 父节点在 visited 数组中的索引 */
    char dir;     /* 'U'/'D'/'L'/'R' */
} Parent;

char *path_find(const GameState *s, int targetX, int targetY, int *outLen) {
    *outLen = 0;
    int sx = s->player.x, sy = s->player.y;
    if (sx == targetX && sy == targetY) {
        /* 已在目标点：返回空数组（非 NULL） */
        char *p = (char *)malloc(1);
        if (p) p[0] = '\0';
        return p;
    }
    if (targetX < 0 || targetY < 0 || targetX >= s->w || targetY >= s->h) return NULL;
    if (s->cells[targetY * s->w + targetX] == '#') return NULL;
    if (game_is_box_at(s, targetX, targetY)) return NULL;

    int total = s->w * s->h;
    /* visited 用整数索引：-1=未访问，>=0=父节点在 visited 中的索引 */
    int *visited = (int *)malloc(sizeof(int) * total);
    Parent *parent = (Parent *)malloc(sizeof(Parent) * total);
    Point *queue = (Point *)malloc(sizeof(Point) * total);
    if (!visited || !parent || !queue) {
        free(visited); free(parent); free(queue);
        return NULL;
    }
    for (int i = 0; i < total; i++) visited[i] = -1;

    int startIdx = sy * s->w + sx;
    visited[startIdx] = -2;  /* 起点标记：父为根 */
    parent[startIdx].from = -1;
    parent[startIdx].dir = 0;

    int head = 0, tail = 0;
    queue[tail].x = sx; queue[tail].y = sy; tail++;

    const int dxs[4] = {0, 0, -1, 1};
    const int dys[4] = {-1, 1, 0, 0};
    const char dirs[4] = {'U', 'D', 'L', 'R'};

    int found = 0;
    while (head < tail) {
        Point cur = queue[head++];
        if (cur.x == targetX && cur.y == targetY) {
            found = 1;
            break;
        }
        for (int k = 0; k < 4; k++) {
            int nx = cur.x + dxs[k];
            int ny = cur.y + dys[k];
            if (nx < 0 || ny < 0 || nx >= s->w || ny >= s->h) continue;
            int nIdx = ny * s->w + nx;
            if (visited[nIdx] != -1) continue;
            if (s->cells[nIdx] == '#') continue;
            if (game_is_box_at(s, nx, ny)) continue;
            visited[nIdx] = cur.y * s->w + cur.x;
            parent[nIdx].from = visited[nIdx];
            parent[nIdx].dir = dirs[k];
            queue[tail].x = nx; queue[tail].y = ny; tail++;
        }
    }

    char *result = NULL;
    if (found) {
        /* 回溯路径 */
        /* 先数长度 */
        int len = 0;
        int idx = targetY * s->w + targetX;
        while (idx != startIdx) {
            len++;
            idx = parent[idx].from;
        }
        result = (char *)malloc((size_t)len + 1);
        if (result) {
            result[len] = '\0';
            idx = targetY * s->w + targetX;
            int p = len - 1;
            while (idx != startIdx) {
                result[p--] = parent[idx].dir;
                idx = parent[idx].from;
            }
            *outLen = len;
        }
    }

    free(visited);
    free(parent);
    free(queue);
    return result;
}
