/* 汇编教学共用：C 侧状态与可链入的 try_move 声明 */
#ifndef ASM_SOKOBAN_GAME_H
#define ASM_SOKOBAN_GAME_H

#define SK_MAX_W 32
#define SK_MAX_H 32
#define SK_MAX_HIST 256

typedef struct {
    int px, py;
    int bfx, bfy, btx, bty;
    int is_push;
} SkHist;

typedef struct {
    char map[SK_MAX_W * SK_MAX_H]; /* row-major: map[y*W+x] 实际用 width 步长 */
    int width, height;
    int px, py;
    int moves;
    int won;
    int hist_n;
    SkHist hist[SK_MAX_HIST];
} SkGame;

void sk_reset(SkGame *g);
int sk_try_move(SkGame *g, int dx, int dy); /* 可由汇编实现同名符号替换 */
int sk_undo(SkGame *g);
void sk_render(const SkGame *g, char *buf, int cap);
int sk_cell(const SkGame *g, int x, int y); /* 返回字符 */

/* 定义 SK_USE_ASM_TRY_MOVE 时 game.c 不提供 sk_try_move，改为链接各 ISA 的同名汇编符号 */

#endif
