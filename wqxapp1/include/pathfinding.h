#ifndef WQX_PATHFINDING_H
#define WQX_PATHFINDING_H

#include "game.h"

/**
 * BFS 寻路。out_dirs 填 0..3 方向；返回路径长度；不可达 -1；已在目标 0。
 * 文曲星无触屏时，可用于「自动走到某格」菜单演示。
 */
int path_find(const GameState *s, int tx, int ty, int *out_dirs, int out_cap);

#endif
