/* main.c - 推箱子 C 命令行版主程序 (跨平台) */
#include "console.h"
#include "levels.h"
#include "game.h"
#include "pathfinding.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>

/* ---- 常量 ---- */
#define ANIM_INTERVAL_MS 60   /* 答案回放每步间隔 */
#define MAX_BUF_W        200  /* 缓冲区最大宽度 */

/* ---- 全局状态 ---- */
static LevelSet   g_levels;
static GameState  g_state;
static Cell      *g_front = NULL;  /* buf_w * buf_h */
static Cell      *g_back  = NULL;
static int        g_buf_w = 0;
static int        g_buf_h = 0;
static int        g_ox = 0;        /* 游戏区在缓冲区中的 x 偏移 */
static int        g_oy = 2;        /* 标题栏占第 0 行，状态栏占第 1 行，游戏从第 2 行开始 */

/* 答案回放 */
static char *g_aiQueue = NULL;
static int   g_aiQueueLen = 0;
static int   g_aiQueuePos = 0;
static int   g_aiActive = 0;
static unsigned long g_aiLastTick = 0;

/* 选关模式 */
static int   g_selecting = 0;
static char  g_selectBuf[16];
static int   g_selectPos = 0;

/* 窗口 resize 防抖 */
static int   g_resizePending = 0;
static unsigned long g_resizeTick = 0;

/* ---- 缓冲区分配 ---- */
static int alloc_buffers(int levelW, int levelH) {
    int w = levelW;
    if (w < 70) w = 70;
    if (w > MAX_BUF_W) w = MAX_BUF_W;
    int h = levelH + 3;  /* 状态栏 + 关卡 + 过关提示 + 余量 */

    if (w != g_buf_w || h != g_buf_h) {
        free(g_front);
        free(g_back);
        g_front = (Cell *)malloc(sizeof(Cell) * (size_t)w * h);
        g_back  = (Cell *)malloc(sizeof(Cell) * (size_t)w * h);
        if (!g_front || !g_back) return -1;
        g_buf_w = w;
        g_buf_h = h;
        /* 重置 back 为未知，强制全量重绘 */
        for (int i = 0; i < w * h; i++) {
            g_back[i].ch = 0;
            g_back[i].attr = 0xFFFF;
        }
    }
    return 0;
}

/* ---- 把一个宽字符串写进缓冲区的某一行（超出宽度截断） ---- */
static void buf_write_str(int row, int col, const wchar_t *s, unsigned short attr) {
    if (row < 0 || row >= g_buf_h) return;
    int c = col;
    for (int i = 0; s[i] && c < g_buf_w; i++) {
        int idx = row * g_buf_w + c;
        g_front[idx].ch = s[i];
        g_front[idx].attr = attr;
        c++;
        /* CJK 字符占 2 格，下一格标记为占位 */
        if (s[i] >= 0x4E00) {
            if (c < g_buf_w) {
                int idx2 = row * g_buf_w + c;
                g_front[idx2].ch = 0;
                g_front[idx2].attr = 0;
            }
            c++;
        }
    }
}

/* ---- 把缓冲区某一行填成 ch + attr ---- */
static void buf_fill_row(int row, wchar_t ch, unsigned short attr) {
    if (row < 0 || row >= g_buf_h) return;
    for (int x = 0; x < g_buf_w; x++) {
        int idx = row * g_buf_w + x;
        g_front[idx].ch = ch;
        g_front[idx].attr = attr;
    }
}

/* ---- 构造 front 缓冲区（根据 g_state） ---- */
static void render_front(void) {
    /* ---- 更新窗口标题 ---- */
    wchar_t title[128];
    const char *lvlName = "";
    if (g_state.levelIndex >= 0 && g_state.levelIndex < g_levels.count) {
        lvlName = g_levels.items[g_state.levelIndex].name;
    }
    wchar_t wname[64];
    int i;
    for (i = 0; i < 63 && lvlName[i]; i++) wname[i] = (wchar_t)lvlName[i];
    wname[i] = 0;
    swprintf(title, 128, L"Sokoban Level %d/%d (%ls) Moves %d",
             g_state.levelIndex + 1, g_levels.count, wname, g_state.moves);
    con_set_title(title);

    /* ---- 标题行：第 0 行（含 CJK） ---- */
    buf_fill_row(0, L' ', ATTR_STATUSBAR);
    swprintf(title, 128, L"推箱子 关卡%d/%d(%ls) 步数%d",
             g_state.levelIndex + 1, g_levels.count, wname, g_state.moves);
    buf_write_str(0, 0, title, ATTR_STATUSBAR);

    /* ---- 状态栏：第 1 行 ---- */
    buf_fill_row(1, L' ', ATTR_STATUSBAR);

    wchar_t status[256];
    if (g_selecting) {
        swprintf(status, 256, L" 选关: 输入关卡号 (1-%d): %s",
                 g_levels.count, g_selectBuf);
    } else if (g_aiActive) {
        swprintf(status, 256, L" 答案回放中 %d/%d  [任意键]停止",
                 g_aiQueuePos, g_aiQueueLen);
    } else if (g_state.won) {
        swprintf(status, 256, L" 已过关! [Space]下一关  [F1]答案  [F2]选关  [Q]退出");
    } else {
        swprintf(status, 256, L" [F1]答案  [Z]撤销  [R]重置  [PgUp/PgDn]切关  [F2]选关  [Q]退出");
    }
    buf_write_str(1, 0, status, ATTR_STATUSBAR);

    /* ---- 游戏区：第 2..h+1 行 ---- */
    for (int y = 0; y < g_state.h; y++) {
        int row = g_oy + y;
        if (row >= g_buf_h) break;
        /* 先把该行地图范围内的格子填成深蓝底空格（消除上一关残留） */
        for (int x = 0; x < g_state.w && x < g_buf_w; x++) {
            int idx = row * g_buf_w + x;
            g_front[idx].ch = L' ';
            g_front[idx].attr = ATTR_FLOOR;
        }
        /* 地图外围不显示任何东西 */
        for (int x = g_state.w; x < g_buf_w; x++) {
            int idx = row * g_buf_w + x;
            g_front[idx].ch = L' ';
            g_front[idx].attr = 0;
        }
        /* 再画关卡 */
        for (int x = 0; x < g_state.w && x < g_buf_w; x++) {
            char c = game_cell_at(&g_state, x, y);
            int idx = row * g_buf_w + x;
            switch (c) {
                case '#':
                    g_front[idx].ch = L'#';  /* # 墙 */
                    g_front[idx].attr = ATTR_WALL;
                    break;
                case '-':
                    g_front[idx].ch = L' ';
                    g_front[idx].attr = ATTR_FLOOR;
                    break;
                case '.':
                    g_front[idx].ch = L'.';  /* . 目标 */
                    g_front[idx].attr = ATTR_GOAL;
                    break;
                case '$':
                    g_front[idx].ch = L'$';  /* $ 箱子未到位 */
                    g_front[idx].attr = ATTR_BOX;
                    break;
                case '*':
                    g_front[idx].ch = L'$';  /* $ 箱子已到位 */
                    g_front[idx].attr = ATTR_BOX_GOAL;
                    break;
                case '@':
                    g_front[idx].ch = L'\u263B';  /* ☻ 玩家 */
                    g_front[idx].attr = ATTR_PLAYER;
                    break;
                case '+':
                    g_front[idx].ch = L'\u263B';  /* ☻ 玩家在目标 */
                    g_front[idx].attr = ATTR_PLAYER_GOAL;
                    break;
                default:
                    g_front[idx].ch = L'?';
                    g_front[idx].attr = ATTR_FLOOR;
                    break;
            }
        }
    }

    /* 过关提示行：仅当过关时写消息，不加蓝色背景 */
    int winRow = g_oy + g_state.h;
    if (winRow < g_buf_h) {
        buf_fill_row(winRow, L' ', 0);
        if (g_state.won) {
            buf_write_str(winRow, 0, L" 恭喜过关！按 Space 进入下一关", ATTR_WINMSG);
        }
    }

    /* 清除地图下方所有残留行（切关后旧关卡残留） */
    for (int y = winRow + 1; y < g_buf_h; y++) {
        buf_fill_row(y, L' ', 0);
    }
}

/* ---- 增量刷新到控制台 ---- */
static void present(void) {
    con_present(g_front, g_back, g_buf_w, g_buf_h, 0, 0);
}

/* ---- 强制全量重绘（清 back） ---- */
static void invalidate_back(void) {
    for (int i = 0; i < g_buf_w * g_buf_h; i++) {
        g_back[i].ch = 0;
        g_back[i].attr = 0xFFFF;
    }
}

/* ---- lastlevel.ini 持久化 ---- */
static int load_last_level(void) {
    FILE *f = fopen("lastlevel.ini", "r");
    if (!f) return 0;
    int n = 0;
    if (fscanf(f, "%d", &n) != 1) n = 0;
    fclose(f);
    if (n < 0 || n >= g_levels.count) n = 0;
    return n;
}

static void save_last_level(int idx) {
    FILE *f = fopen("lastlevel.ini", "w");
    if (!f) return;
    fprintf(f, "%d\n", idx);
    fclose(f);
}

/* ---- 加载关卡 ---- */
static void load_level(int index) {
    if (index < 0 || index >= g_levels.count) return;
    game_load(&g_levels.items[index], index, &g_state);
    alloc_buffers(g_state.w, g_state.h);
    con_clear();  /* 清屏，清除旧关卡残留 */
    invalidate_back();
    render_front();
    present();
    save_last_level(index);
}

/* ---- 答案回放 ---- */
static void ai_stop(void) {
    g_aiActive = 0;
    if (g_aiQueue) {
        free(g_aiQueue);
        g_aiQueue = NULL;
    }
    g_aiQueueLen = 0;
    g_aiQueuePos = 0;
    render_front();
    present();
}

static void ai_start(void) {
    if (g_state.won) return;
    if (g_state.levelIndex < 0 || g_state.levelIndex >= g_levels.count) return;
    const char *sol = g_levels.items[g_state.levelIndex].solution;
    if (!sol || !sol[0]) {
        /* 无答案，不做任何事 */
        return;
    }
    /* 重置关卡后开始播放 */
    game_reset(&g_state, &g_levels);
    invalidate_back();

    g_aiQueueLen = (int)strlen(sol);
    g_aiQueue = (char *)malloc((size_t)g_aiQueueLen + 1);
    memcpy(g_aiQueue, sol, (size_t)g_aiQueueLen + 1);
    g_aiQueuePos = 0;
    g_aiActive = 1;
    g_aiLastTick = con_get_tick();

    render_front();
    present();
}

/* 方向字符 -> (dx, dy) */
static int dir_to_delta(char d, int *dx, int *dy) {
    switch (d) {
        case 'U': case 'u': *dx = 0;  *dy = -1; return 1;
        case 'D': case 'd': *dx = 0;  *dy = 1;  return 1;
        case 'L': case 'l': *dx = -1; *dy = 0;  return 1;
        case 'R': case 'r': *dx = 1;  *dy = 0;  return 1;
    }
    return 0;
}

/* ---- 鼠标点击处理（与 HTML 逻辑一致） ---- */
static void handle_mouse_click(int mx, int my) {
    if (g_aiActive || g_state.won) return;

    int gx = mx - g_ox;
    int gy = my - g_oy;
    if (gx < 0 || gy < 0 || gx >= g_state.w || gy >= g_state.h) return;

    /* 点击玩家相邻的箱子 -> 推 1 格 */
    if (game_is_box_at(&g_state, gx, gy)) {
        int dx = gx - g_state.player.x;
        int dy = gy - g_state.player.y;
        if (abs(dx) + abs(dy) == 1) {
            if (game_try_move(&g_state, dx, dy)) {
                render_front();
                present();
            }
        }
        return;
    }

    /* 点击空地 -> BFS 寻路 */
    char base = g_state.cells[gy * g_state.w + gx];
    if (base == '#') return;
    if (game_is_box_at(&g_state, gx, gy)) return;

    int pathLen = 0;
    char *path = path_find(&g_state, gx, gy, &pathLen);
    if (!path) return;

    /* 同步执行完所有步，最后一次渲染 */
    for (int i = 0; i < pathLen; i++) {
        int dx, dy;
        if (!dir_to_delta(path[i], &dx, &dy)) continue;
        game_try_move_instant(&g_state, dx, dy);
        if (g_state.won) break;
    }
    free(path);

    render_front();
    present();
}

/* ---- 键盘处理 ---- */
static void handle_key(int vk, int unicode) {
    /* AI 回放中：任何键都停止回放（且消费该按键，不执行动作） */
    if (g_aiActive) {
        ai_stop();
        return;
    }

    /* ---- 选关模式输入 ---- */
    if (g_selecting) {
        if (vk == VK_ESCAPE) {
            g_selecting = 0;
            render_front();
            present();
            return;
        }
        if (vk == VK_RETURN) {
            g_selectBuf[g_selectPos] = '\0';
            int n = atoi(g_selectBuf);
            g_selecting = 0;
            if (n >= 1 && n <= g_levels.count) {
                load_level(n - 1);
            } else {
                render_front();
                present();
            }
            return;
        }
        if (vk == VK_BACK && g_selectPos > 0) {
            g_selectPos--;
            g_selectBuf[g_selectPos] = '\0';
            render_front();
            present();
            return;
        }
        if (unicode >= '0' && unicode <= '9' && g_selectPos < (int)sizeof(g_selectBuf) - 1) {
            g_selectBuf[g_selectPos++] = (char)unicode;
            g_selectBuf[g_selectPos] = '\0';
            render_front();
            present();
            return;
        }
        return;  /* 其他键忽略 */
    }

    int dx = 0, dy = 0;
    int handled = 1;

    switch (vk) {
        case VK_UP:    case 'W': case 'w':  dx = 0;  dy = -1; break;
        case VK_DOWN:  case 'S': case 's':  dx = 0;  dy = 1;  break;
        case VK_LEFT:  case 'A': case 'a':  dx = -1; dy = 0;  break;
        case VK_RIGHT: case 'D': case 'd':  dx = 1;  dy = 0;  break;
        case 'Z': case 'z':
            game_undo(&g_state);
            render_front();
            present();
            return;
        case 'R': case 'r':
            game_reset(&g_state, &g_levels);
            invalidate_back();
            render_front();
            present();
            return;
        case 'Q':
        case VK_ESCAPE:
            exit(0);
            return;
        case VK_F1:
            ai_start();
            return;
        case VK_F2:
            g_selecting = 1;
            g_selectPos = 0;
            g_selectBuf[0] = '\0';
            render_front();
            present();
            return;
        case VK_SPACE:
            if (g_state.won) {
                int next = g_state.levelIndex + 1;
                if (next < g_levels.count) load_level(next);
            }
            return;
        case VK_PRIOR: /* PageUp */
            if (g_state.levelIndex > 0) load_level(g_state.levelIndex - 1);
            return;
        case VK_NEXT:  /* PageDown */
            if (g_state.levelIndex + 1 < g_levels.count) load_level(g_state.levelIndex + 1);
            return;
        default:
            handled = 0;
    }
    if (!handled) return;

    if (g_state.won) return;

    if (game_try_move(&g_state, dx, dy)) {
        render_front();
        present();
    }
}

/* ---- 主循环 ---- */
int main(void) {
    con_init();
    con_clear();
    atexit(con_shutdown);

    /* 加载关卡 */
    if (levels_load("levels.json", &g_levels) != 0) {
        fprintf(stderr, "无法加载 levels.json，请确保该文件与 sokoban 同目录。\n");
        return 1;
    }
    fprintf(stderr, "已加载 %d 关\n", g_levels.count);

    int startLevel = load_last_level();
    load_level(startLevel);

    con_flush_input();

    /* 主循环 */
    for (;;) {
        int waitMs = 50;
        if (g_aiActive) {
            unsigned long now = con_get_tick();
            int since = (int)(now - g_aiLastTick);
            int remain = ANIM_INTERVAL_MS - since;
            if (remain < 1) remain = 1;
            if (remain < waitMs) waitMs = remain;
        }

        int type, k1, k2, mx, my;
        con_read_event(&type, &k1, &k2, &mx, &my, waitMs);

        if (type == EV_KEY) {
            handle_key(k1, k2);
        } else if (type == EV_MOUSE) {
            handle_mouse_click(mx, my);
        } else if (type == EV_RESIZE) {
            /* 延迟 500ms 再处理，避免连续 resize 频繁清屏 */
            g_resizePending = 1;
            g_resizeTick = con_get_tick();
        }

        /* 处理延迟的 resize */
        if (g_resizePending && (int)(con_get_tick() - g_resizeTick) >= 500) {
            g_resizePending = 0;
            con_clear();
            invalidate_back();
            render_front();
            present();
        }

        /* AI 步进 */
        if (g_aiActive) {
            unsigned long now = con_get_tick();
            if ((int)(now - g_aiLastTick) >= ANIM_INTERVAL_MS) {
                g_aiLastTick = now;
                if (g_aiQueuePos < g_aiQueueLen) {
                    int dx, dy;
                    if (dir_to_delta(g_aiQueue[g_aiQueuePos], &dx, &dy)) {
                        game_try_move_instant(&g_state, dx, dy);
                    }
                    g_aiQueuePos++;
                    render_front();
                    present();
                } else {
                    ai_stop();
                }
            }
        }
    }

    /* 不会到达 */
    levels_free(&g_levels);
    game_free(&g_state);
    free(g_front);
    free(g_back);
    return 0;
}
