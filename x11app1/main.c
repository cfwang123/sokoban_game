/**
 * x11app1 — X11 / Xlib 推箱子（教学演示源码）
 * 不要求在本仓库内编译。Linux 可选：
 *   gcc -O2 main.c game.c -o sokoban -lX11
 *
 * 键位：WASD / 方向键，Z 撤销，R 重置，Q/Esc 退出
 */
#include <X11/Xlib.h>
#include <X11/keysym.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "game.h"

#define CELL 40
#define PAD  16

static GameState g;
static const char *LEVEL[] = {
    "#######", "#. . .#", "# $$$ #", "#.$@$.#",
    "# $$$ #", "#. . .#", "#######",
};

static void load(void) { game_from_rows(&g, LEVEL, 7); }

static void draw(Display *dpy, Window win, GC gc, Colormap cmap)
{
    int x, y;
    XColor wall, floor, box, boxok, player, goal, bg, white;
    char status[80];
    int ww = PAD * 2 + g.width * CELL;
    int wh = PAD * 2 + g.height * CELL + 28;

    XParseColor(dpy, cmap, "#1a1a2e", &bg);
    XAllocColor(dpy, cmap, &bg);
    XSetForeground(dpy, gc, bg.pixel);
    XFillRectangle(dpy, win, gc, 0, 0, ww, wh);

    XParseColor(dpy, cmap, "#4a4a6a", &wall); XAllocColor(dpy, cmap, &wall);
    XParseColor(dpy, cmap, "#3a3a55", &floor); XAllocColor(dpy, cmap, &floor);
    XParseColor(dpy, cmap, "#f39c12", &box); XAllocColor(dpy, cmap, &box);
    XParseColor(dpy, cmap, "#2ecc71", &boxok); XAllocColor(dpy, cmap, &boxok);
    XParseColor(dpy, cmap, "#3498db", &player); XAllocColor(dpy, cmap, &player);
    XParseColor(dpy, cmap, "#e94560", &goal); XAllocColor(dpy, cmap, &goal);
    XParseColor(dpy, cmap, "#ffffff", &white); XAllocColor(dpy, cmap, &white);

    for (y = 0; y < g.height; y++) {
        for (x = 0; x < g.width; x++) {
            int rx = PAD + x * CELL, ry = PAD + y * CELL;
            char ch = g.map[x][y];
            if (ch == '#') {
                XSetForeground(dpy, gc, wall.pixel);
                XFillRectangle(dpy, win, gc, rx, ry, CELL, CELL);
            } else {
                XSetForeground(dpy, gc, floor.pixel);
                XFillRectangle(dpy, win, gc, rx, ry, CELL, CELL);
                if (ch == '.' || ch == '*') {
                    XSetForeground(dpy, gc, goal.pixel);
                    XFillArc(dpy, win, gc, rx + CELL / 2 - 6, ry + CELL / 2 - 6, 12, 12, 0, 360 * 64);
                }
                if (ch == '$' || ch == '*') {
                    XSetForeground(dpy, gc, ch == '*' ? boxok.pixel : box.pixel);
                    XFillRectangle(dpy, win, gc, rx + 4, ry + 4, CELL - 8, CELL - 8);
                }
            }
            if (x == g.px && y == g.py) {
                XSetForeground(dpy, gc, player.pixel);
                XFillArc(dpy, win, gc, rx + 6, ry + 6, CELL - 12, CELL - 12, 0, 360 * 64);
            }
        }
    }
    snprintf(status, sizeof(status), "moves=%d%s  WASD Z R Q", g.moves, g.won ? " WIN" : "");
    XSetForeground(dpy, gc, white.pixel);
    XDrawString(dpy, win, gc, 8, PAD + g.height * CELL + 16, status, (int)strlen(status));
}

int main(void)
{
    Display *dpy;
    Window win;
    XEvent ev;
    GC gc;
    Colormap cmap;
    int screen;
    Atom wm_delete;

    dpy = XOpenDisplay(NULL);
    if (!dpy) {
        fprintf(stderr, "x11app1: cannot open display (need X11)\n");
        return 1;
    }
    load();
    screen = DefaultScreen(dpy);
    cmap = DefaultColormap(dpy, screen);
    win = XCreateSimpleWindow(dpy, RootWindow(dpy, screen),
                              100, 100,
                              PAD * 2 + g.width * CELL,
                              PAD * 2 + g.height * CELL + 28,
                              1, BlackPixel(dpy, screen), WhitePixel(dpy, screen));
    XStoreName(dpy, win, "Sokoban X11 (teaching)");
    XSelectInput(dpy, win, ExposureMask | KeyPressMask | StructureNotifyMask);
    wm_delete = XInternAtom(dpy, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(dpy, win, &wm_delete, 1);
    gc = XCreateGC(dpy, win, 0, NULL);
    XMapWindow(dpy, win);

    for (;;) {
        XNextEvent(dpy, &ev);
        if (ev.type == Expose && ev.xexpose.count == 0)
            draw(dpy, win, gc, cmap);
        else if (ev.type == ClientMessage)
            break;
        else if (ev.type == KeyPress) {
            KeySym ks = XLookupKeysym(&ev.xkey, 0);
            int dirty = 0;
            if (ks == XK_w || ks == XK_W || ks == XK_Up) dirty = game_try_move(&g, 0, -1);
            else if (ks == XK_s || ks == XK_S || ks == XK_Down) dirty = game_try_move(&g, 0, 1);
            else if (ks == XK_a || ks == XK_A || ks == XK_Left) dirty = game_try_move(&g, -1, 0);
            else if (ks == XK_d || ks == XK_D || ks == XK_Right) dirty = game_try_move(&g, 1, 0);
            else if (ks == XK_z || ks == XK_Z) dirty = game_undo(&g);
            else if (ks == XK_r || ks == XK_R) { load(); dirty = 1; }
            else if (ks == XK_q || ks == XK_Q || ks == XK_Escape) break;
            if (dirty) {
                draw(dpy, win, gc, cmap);
            }
            /* always redraw on any game key for simplicity */
            if (ks == XK_w || ks == XK_W || ks == XK_Up ||
                ks == XK_s || ks == XK_S || ks == XK_Down ||
                ks == XK_a || ks == XK_A || ks == XK_Left ||
                ks == XK_d || ks == XK_D || ks == XK_Right ||
                ks == XK_z || ks == XK_Z || ks == XK_r || ks == XK_R)
                draw(dpy, win, gc, cmap);
        }
    }
    XFreeGC(dpy, gc);
    XDestroyWindow(dpy, win);
    XCloseDisplay(dpy);
    return 0;
}
