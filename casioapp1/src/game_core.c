#include "game_core.h"
#include "mini_levels.h"
#include <string.h>

#define HIST 256
static int hist[HIST];
static int hist_n;

static void hclear(void) { hist_n = 0; }
static void hpush(int a, int b, int c, int d, int e) {
  if (hist_n + 5 > HIST) {
    memmove(hist, hist + 5, (size_t)(hist_n - 5) * sizeof(int));
    hist_n -= 5;
  }
  hist[hist_n++] = a; hist[hist_n++] = b; hist[hist_n++] = c;
  hist[hist_n++] = d; hist[hist_n++] = e;
}

int gc_idx(const GameCore *s, int x, int y) { return y * s->w + x; }

int gc_load(GameCore *s, int level_index) {
  const MiniLevel *lv;
  int y, x, w = 0, h = 0;
  if (level_index < 0 || level_index >= MINI_LEVEL_COUNT) return -1;
  memset(s, 0, sizeof(*s));
  hclear();
  lv = &g_mini_levels[level_index];
  while (lv->rows[h]) {
    int len = (int)strlen(lv->rows[h]);
    if (len > w) w = len;
    h++;
  }
  if (w > GC_MAX_W) w = GC_MAX_W;
  if (h > GC_MAX_H) h = GC_MAX_H;
  s->w = w; s->h = h; s->level = level_index;
  for (y = 0; y < h; y++) {
    const char *row = lv->rows[y];
    for (x = 0; row[x] && x < w; x++) {
      int i = gc_idx(s, x, y);
      switch (row[x]) {
      case '#': s->walls[i] = 1; break;
      case '.': s->goals[i] = 1; break;
      case '$': s->boxes[i] = 1; break;
      case '*': s->boxes[i] = 1; s->goals[i] = 1; break;
      case '@': s->px = x; s->py = y; break;
      case '+': s->px = x; s->py = y; s->goals[i] = 1; break;
      }
    }
  }
  return 0;
}

static int inb(const GameCore *s, int x, int y) {
  return x >= 0 && y >= 0 && x < s->w && y < s->h;
}

static void check_win(GameCore *s) {
  int i, n = s->w * s->h;
  for (i = 0; i < n; i++) if (s->boxes[i] && !s->goals[i]) { s->won = 0; return; }
  s->won = 1;
}

int gc_try_move(GameCore *s, int dx, int dy) {
  int nx, ny, ni, bx, by, bi;
  if (s->won) return 0;
  nx = s->px + dx; ny = s->py + dy;
  if (!inb(s, nx, ny) || s->walls[gc_idx(s, nx, ny)]) return 0;
  ni = gc_idx(s, nx, ny);
  if (s->boxes[ni]) {
    bx = nx + dx; by = ny + dy;
    if (!inb(s, bx, by) || s->walls[gc_idx(s, bx, by)] || s->boxes[gc_idx(s, bx, by)]) return 0;
    bi = gc_idx(s, bx, by);
    hpush(s->px, s->py, ni, bi, 1);
    s->boxes[ni] = 0; s->boxes[bi] = 1;
    s->px = nx; s->py = ny; s->moves++; check_win(s); return 1;
  }
  hpush(s->px, s->py, -1, -1, 0);
  s->px = nx; s->py = ny; return 1;
}

int gc_undo(GameCore *s) {
  int is_push = 0, from = -1, to = -1, px, py;
  if (s->won || hist_n < 5) return 0;
  px = s->px; py = s->py;
  while (hist_n >= 5) {
    is_push = hist[--hist_n]; to = hist[--hist_n]; from = hist[--hist_n];
    py = hist[--hist_n]; px = hist[--hist_n];
    if (is_push) break;
    s->px = px; s->py = py;
  }
  if (!is_push || from < 0) return 1;
  s->px = px; s->py = py;
  s->boxes[to] = 0; s->boxes[from] = 1;
  if (s->moves > 0) s->moves--;
  s->won = 0; return 1;
}
