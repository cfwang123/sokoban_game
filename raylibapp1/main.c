/**
 * raylibapp1 — raylib 推箱子桌面 demo（教学）
 * 需 raylib：https://www.raylib.com/
 */
#include "raylib.h"
#include <string.h>
#include <stdbool.h>

#define CELL 40
#define PAD 20
#define MAX_W 32
#define MAX_H 32
#define MAX_HIST 256

static const char *LEVEL[] = {
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
};
static const int LEVEL_H = 7;

typedef struct {
    int w, h, px, py, moves;
    bool won;
    bool walls[MAX_H][MAX_W];
    bool goals[MAX_H][MAX_W];
    bool boxes[MAX_H][MAX_W];
    int hist[MAX_HIST][5];
    int hist_n;
} State;

static void load(State *s) {
    memset(s, 0, sizeof(*s));
    s->h = LEVEL_H;
    for (int y = 0; y < LEVEL_H; y++) {
        int len = (int)strlen(LEVEL[y]);
        if (len > s->w) s->w = len;
        for (int x = 0; x < len; x++) {
            char ch = LEVEL[y][x];
            if (ch == '#') s->walls[y][x] = true;
            else if (ch == '.') s->goals[y][x] = true;
            else if (ch == '$') s->boxes[y][x] = true;
            else if (ch == '*') { s->boxes[y][x] = true; s->goals[y][x] = true; }
            else if (ch == '@') { s->px = x; s->py = y; }
            else if (ch == '+') { s->px = x; s->py = y; s->goals[y][x] = true; }
        }
    }
}

static void check_win(State *s) {
    for (int y = 0; y < s->h; y++)
        for (int x = 0; x < s->w; x++)
            if (s->boxes[y][x] && !s->goals[y][x]) { s->won = false; return; }
    s->won = true;
}

static bool try_move(State *s, int dx, int dy) {
    if (s->won) return false;
    int nx = s->px + dx, ny = s->py + dy;
    if (nx < 0 || ny < 0 || nx >= s->w || ny >= s->h || s->walls[ny][nx]) return false;
    if (s->boxes[ny][nx]) {
        int bx = nx + dx, by = ny + dy;
        if (bx < 0 || by < 0 || bx >= s->w || by >= s->h || s->walls[by][bx] || s->boxes[by][bx])
            return false;
        if (s->hist_n < MAX_HIST) {
            s->hist[s->hist_n][0] = s->px; s->hist[s->hist_n][1] = s->py;
            s->hist[s->hist_n][2] = ny * s->w + nx; s->hist[s->hist_n][3] = by * s->w + bx;
            s->hist[s->hist_n][4] = 1; s->hist_n++;
        }
        s->boxes[ny][nx] = false; s->boxes[by][bx] = true;
        s->px = nx; s->py = ny; s->moves++; check_win(s);
        return true;
    }
    if (s->hist_n < MAX_HIST) {
        s->hist[s->hist_n][0] = s->px; s->hist[s->hist_n][1] = s->py;
        s->hist[s->hist_n][2] = -1; s->hist[s->hist_n][3] = -1;
        s->hist[s->hist_n][4] = 0; s->hist_n++;
    }
    s->px = nx; s->py = ny;
    return true;
}

static void undo(State *s) {
    if (s->won || s->hist_n == 0) return;
    int is_push = 0, from = -1, to = -1, px = s->px, py = s->py;
    while (s->hist_n > 0) {
        s->hist_n--;
        is_push = s->hist[s->hist_n][4];
        to = s->hist[s->hist_n][3]; from = s->hist[s->hist_n][2];
        py = s->hist[s->hist_n][1]; px = s->hist[s->hist_n][0];
        if (is_push) break;
        s->px = px; s->py = py;
    }
    if (!is_push || from < 0) return;
    s->px = px; s->py = py;
    s->boxes[to / s->w][to % s->w] = false;
    s->boxes[from / s->w][from % s->w] = true;
    if (s->moves > 0) s->moves--;
    s->won = false;
}

int main(void) {
    State st;
    load(&st);
    int ww = PAD * 2 + st.w * CELL;
    int wh = PAD * 2 + st.h * CELL + 28;
    InitWindow(ww, wh, "Sokoban raylib");
    SetTargetFPS(60);
    Color bg = { 26, 26, 46, 255 };
    while (!WindowShouldClose()) {
        if (IsKeyPressed(KEY_W) || IsKeyPressed(KEY_UP)) try_move(&st, 0, -1);
        if (IsKeyPressed(KEY_S) || IsKeyPressed(KEY_DOWN)) try_move(&st, 0, 1);
        if (IsKeyPressed(KEY_A) || IsKeyPressed(KEY_LEFT)) try_move(&st, -1, 0);
        if (IsKeyPressed(KEY_D) || IsKeyPressed(KEY_RIGHT)) try_move(&st, 1, 0);
        if (IsKeyPressed(KEY_Z)) undo(&st);
        if (IsKeyPressed(KEY_R)) load(&st);
        if (IsKeyPressed(KEY_Q)) break;

        BeginDrawing();
        ClearBackground(bg);
        for (int y = 0; y < st.h; y++) {
            for (int x = 0; x < st.w; x++) {
                int px = PAD + x * CELL, py = PAD + y * CELL;
                if (st.walls[y][x]) DrawRectangle(px, py, CELL, CELL, (Color){74, 74, 106, 255});
                else {
                    DrawRectangle(px, py, CELL, CELL, (Color){58, 58, 85, 255});
                    DrawRectangleLines(px, py, CELL, CELL, (Color){68, 68, 102, 255});
                }
                if (st.goals[y][x])
                    DrawCircle(px + CELL / 2, py + CELL / 2, 6, (Color){233, 69, 96, 255});
                if (st.boxes[y][x]) {
                    bool on = st.goals[y][x];
                    DrawRectangle(px + 4, py + 4, CELL - 8, CELL - 8,
                        on ? (Color){46, 204, 113, 255} : (Color){243, 156, 18, 255});
                }
                if (st.px == x && st.py == y)
                    DrawCircle(px + CELL / 2, py + CELL / 2, CELL * 0.35f, (Color){52, 152, 219, 255});
            }
        }
        DrawText(TextFormat("moves=%d%s  WASD Z R Q", st.moves, st.won ? " WIN" : ""),
                 8, wh - 24, 16, RAYWHITE);
        EndDrawing();
    }
    CloseWindow();
    return 0;
}
