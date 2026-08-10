/* 推箱子核心（Win32 教学共享） */
#ifndef SOKOBAN_GAME_H
#define SOKOBAN_GAME_H

#define MAX_W 32
#define MAX_H 32
#define MAX_HIST 1024

typedef struct {
    int px, py;
    int bfx, bfy, btx, bty;
    int is_push;
} Hist;

typedef struct {
    char map[MAX_W][MAX_H];
    int width, height;
    int px, py;
    int moves;
    int won;
    int hist_n;
    Hist hist[MAX_HIST];
} GameState;

void game_from_rows(GameState *s, const char **rows, int n);
int game_try_move(GameState *s, int dx, int dy);
int game_undo(GameState *s);
void game_render_ascii(const GameState *s, char *out, int out_cap);

#endif
