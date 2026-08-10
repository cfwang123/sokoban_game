#include "game.h"
#include <string.h>

static void check_win(GameState *s)
{
    int x, y;
    s->won = 1;
    for (y = 0; y < s->height; y++)
        for (x = 0; x < s->width; x++)
            if (s->map[x][y] == '$')
                s->won = 0;
}

void game_from_rows(GameState *s, const char **rows, int n)
{
    int y, x, len;
    char ch;
    memset(s, 0, sizeof(*s));
    s->height = n;
    for (y = 0; y < n; y++) {
        len = (int)strlen(rows[y]);
        if (len > s->width) s->width = len;
        for (x = 0; x < len; x++) {
            ch = rows[y][x];
            switch (ch) {
            case '#': s->map[x][y] = '#'; break;
            case '.': s->map[x][y] = '.'; break;
            case '$': s->map[x][y] = '$'; break;
            case '*': s->map[x][y] = '*'; break;
            case '@': s->map[x][y] = ' '; s->px = x; s->py = y; break;
            case '+': s->map[x][y] = '.'; s->px = x; s->py = y; break;
            default:  s->map[x][y] = ' '; break;
            }
        }
    }
}

int game_try_move(GameState *s, int dx, int dy)
{
    int nx, ny, bx, by;
    char ch;
    if (s->won) return 0;
    nx = s->px + dx;
    ny = s->py + dy;
    if (nx < 0 || ny < 0 || nx >= s->width || ny >= s->height) return 0;
    ch = s->map[nx][ny];
    if (ch == '#') return 0;
    if (ch == '$' || ch == '*') {
        bx = nx + dx;
        by = ny + dy;
        if (bx < 0 || by < 0 || bx >= s->width || by >= s->height) return 0;
        ch = s->map[bx][by];
        if (ch == '#' || ch == '$' || ch == '*') return 0;
        if (s->hist_n >= MAX_HIST) return 0;
        s->hist[s->hist_n++] = (Hist){ s->px, s->py, nx, ny, bx, by, 1 };
        s->map[nx][ny] = (s->map[nx][ny] == '*') ? '.' : ' ';
        s->map[bx][by] = (s->map[bx][by] == '.') ? '*' : '$';
        s->px = nx;
        s->py = ny;
        s->moves++;
        check_win(s);
        return 1;
    }
    if (s->hist_n >= MAX_HIST) return 0;
    s->hist[s->hist_n++] = (Hist){ s->px, s->py, 0, 0, 0, 0, 0 };
    s->px = nx;
    s->py = ny;
    return 1;
}

int game_undo(GameState *s)
{
    Hist h;
    if (s->won || s->hist_n == 0) return 0;
    while (s->hist_n > 0) {
        h = s->hist[--s->hist_n];
        if (h.is_push) {
            s->px = h.px;
            s->py = h.py;
            s->map[h.btx][h.bty] = (s->map[h.btx][h.bty] == '*') ? '.' : ' ';
            s->map[h.bfx][h.bfy] = (s->map[h.bfx][h.bfy] == '.') ? '*' : '$';
            if (s->moves > 0) s->moves--;
            s->won = 0;
            return 1;
        }
        s->px = h.px;
        s->py = h.py;
    }
    return 1;
}
