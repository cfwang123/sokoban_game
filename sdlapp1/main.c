/**
 * sdlapp1 — SDL2 推箱子桌面 demo（教学）
 * 编译见 readme（需 SDL2 开发库）。
 */
#include <SDL.h>
#include <stdio.h>
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
    int hist[MAX_HIST][5]; /* px,py,from_i,to_i,is_push */
    int hist_n;
} State;

static void load(State *s) {
    memset(s, 0, sizeof(*s));
    s->h = LEVEL_H;
    s->w = 0;
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
            s->hist[s->hist_n][0] = s->px;
            s->hist[s->hist_n][1] = s->py;
            s->hist[s->hist_n][2] = ny * s->w + nx;
            s->hist[s->hist_n][3] = by * s->w + bx;
            s->hist[s->hist_n][4] = 1;
            s->hist_n++;
        }
        s->boxes[ny][nx] = false;
        s->boxes[by][bx] = true;
        s->px = nx; s->py = ny;
        s->moves++;
        check_win(s);
        return true;
    }
    if (s->hist_n < MAX_HIST) {
        s->hist[s->hist_n][0] = s->px;
        s->hist[s->hist_n][1] = s->py;
        s->hist[s->hist_n][2] = -1;
        s->hist[s->hist_n][3] = -1;
        s->hist[s->hist_n][4] = 0;
        s->hist_n++;
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
        to = s->hist[s->hist_n][3];
        from = s->hist[s->hist_n][2];
        py = s->hist[s->hist_n][1];
        px = s->hist[s->hist_n][0];
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

static void draw(SDL_Renderer *r, State *s) {
    SDL_SetRenderDrawColor(r, 26, 26, 46, 255);
    SDL_RenderClear(r);
    for (int y = 0; y < s->h; y++) {
        for (int x = 0; x < s->w; x++) {
            SDL_Rect rc = { PAD + x * CELL, PAD + y * CELL, CELL, CELL };
            if (s->walls[y][x]) {
                SDL_SetRenderDrawColor(r, 74, 74, 106, 255);
                SDL_RenderFillRect(r, &rc);
            } else {
                SDL_SetRenderDrawColor(r, 58, 58, 85, 255);
                SDL_RenderFillRect(r, &rc);
                SDL_SetRenderDrawColor(r, 68, 68, 102, 255);
                SDL_RenderDrawRect(r, &rc);
            }
            if (s->goals[y][x]) {
                SDL_SetRenderDrawColor(r, 233, 69, 96, 255);
                int cx = rc.x + CELL / 2, cy = rc.y + CELL / 2;
                for (int dy = -4; dy <= 4; dy++)
                    for (int dx = -4; dx <= 4; dx++)
                        if (dx * dx + dy * dy <= 16)
                            SDL_RenderDrawPoint(r, cx + dx, cy + dy);
            }
            if (s->boxes[y][x]) {
                bool on = s->goals[y][x];
                SDL_SetRenderDrawColor(r, on ? 46 : 243, on ? 204 : 156, on ? 113 : 18, 255);
                SDL_Rect br = { rc.x + 4, rc.y + 4, CELL - 8, CELL - 8 };
                SDL_RenderFillRect(r, &br);
            }
            if (s->px == x && s->py == y) {
                SDL_SetRenderDrawColor(r, 52, 152, 219, 255);
                int cx = rc.x + CELL / 2, cy = rc.y + CELL / 2;
                for (int dy = -12; dy <= 12; dy++)
                    for (int dx = -12; dx <= 12; dx++)
                        if (dx * dx + dy * dy <= 144)
                            SDL_RenderDrawPoint(r, cx + dx, cy + dy);
            }
        }
    }
    SDL_RenderPresent(r);
}

int main(int argc, char **argv) {
    (void)argc; (void)argv;
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        fprintf(stderr, "SDL_Init: %s\n", SDL_GetError());
        return 1;
    }
    State st;
    load(&st);
    int ww = PAD * 2 + st.w * CELL;
    int wh = PAD * 2 + st.h * CELL;
    SDL_Window *win = SDL_CreateWindow("Sokoban SDL2",
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, ww, wh, 0);
    SDL_Renderer *ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED);
    if (!win || !ren) {
        fprintf(stderr, "SDL window/renderer failed\n");
        return 1;
    }
    bool running = true;
    while (running) {
        SDL_Event e;
        while (SDL_PollEvent(&e)) {
            if (e.type == SDL_QUIT) running = false;
            else if (e.type == SDL_KEYDOWN) {
                switch (e.key.keysym.sym) {
                case SDLK_w: case SDLK_UP: try_move(&st, 0, -1); break;
                case SDLK_s: case SDLK_DOWN: try_move(&st, 0, 1); break;
                case SDLK_a: case SDLK_LEFT: try_move(&st, -1, 0); break;
                case SDLK_d: case SDLK_RIGHT: try_move(&st, 1, 0); break;
                case SDLK_z: undo(&st); break;
                case SDLK_r: load(&st); break;
                case SDLK_q: case SDLK_ESCAPE: running = false; break;
                default: break;
                }
            }
        }
        draw(ren, &st);
        SDL_Delay(16);
    }
    SDL_DestroyRenderer(ren);
    SDL_DestroyWindow(win);
    SDL_Quit();
    return 0;
}
