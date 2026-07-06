/* game.c — 游戏状态、移动、撤销、胜利判定 */
#include "game.h"

#include <stdlib.h>
#include <string.h>

/* 内部：把箱子位置从 from 改到 to（线性查找） */
static void move_box(GameState *s, int fromX, int fromY, int toX, int toY) {
    for (int i = 0; i < s->nBoxes; i++) {
        if (s->boxes[i].x == fromX && s->boxes[i].y == fromY) {
            s->boxes[i].x = toX;
            s->boxes[i].y = toY;
            return;
        }
    }
}

/* 内部：压栈一条历史 */
static void hist_push(GameState *s, Pos playerBefore, int hadBox, Pos boxFrom, Pos boxTo) {
    if (s->histCount == s->histCap) {
        int newCap = s->histCap ? s->histCap * 2 : 64;
        s->histPlayer = (Pos *)realloc(s->histPlayer, sizeof(Pos) * newCap);
        s->histBoxFrom = (Pos *)realloc(s->histBoxFrom, sizeof(Pos) * newCap);
        s->histBoxTo   = (Pos *)realloc(s->histBoxTo,   sizeof(Pos) * newCap);
        s->histHadBox  = (int *)realloc(s->histHadBox,  sizeof(int)  * newCap);
        s->histCap = newCap;
    }
    s->histPlayer[s->histCount] = playerBefore;
    s->histHadBox[s->histCount] = hadBox;
    if (hadBox) {
        s->histBoxFrom[s->histCount] = boxFrom;
        s->histBoxTo[s->histCount]   = boxTo;
    }
    s->histCount++;
}

void game_load(Level *lvl, int index, GameState *out) {
    /* 计算尺寸 */
    int w = 0, h = lvl->rowCount;
    for (int r = 0; r < lvl->rowCount; r++) {
        int len = (int)strlen(lvl->puzzle[r]);
        if (len > w) w = len;
    }
    if (w < 1) w = 1;
    if (h < 1) h = 1;

    /* 释放旧数据 */
    game_free(out);

    out->w = w;
    out->h = h;
    out->cells = (char *)malloc((size_t)w * h);
    /* 默认全部地板 */
    memset(out->cells, '-', (size_t)w * h);

    /* 先统计箱子和目标数 */
    int boxCap = 16, goalCap = 16;
    Pos *boxes = (Pos *)malloc(sizeof(Pos) * boxCap);
    Pos *goals = (Pos *)malloc(sizeof(Pos) * goalCap);
    int nBox = 0, nGoal = 0;
    out->player.x = 0; out->player.y = 0;

    for (int y = 0; y < h; y++) {
        const char *row = lvl->puzzle[y];
        int len = (int)strlen(row);
        for (int x = 0; x < w; x++) {
            char ch = (x < len) ? row[x] : '-';
            char base = '-';
            switch (ch) {
                case '#': base = '#'; break;
                case '.':
                    base = '.';
                    if (nGoal == goalCap) {
                        goalCap *= 2;
                        goals = (Pos *)realloc(goals, sizeof(Pos) * goalCap);
                    }
                    goals[nGoal].x = x; goals[nGoal].y = y; nGoal++;
                    break;
                case '-': base = '-'; break;
                case '$':
                    base = '-';
                    if (nBox == boxCap) {
                        boxCap *= 2;
                        boxes = (Pos *)realloc(boxes, sizeof(Pos) * boxCap);
                    }
                    boxes[nBox].x = x; boxes[nBox].y = y; nBox++;
                    break;
                case '*':
                    base = '.';
                    if (nBox == boxCap) {
                        boxCap *= 2;
                        boxes = (Pos *)realloc(boxes, sizeof(Pos) * boxCap);
                    }
                    boxes[nBox].x = x; boxes[nBox].y = y; nBox++;
                    if (nGoal == goalCap) {
                        goalCap *= 2;
                        goals = (Pos *)realloc(goals, sizeof(Pos) * goalCap);
                    }
                    goals[nGoal].x = x; goals[nGoal].y = y; nGoal++;
                    break;
                case '@':
                    base = '-';
                    out->player.x = x; out->player.y = y;
                    break;
                case '+':
                    base = '.';
                    out->player.x = x; out->player.y = y;
                    if (nGoal == goalCap) {
                        goalCap *= 2;
                        goals = (Pos *)realloc(goals, sizeof(Pos) * goalCap);
                    }
                    goals[nGoal].x = x; goals[nGoal].y = y; nGoal++;
                    break;
                default:
                    base = '-';  /* 未知字符当地板 */
                    break;
            }
            out->cells[y * w + x] = base;
        }
    }

    out->boxes = boxes;
    out->nBoxes = nBox;
    out->goals = goals;
    out->nGoals = nGoal;
    out->moves = 0;
    out->won = 0;
    out->levelIndex = index;
    out->histPlayer = NULL;
    out->histBoxFrom = NULL;
    out->histBoxTo = NULL;
    out->histHadBox = NULL;
    out->histCount = 0;
    out->histCap = 0;
}

void game_free(GameState *s) {
    if (s->cells) { free(s->cells); s->cells = NULL; }
    if (s->boxes) { free(s->boxes); s->boxes = NULL; }
    if (s->goals) { free(s->goals); s->goals = NULL; }
    if (s->histPlayer) { free(s->histPlayer); s->histPlayer = NULL; }
    if (s->histBoxFrom) { free(s->histBoxFrom); s->histBoxFrom = NULL; }
    if (s->histBoxTo)   { free(s->histBoxTo);   s->histBoxTo = NULL; }
    if (s->histHadBox)  { free(s->histHadBox);  s->histHadBox = NULL; }
    s->nBoxes = s->nGoals = 0;
    s->histCount = s->histCap = 0;
}

void game_reset(GameState *s, LevelSet *ls) {
    if (s->levelIndex < 0 || s->levelIndex >= ls->count) return;
    /* game_load 会先 game_free 旧数据 */
    game_load(&ls->items[s->levelIndex], s->levelIndex, s);
}

int game_is_box_at(const GameState *s, int x, int y) {
    for (int i = 0; i < s->nBoxes; i++) {
        if (s->boxes[i].x == x && s->boxes[i].y == y) return 1;
    }
    return 0;
}

int game_is_goal_at(const GameState *s, int x, int y) {
    if (x < 0 || y < 0 || x >= s->w || y >= s->h) return 0;
    return s->cells[y * s->w + x] == '.';
}

char game_cell_at(const GameState *s, int x, int y) {
    if (x < 0 || y < 0 || x >= s->w || y >= s->h) return '#';
    char base = s->cells[y * s->w + x];
    if (s->player.x == x && s->player.y == y) {
        return base == '.' ? '+' : '@';
    }
    if (game_is_box_at(s, x, y)) {
        return base == '.' ? '*' : '$';
    }
    return base;
}

/* 内部核心：执行一次移动，返回是否移动 */
static int do_move(GameState *s, int dx, int dy, int checkWin) {
    if (s->won) return 0;

    int nx = s->player.x + dx;
    int ny = s->player.y + dy;
    if (nx < 0 || ny < 0 || nx >= s->w || ny >= s->h) return 0;
    char nb = s->cells[ny * s->w + nx];
    if (nb == '#') return 0;

    Pos playerBefore = s->player;

    if (game_is_box_at(s, nx, ny)) {
        int bx = nx + dx;
        int by = ny + dy;
        if (bx < 0 || by < 0 || bx >= s->w || by >= s->h) return 0;
        char bb = s->cells[by * s->w + bx];
        if (bb == '#') return 0;
        if (game_is_box_at(s, bx, by)) return 0;

        /* 推箱子 */
        Pos from = { nx, ny }, to = { bx, by };
        move_box(s, nx, ny, bx, by);
        s->player.x = nx; s->player.y = ny;
        s->moves++;
        hist_push(s, playerBefore, 1, from, to);
        if (checkWin) game_check_win(s);
        return 1;
    }

    /* 纯移动 */
    s->player.x = nx; s->player.y = ny;
    s->moves++;
    hist_push(s, playerBefore, 0, (Pos){0,0}, (Pos){0,0});
    return 1;
}

int game_try_move(GameState *s, int dx, int dy) {
    return do_move(s, dx, dy, 1);
}

int game_try_move_instant(GameState *s, int dx, int dy) {
    return do_move(s, dx, dy, 1);   /* 检查胜利也无害，won 标志会被设置 */
}

void game_undo(GameState *s) {
    if (s->won) return;
    if (s->histCount == 0) return;

    /* 弹出栈顶直到遇到推箱动作（与 HTML 行为一致） */
    int poppedBox = 0;
    while (s->histCount > 0 && !poppedBox) {
        int idx = --s->histCount;
        Pos pb = s->histPlayer[idx];
        int hadBox = s->histHadBox[idx];
        if (hadBox) {
            Pos from = s->histBoxFrom[idx];
            Pos to   = s->histBoxTo[idx];
            /* 把箱子从 to 移回 from */
            move_box(s, to.x, to.y, from.x, from.y);
            s->player = pb;
            s->moves--;
            poppedBox = 1;
        } else {
            /* 纯移动：恢复玩家位置，步数减一，继续弹 */
            s->player = pb;
            s->moves--;
        }
    }
}

int game_check_win(GameState *s) {
    if (s->nBoxes == 0) { s->won = 1; return 1; }
    for (int i = 0; i < s->nBoxes; i++) {
        int onGoal = 0;
        for (int j = 0; j < s->nGoals; j++) {
            if (s->goals[j].x == s->boxes[i].x && s->goals[j].y == s->boxes[i].y) {
                onGoal = 1; break;
            }
        }
        if (!onGoal) { s->won = 0; return 0; }
    }
    s->won = 1;
    return 1;
}
