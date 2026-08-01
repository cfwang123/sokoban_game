#include "game.h"
#include "levels_data.h"

#include <string.h>

/* 历史：每步 5 个 int — px,py,boxFrom,boxTo,isPush */
#define HIST_CAP 512
static int s_hist[HIST_CAP];
static int s_hist_n;

static void hist_clear(void) {
    s_hist_n = 0;
}

static void hist_push5(int a, int b, int c, int d, int e) {
    if (s_hist_n + 5 > HIST_CAP) {
        /* 丢弃最旧的 5 槽 */
        memmove(s_hist, s_hist + 5, (size_t)(s_hist_n - 5) * sizeof(int));
        s_hist_n -= 5;
    }
    s_hist[s_hist_n++] = a;
    s_hist[s_hist_n++] = b;
    s_hist[s_hist_n++] = c;
    s_hist[s_hist_n++] = d;
    s_hist[s_hist_n++] = e;
}

int game_idx(const GameState *s, int x, int y) {
    return y * s->width + x;
}

static int in_bounds(const GameState *s, int x, int y) {
    return x >= 0 && y >= 0 && x < s->width && y < s->height;
}

static void check_win(GameState *s) {
    int i, n = s->width * s->height;
    for (i = 0; i < n; i++) {
        if (s->boxes[i] && !s->goals[i]) {
            s->won = 0;
            return;
        }
    }
    s->won = 1;
}

int game_load_level(GameState *s, int level_index) {
    const WqxLevel *lv;
    int y, x, w, h;
    const char *const *rows;

    if (level_index < 0 || level_index >= WQX_LEVEL_COUNT) {
        return -1;
    }
    memset(s, 0, sizeof(*s));
    hist_clear();

    lv = &g_wqx_levels[level_index];
    rows = lv->rows;
    h = 0;
    w = 0;
    while (rows[h]) {
        int len = (int)strlen(rows[h]);
        if (len > w) {
            w = len;
        }
        h++;
    }
    if (w > GAME_MAX_W) {
        w = GAME_MAX_W;
    }
    if (h > GAME_MAX_H) {
        h = GAME_MAX_H;
    }
    s->width = w;
    s->height = h;
    s->level_index = level_index;
    s->player_x = 0;
    s->player_y = 0;

    for (y = 0; y < h; y++) {
        const char *row = rows[y];
        int len = (int)strlen(row);
        for (x = 0; x < len && x < w; x++) {
            int i = game_idx(s, x, y);
            switch (row[x]) {
            case '#':
                s->walls[i] = 1;
                break;
            case '.':
                s->goals[i] = 1;
                break;
            case '$':
                s->boxes[i] = 1;
                break;
            case '*':
                s->boxes[i] = 1;
                s->goals[i] = 1;
                break;
            case '@':
                s->player_x = x;
                s->player_y = y;
                break;
            case '+':
                s->player_x = x;
                s->player_y = y;
                s->goals[i] = 1;
                break;
            default:
                break;
            }
        }
    }
    return 0;
}

int game_try_move(GameState *s, int dx, int dy) {
    int nx, ny, ni, bx, by, bi;

    if (s->won) {
        return 0;
    }
    nx = s->player_x + dx;
    ny = s->player_y + dy;
    if (!in_bounds(s, nx, ny) || s->walls[game_idx(s, nx, ny)]) {
        return 0;
    }
    ni = game_idx(s, nx, ny);
    if (s->boxes[ni]) {
        bx = nx + dx;
        by = ny + dy;
        if (!in_bounds(s, bx, by) || s->walls[game_idx(s, bx, by)] ||
            s->boxes[game_idx(s, bx, by)]) {
            return 0;
        }
        bi = game_idx(s, bx, by);
        hist_push5(s->player_x, s->player_y, ni, bi, 1);
        s->boxes[ni] = 0;
        s->boxes[bi] = 1;
        s->player_x = nx;
        s->player_y = ny;
        s->moves++;
        check_win(s);
        return 1;
    }
    hist_push5(s->player_x, s->player_y, -1, -1, 0);
    s->player_x = nx;
    s->player_y = ny;
    return 1;
}

int game_try_move_dir(GameState *s, int dir) {
    static const int DX[4] = {0, 0, -1, 1};
    static const int DY[4] = {-1, 1, 0, 0};
    if (dir < 0 || dir > 3) {
        return 0;
    }
    return game_try_move(s, DX[dir], DY[dir]);
}

int game_undo(GameState *s) {
    int is_push = 0, from = -1, to = -1, px, py;

    if (s->won || s_hist_n < 5) {
        return 0;
    }
    px = s->player_x;
    py = s->player_y;
    while (s_hist_n >= 5) {
        is_push = s_hist[--s_hist_n];
        to = s_hist[--s_hist_n];
        from = s_hist[--s_hist_n];
        py = s_hist[--s_hist_n];
        px = s_hist[--s_hist_n];
        if (is_push) {
            break;
        }
        s->player_x = px;
        s->player_y = py;
    }
    if (!is_push || from < 0 || to < 0) {
        return 1;
    }
    s->player_x = px;
    s->player_y = py;
    s->boxes[to] = 0;
    s->boxes[from] = 1;
    if (s->moves > 0) {
        s->moves--;
    }
    s->won = 0;
    return 1;
}
