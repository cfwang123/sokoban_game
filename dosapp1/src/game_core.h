#ifndef GAME_CORE_H
#define GAME_CORE_H

#define GC_MAX_W 16
#define GC_MAX_H 12
#define GC_MAX (GC_MAX_W * GC_MAX_H)

typedef struct {
  int w, h, px, py, moves, won, level;
  unsigned char walls[GC_MAX], goals[GC_MAX], boxes[GC_MAX];
} GameCore;

int gc_idx(const GameCore *s, int x, int y);
int gc_load(GameCore *s, int level_index); /* uses mini_levels.h */
int gc_try_move(GameCore *s, int dx, int dy);
int gc_undo(GameCore *s);

#endif
