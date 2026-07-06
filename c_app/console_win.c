/* console_win.c — Windows 控制台封装实现 */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#include "console.h"

#include <stdio.h>

static HANDLE s_hOut = INVALID_HANDLE_VALUE;
static HANDLE s_hIn  = INVALID_HANDLE_VALUE;
static DWORD  s_oldOutMode = 0;
static DWORD  s_oldInMode  = 0;
static UINT   s_oldCP = 0;

/* 颜色属性辅助宏 */
#define FG(r,g,b,i)  ((r)?FOREGROUND_RED:0)|((g)?FOREGROUND_GREEN:0)|((b)?FOREGROUND_BLUE:0)|((i)?FOREGROUND_INTENSITY:0)
#define BG(r,g,b,i)  ((r)?BACKGROUND_RED:0)|((g)?BACKGROUND_GREEN:0)|((b)?BACKGROUND_BLUE:0)|((i)?BACKGROUND_INTENSITY:0)

void con_init(void) {
    s_hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    s_hIn  = GetStdHandle(STD_INPUT_HANDLE);

    /* 保存旧模式 */
    GetConsoleMode(s_hOut, &s_oldOutMode);
    GetConsoleMode(s_hIn,  &s_oldInMode);
    s_oldCP = GetConsoleOutputCP();

    /* 启用 VT 处理（可选，便于颜色），同时启用鼠标/窗口输入 */
    SetConsoleMode(s_hOut, ENABLE_PROCESSED_OUTPUT | ENABLE_WRAP_AT_EOL_OUTPUT | ENABLE_VIRTUAL_TERMINAL_PROCESSING);

    /* 输入：禁用 quick edit（ENABLE_EXTENDED_FLAGS 关闭），启用鼠标+窗口+键盘 */
    SetConsoleMode(s_hIn,
        ENABLE_WINDOW_INPUT | ENABLE_MOUSE_INPUT | ENABLE_EXTENDED_FLAGS);

    /* UTF-8 输出（WriteConsoleW 不依赖此，但 printf 中文显示受益） */
    SetConsoleOutputCP(CP_UTF8);

    /* 设置窗口标题 */
    SetConsoleTitleW(L"推箱子");

    /* 隐藏光标 */
    CONSOLE_CURSOR_INFO ci;
    ci.dwSize = 1;
    ci.bVisible = FALSE;
    SetConsoleCursorInfo(s_hOut, &ci);
}

void con_shutdown(void) {
    con_clear();  /* 退出时清屏 */
    if (s_hOut != INVALID_HANDLE_VALUE) {
        SetConsoleMode(s_hOut, s_oldOutMode);
        CONSOLE_CURSOR_INFO ci;
        ci.dwSize = 1;
        ci.bVisible = TRUE;
        SetConsoleCursorInfo(s_hOut, &ci);
    }
    if (s_hIn != INVALID_HANDLE_VALUE) {
        SetConsoleMode(s_hIn, s_oldInMode);
    }
    if (s_oldCP) SetConsoleOutputCP(s_oldCP);
}

void con_clear(void) {
    COORD origin = {0, 0};
    DWORD written;
    CONSOLE_SCREEN_BUFFER_INFO csbi;
    GetConsoleScreenBufferInfo(s_hOut, &csbi);
    DWORD cells = (DWORD)csbi.dwSize.X * csbi.dwSize.Y;
    FillConsoleOutputCharacterW(s_hOut, L' ', cells, origin, &written);
    FillConsoleOutputAttribute(s_hOut, 0, cells, origin, &written);
    SetConsoleCursorPosition(s_hOut, origin);
}

void con_get_size(int *w, int *h) {
    CONSOLE_SCREEN_BUFFER_INFO csbi;
    GetConsoleScreenBufferInfo(s_hOut, &csbi);
    if (w) *w = csbi.srWindow.Right - csbi.srWindow.Left + 1;
    if (h) *h = csbi.srWindow.Bottom - csbi.srWindow.Top + 1;
}

void con_present(const Cell *front, Cell *back, int w, int h, int ox, int oy) {
    for (int y = 0; y < h; y++) {
        for (int x = 0; x < w; x++) {
            int idx = y * w + x;
            const Cell *f = &front[idx];
            Cell *b = back ? &back[idx] : NULL;

            /* CJK 占位格：跳过写入（CJK 字符写入时已占据该格），仅同步 back */
            if (f->ch == 0) {
                if (b) *b = *f;
                continue;
            }

            /* 比较是否需要重绘：字符或颜色不同，或 back 未知 */
            int needDraw = 1;
            if (b && b->ch == f->ch && b->attr == f->attr) {
                needDraw = 0;
            }
            if (!needDraw) continue;

            COORD pos = { (SHORT)(ox + x), (SHORT)(oy + y) };
            SetConsoleCursorPosition(s_hOut, pos);
            SetConsoleTextAttribute(s_hOut, f->attr);
            DWORD written;
            WriteConsoleW(s_hOut, &f->ch, 1, &written, NULL);

            if (b) *b = *f;
        }
    }
    /* 恢复默认属性以防状态栏/其他输出受影响 */
    SetConsoleTextAttribute(s_hOut, 0x07);
}

void con_flush_input(void) {
    DWORD n;
    GetNumberOfConsoleInputEvents(s_hIn, &n);
    if (n == 0) return;
    INPUT_RECORD *recs = (INPUT_RECORD *)malloc(sizeof(INPUT_RECORD) * n);
    if (!recs) return;
    DWORD got;
    ReadConsoleInputW(s_hIn, recs, n, &got);
    free(recs);
}

int con_read_event(int *outType, int *k1, int *k2, int *mx, int *my, int waitMs) {
    *outType = EV_NONE;
    if (k1) *k1 = 0;
    if (k2) *k2 = 0;
    if (mx) *mx = 0;
    if (my) *my = 0;

    DWORD startTick = GetTickCount();
    for (;;) {
        DWORD remaining;
        DWORD elapsed = GetTickCount() - startTick;
        if ((int)elapsed >= waitMs) return EV_NONE;
        remaining = (DWORD)(waitMs - (int)elapsed);

        /* 等待输入可用 */
        DWORD r = WaitForSingleObject(s_hIn, remaining);
        if (r == WAIT_TIMEOUT) return EV_NONE;
        if (r != WAIT_OBJECT_0) return EV_NONE;

        /* 读一个事件 */
        INPUT_RECORD rec;
        DWORD got;
        BOOL ok = ReadConsoleInputW(s_hIn, &rec, 1, &got);
        if (!ok || got == 0) return EV_NONE;

        if (rec.EventType == KEY_EVENT && rec.Event.KeyEvent.bKeyDown) {
            *outType = EV_KEY;
            if (k1) *k1 = rec.Event.KeyEvent.wVirtualKeyCode;
            if (k2) *k2 = rec.Event.KeyEvent.uChar.UnicodeChar;
            return EV_KEY;
        }
        if (rec.EventType == WINDOW_BUFFER_SIZE_EVENT) {
            *outType = EV_RESIZE;
            return EV_RESIZE;
        }
        if (rec.EventType == MOUSE_EVENT) {
            /* 左键按下：dwEventFlags==0 表示按下/释放事件（不是移动/滚轮） */
            DWORD btn = rec.Event.MouseEvent.dwButtonState;
            DWORD flags = rec.Event.MouseEvent.dwEventFlags;
            if ((btn & FROM_LEFT_1ST_BUTTON_PRESSED) && (flags == 0)) {
                *outType = EV_MOUSE;
                if (mx) *mx = rec.Event.MouseEvent.dwMousePosition.X;
                if (my) *my = rec.Event.MouseEvent.dwMousePosition.Y;
                return EV_MOUSE;
            }
            /* 其他鼠标事件忽略，继续循环 */
        }
        /* 其他事件忽略 */
    }
}
