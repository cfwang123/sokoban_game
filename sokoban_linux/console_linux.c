/* console_linux.c - Linux 控制台封装实现 (ncursesw) */
#include "console.h"

#ifndef _WIN32

#include <ncursesw/ncurses.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <wchar.h>
#include <locale.h>
#include <limits.h>

/* ---- 颜色对管理 ---- */
static int  s_color_ok = 0;
static int  s_pair_init[64];  /* 标记 64 个颜色对(8bg*8fg)是否已初始化 */

/* Win32 颜色位 -> ncurses 颜色值（恰好一致：R=4, G=2, B=1） */
static short nibble_to_nc(int nibble) {
    return (short)(nibble & 0x07);
}

/*
 * 把 Win32 attr 转换为 ncurses 属性。
 * 返回 attr_t（含 A_BOLD 等），pair_out 输出颜色对号。
 */
static attr_t attr_to_curses(unsigned short attr, short *pair_out) {
    int fg = attr & 0x0F;
    int bg = (attr >> 4) & 0x0F;

    short nc_fg = nibble_to_nc(fg);
    short nc_bg = nibble_to_nc(bg);
    short pair  = (short)(nc_bg * 8 + nc_fg + 1);  /* 1..64 */

    if (pair >= 1 && pair <= 64 && !s_pair_init[pair]) {
        init_pair(pair, nc_fg, nc_bg);
        s_pair_init[pair] = 1;
    }

    *pair_out = pair;
    return (fg & 0x08) ? A_BOLD : A_NORMAL;
}

/* ---- 接口实现 ---- */

void con_init(void) {
    setlocale(LC_ALL, "");
    initscr();
    cbreak();
    noecho();
    keypad(stdscr, TRUE);
    curs_set(0);  /* 隐藏光标 */

    /* 缩短 ESC 延迟，避免按键卡顿 */
    ESCDELAY = 25;

    s_color_ok = has_colors();
    if (s_color_ok) {
        start_color();
        use_default_colors();
        memset(s_pair_init, 0, sizeof(s_pair_init));
    }

    /* 启用鼠标点击 */
    mousemask(BUTTON1_CLICKED, NULL);

    /* 设置窗口标题 */
    printf("\033]0;Sokoban\007");
    fflush(stdout);
}

void con_shutdown(void) {
    endwin();
}

void con_clear(void) {
    clear();
    refresh();
}

void con_get_size(int *w, int *h) {
    if (w) *w = COLS;
    if (h) *h = LINES;
}

void con_present(const Cell *front, Cell *back, int w, int h, int ox, int oy) {
    for (int y = 0; y < h; y++) {
        for (int x = 0; x < w; x++) {
            int idx = y * w + x;
            const Cell *f = &front[idx];
            Cell *b = back ? &back[idx] : NULL;

            /* CJK 占位格：跳过 */
            if (f->ch == 0) {
                if (b) *b = *f;
                continue;
            }

            /* 比较是否需要重绘 */
            int needDraw = 1;
            if (b && b->ch == f->ch && b->attr == f->attr) {
                needDraw = 0;
            }
            if (!needDraw) continue;

            int sy = oy + y;
            int sx = ox + x;
            if (sy < 0 || sy >= LINES || sx < 0 || sx >= COLS) {
                if (b) *b = *f;
                continue;
            }

            if (s_color_ok) {
                short pair;
                attr_t extra = attr_to_curses(f->attr, &pair);
                cchar_t cch;
                wchar_t wch[2] = { f->ch, 0 };
                setcchar(&cch, wch, extra, pair, NULL);
                mvadd_wch(sy, sx, &cch);
            } else {
                /* 无颜色支持：用普通字符输出 */
                move(sy, sx);
                char mb[MB_LEN_MAX];
                int n = wctomb(mb, (wint_t)f->ch);
                if (n > 0) addnstr(mb, n);
            }

            if (b) *b = *f;
        }
    }
    refresh();
}

void con_flush_input(void) {
    nodelay(stdscr, TRUE);
    while (getch() != ERR) {}
    nodelay(stdscr, FALSE);
}

int con_read_event(int *outType, int *k1, int *k2, int *mx, int *my, int waitMs) {
    *outType = EV_NONE;
    if (k1) *k1 = 0;
    if (k2) *k2 = 0;
    if (mx) *mx = 0;
    if (my) *my = 0;

    struct timeval start, now;
    gettimeofday(&start, NULL);

    for (;;) {
        gettimeofday(&now, NULL);
        long elapsed = (now.tv_sec - start.tv_sec) * 1000
                     + (now.tv_usec - start.tv_usec) / 1000;
        int remain = waitMs - (int)elapsed;
        if (remain < 1) return EV_NONE;

        timeout(remain);
        int ch = getch();

        if (ch == ERR) return EV_NONE;

        switch (ch) {
            case KEY_UP:     *outType = EV_KEY; *k1 = VK_UP;     return EV_KEY;
            case KEY_DOWN:   *outType = EV_KEY; *k1 = VK_DOWN;   return EV_KEY;
            case KEY_LEFT:   *outType = EV_KEY; *k1 = VK_LEFT;   return EV_KEY;
            case KEY_RIGHT:  *outType = EV_KEY; *k1 = VK_RIGHT;  return EV_KEY;
            case KEY_F(1):   *outType = EV_KEY; *k1 = VK_F1;     return EV_KEY;
            case KEY_F(2):   *outType = EV_KEY; *k1 = VK_F2;     return EV_KEY;
            case KEY_PPAGE:  *outType = EV_KEY; *k1 = VK_PRIOR;  return EV_KEY;
            case KEY_NPAGE:  *outType = EV_KEY; *k1 = VK_NEXT;   return EV_KEY;
            case KEY_BACKSPACE:
            case 127:
            case 8:          *outType = EV_KEY; *k1 = VK_BACK;   *k2 = VK_BACK;   return EV_KEY;
            case KEY_ENTER:
            case '\n':
            case 13:         *outType = EV_KEY; *k1 = VK_RETURN; *k2 = VK_RETURN; return EV_KEY;
            case KEY_MOUSE: {
                MEVENT me;
                if (getmouse(&me) == OK && (me.bstate & BUTTON1_CLICKED)) {
                    *outType = EV_MOUSE;
                    if (mx) *mx = me.x;
                    if (my) *my = me.y;
                    return EV_MOUSE;
                }
                /* 其他鼠标事件：继续循环 */
                break;
            }
            case KEY_RESIZE:
                endwin();
                refresh();
                *outType = EV_RESIZE;
                return EV_RESIZE;
            case 27:  /* ESC */
                *outType = EV_KEY; *k1 = VK_ESCAPE; *k2 = 27;
                return EV_KEY;
            default:
                /* 普通字符：k1 和 k2 都设为字符值 */
                if (ch >= 0 && ch < 0x100) {
                    *outType = EV_KEY; *k1 = ch; *k2 = ch;
                    return EV_KEY;
                }
                /* 未识别的特殊键：忽略，继续循环 */
                break;
        }
    }
}

void con_set_title(const wchar_t *title) {
    /* 转换为多字节字符串后用转义序列设置终端标题 */
    char buf[256];
    wcstombs(buf, title, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\0';
    printf("\033]0;%s\007", buf);
    fflush(stdout);
}

unsigned long con_get_tick(void) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (unsigned long)(tv.tv_sec * 1000 + tv.tv_usec / 1000);
}

#endif /* !_WIN32 */
