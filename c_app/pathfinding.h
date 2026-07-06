#ifndef PATHFINDING_H
#define PATHFINDING_H

#include "game.h"

/*
 * BFS 寻路：从玩家位置到 (targetX,targetY)，避开墙和箱子
 * 返回堆分配的方向字符数组 'U'/'D'/'L'/'R'，*outLen 为长度
 * 无路径返回 NULL
 * 调用者负责 free
 */
char *path_find(const GameState *s, int targetX, int targetY, int *outLen);

#endif /* PATHFINDING_H */
