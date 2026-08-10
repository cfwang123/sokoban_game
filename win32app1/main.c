/**
 * win32app1 — Win32 API 推箱子（教学演示源码）
 * 纯 User32/GDI，无 MFC / 无 CRT 依赖以外的库。
 *
 * 不要求在本仓库内编译。若本机有 MinGW/MSVC：
 *   gcc -O2 main.c game.c -o sokoban.exe -mwindows -lgdi32 -luser32
 *   或 cl /O2 main.c game.c user32.lib gdi32.lib
 *
 * 键位：WASD / 方向键 移动，Z 撤销，R 重置，Esc 退出
 */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include "game.h"

#define CELL 40
#define PAD  16

static GameState g;
static const char *LEVEL[] = {
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
};
static const int NLEVEL = 7;

static void load_level(void)
{
    game_from_rows(&g, LEVEL, NLEVEL);
}

static void paint(HWND hwnd, HDC hdc)
{
    int x, y;
    RECT rc, client;
    HBRUSH brWall, brFloor, brBox, brBoxOk, brPlayer, brGoal;
    char status[64];
    int ww, wh;

    GetClientRect(hwnd, &client);
    FillRect(hdc, &client, (HBRUSH)GetStockObject(DKGRAY_BRUSH));

    brWall = CreateSolidBrush(RGB(74, 74, 106));
    brFloor = CreateSolidBrush(RGB(58, 58, 85));
    brBox = CreateSolidBrush(RGB(243, 156, 18));
    brBoxOk = CreateSolidBrush(RGB(46, 204, 113));
    brPlayer = CreateSolidBrush(RGB(52, 152, 219));
    brGoal = CreateSolidBrush(RGB(233, 69, 96));

    for (y = 0; y < g.height; y++) {
        for (x = 0; x < g.width; x++) {
            rc.left = PAD + x * CELL;
            rc.top = PAD + y * CELL;
            rc.right = rc.left + CELL;
            rc.bottom = rc.top + CELL;
            if (g.map[x][y] == '#') {
                FillRect(hdc, &rc, brWall);
            } else {
                FillRect(hdc, &rc, brFloor);
                FrameRect(hdc, &rc, brWall);
                if (g.map[x][y] == '.' || g.map[x][y] == '*') {
                    Ellipse(hdc,
                            rc.left + CELL / 2 - 6, rc.top + CELL / 2 - 6,
                            rc.left + CELL / 2 + 6, rc.top + CELL / 2 + 6);
                    /* goal filled separately below */
                }
                if (g.map[x][y] == '.' || g.map[x][y] == '*') {
                    SelectObject(hdc, brGoal);
                    Ellipse(hdc,
                            rc.left + CELL / 2 - 6, rc.top + CELL / 2 - 6,
                            rc.left + CELL / 2 + 6, rc.top + CELL / 2 + 6);
                }
                if (g.map[x][y] == '$' || g.map[x][y] == '*') {
                    RECT b = { rc.left + 4, rc.top + 4, rc.right - 4, rc.bottom - 4 };
                    FillRect(hdc, &b, (g.map[x][y] == '*') ? brBoxOk : brBox);
                }
            }
            if (x == g.px && y == g.py) {
                SelectObject(hdc, brPlayer);
                Ellipse(hdc,
                        rc.left + 6, rc.top + 6,
                        rc.right - 6, rc.bottom - 6);
            }
        }
    }

    SetBkMode(hdc, TRANSPARENT);
    SetTextColor(hdc, RGB(255, 255, 255));
    wsprintfA(status, "moves=%d%s  WASD Z R Esc", g.moves, g.won ? " WIN" : "");
    TextOutA(hdc, 8, PAD + g.height * CELL + 4, status, lstrlenA(status));

    DeleteObject(brWall);
    DeleteObject(brFloor);
    DeleteObject(brBox);
    DeleteObject(brBoxOk);
    DeleteObject(brPlayer);
    DeleteObject(brGoal);

    (void)ww;
    (void)wh;
}

static LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    PAINTSTRUCT ps;
    HDC hdc;
    int dx, dy;

    switch (msg) {
    case WM_CREATE:
        load_level();
        return 0;
    case WM_PAINT:
        hdc = BeginPaint(hwnd, &ps);
        paint(hwnd, hdc);
        EndPaint(hwnd, &ps);
        return 0;
    case WM_KEYDOWN:
        dx = dy = 0;
        switch (wParam) {
        case 'W': case VK_UP:    dy = -1; break;
        case 'S': case VK_DOWN:  dy = 1; break;
        case 'A': case VK_LEFT:  dx = -1; break;
        case 'D': case VK_RIGHT: dx = 1; break;
        case 'Z': game_undo(&g); InvalidateRect(hwnd, NULL, TRUE); return 0;
        case 'R': load_level(); InvalidateRect(hwnd, NULL, TRUE); return 0;
        case VK_ESCAPE: case 'Q': DestroyWindow(hwnd); return 0;
        default: return DefWindowProc(hwnd, msg, wParam, lParam);
        }
        if (dx || dy) {
            game_try_move(&g, dx, dy);
            InvalidateRect(hwnd, NULL, TRUE);
        }
        return 0;
    case WM_DESTROY:
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProc(hwnd, msg, wParam, lParam);
}

int WINAPI WinMain(HINSTANCE hInst, HINSTANCE hPrev, LPSTR lpCmd, int nShow)
{
    WNDCLASSA wc;
    HWND hwnd;
    MSG msg;
    int ww, wh;

    (void)hPrev;
    (void)lpCmd;

    ZeroMemory(&wc, sizeof(wc));
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInst;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wc.lpszClassName = "SokobanWin32";
    RegisterClassA(&wc);

    load_level();
    ww = PAD * 2 + g.width * CELL + 16;
    wh = PAD * 2 + g.height * CELL + 48;

    hwnd = CreateWindowA("SokobanWin32", "Sokoban Win32 API (teaching)",
                         WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,
                         CW_USEDEFAULT, CW_USEDEFAULT, ww, wh,
                         NULL, NULL, hInst, NULL);
    ShowWindow(hwnd, nShow);
    UpdateWindow(hwnd);

    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    return (int)msg.wParam;
}
