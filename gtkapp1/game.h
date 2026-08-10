/* 与 x11app1 同接口（教学拷贝） */
#ifndef SOKOBAN_GAME_H
#define SOKOBAN_GAME_H

#define MAX_W 32
#define MAX_H 32
#define MAX_HIST 1024

typedef struct {
    int px, py, bfx, bfy, btx, bty, is_push;
} Hist;

typedef struct {
    char map[MAX_W][MAX_H];
    int width, height, px, py, moves, won, hist_n;
    Hist hist[MAX_HIST];
} GameState;

void game_from_rows(GameState *s, const char **rows, int n);
int game_try_move(GameState *s, int dx, int dy);
int game_undo(GameState *s);

#endif
