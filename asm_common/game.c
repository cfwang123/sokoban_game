/* 汇编教学共用玩法（C 参考实现；各 ISA 的 .s 对照阅读 / 可选替换 try_move） */
#include "game.h"
#include <string.h>

static const char *LEVEL[] = {
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
};

static char at(const SkGame *g, int x, int y)
{
    if (x < 0 || y < 0 || x >= g->width || y >= g->height)
        return '#';
    return g->map[y * SK_MAX_W + x];
}

static void setc(SkGame *g, int x, int y, char c)
{
    g->map[y * SK_MAX_W + x] = c;
}

static void check_win(SkGame *g)
{
    int x, y;
    g->won = 1;
    for (y = 0; y < g->height; y++)
        for (x = 0; x < g->width; x++)
            if (at(g, x, y) == '$')
                g->won = 0;
}

void sk_reset(SkGame *g)
{
    int y, x, len;
    memset(g, 0, sizeof(*g));
    g->height = 7;
    for (y = 0; y < 7; y++) {
        len = (int)strlen(LEVEL[y]);
        if (len > g->width)
            g->width = len;
        for (x = 0; x < len; x++) {
            char ch = LEVEL[y][x];
            switch (ch) {
            case '#':
            case '.':
            case '$':
            case '*':
            case ' ':
                setc(g, x, y, ch);
                break;
            case '@':
                setc(g, x, y, ' ');
                g->px = x;
                g->py = y;
                break;
            case '+':
                setc(g, x, y, '.');
                g->px = x;
                g->py = y;
                break;
            default:
                setc(g, x, y, ' ');
                break;
            }
        }
    }
}

#ifndef SK_USE_ASM_TRY_MOVE
int sk_try_move(SkGame *g, int dx, int dy)
{
    int nx, ny, bx, by;
    char ch;
    if (g->won)
        return 0;
    nx = g->px + dx;
    ny = g->py + dy;
    ch = at(g, nx, ny);
    if (ch == '#')
        return 0;
    if (ch == '$' || ch == '*') {
        bx = nx + dx;
        by = ny + dy;
        ch = at(g, bx, by);
        if (ch == '#' || ch == '$' || ch == '*')
            return 0;
        if (g->hist_n >= SK_MAX_HIST)
            return 0;
        g->hist[g->hist_n].px = g->px;
        g->hist[g->hist_n].py = g->py;
        g->hist[g->hist_n].bfx = nx;
        g->hist[g->hist_n].bfy = ny;
        g->hist[g->hist_n].btx = bx;
        g->hist[g->hist_n].bty = by;
        g->hist[g->hist_n].is_push = 1;
        g->hist_n++;
        setc(g, nx, ny, at(g, nx, ny) == '*' ? '.' : ' ');
        setc(g, bx, by, at(g, bx, by) == '.' ? '*' : '$');
        g->px = nx;
        g->py = ny;
        g->moves++;
        check_win(g);
        return 1;
    }
    if (g->hist_n >= SK_MAX_HIST)
        return 0;
    g->hist[g->hist_n].px = g->px;
    g->hist[g->hist_n].py = g->py;
    g->hist[g->hist_n].is_push = 0;
    g->hist_n++;
    g->px = nx;
    g->py = ny;
    return 1;
}
#endif /* !SK_USE_ASM_TRY_MOVE */

int sk_undo(SkGame *g)
{
    SkHist h;
    if (g->won || g->hist_n == 0)
        return 0;
    while (g->hist_n > 0) {
        h = g->hist[--g->hist_n];
        if (h.is_push) {
            g->px = h.px;
            g->py = h.py;
            setc(g, h.btx, h.bty, at(g, h.btx, h.bty) == '*' ? '.' : ' ');
            setc(g, h.bfx, h.bfy, at(g, h.bfx, h.bfy) == '.' ? '*' : '$');
            if (g->moves > 0)
                g->moves--;
            g->won = 0;
            return 1;
        }
        g->px = h.px;
        g->py = h.py;
    }
    return 1;
}

int sk_cell(const SkGame *g, int x, int y)
{
    char ch = at(g, x, y);
    if (x == g->px && y == g->py)
        return ch == '.' ? '+' : '@';
    return (unsigned char)ch;
}

void sk_render(const SkGame *g, char *buf, int cap)
{
    int x, y, n = 0;
    for (y = 0; y < g->height && n + 2 < cap; y++) {
        for (x = 0; x < g->width && n + 2 < cap; x++)
            buf[n++] = (char)sk_cell(g, x, y);
        buf[n++] = '\n';
    }
    buf[n] = 0;
}
