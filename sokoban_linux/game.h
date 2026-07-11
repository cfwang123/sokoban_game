#ifndef GAME_H
#define GAME_H

#include "levels.h"

/*
 * 游戏状态与逻辑
 */

typedef struct { int x, y; } Pos;

typedef struct {
    int   w, h;            /* 关卡尺寸 */
    char *cells;           /* w*h 静态层：'#'墙 / '-'地板 / '.'目标 */
    Pos  *boxes;           /* 箱子位置数组 */
    int   nBoxes;
    Pos  *goals;           /* 目标位置数组 */
    int   nGoals;
    Pos   player;
    int   moves;
    int   won;
    int   levelIndex;

    /* 撤销历史：每条记录玩家位置 + 是否带箱子及箱子起止 */
    Pos  *histPlayer;       /* 移动前玩家位置 */
    Pos  *histBoxFrom;      /* 若有箱子，箱子移动前位置；否则未使用 */
    Pos  *histBoxTo;        /* 若有箱子，箱子移动后位置；否则未使用 */
    int  *histHadBox;       /* 1=此步推了箱子，0=纯移动 */
    int   histCount, histCap;
} GameState;

/* 从 Level 装载到 GameState（清空历史） */
void game_load(Level *lvl, int index, GameState *out);

/* 释放 GameState 内堆内存 */
void game_free(GameState *s);

/* 重置当前关（重新解析 levelIndex 对应的 Level） */
void game_reset(GameState *s, LevelSet *ls);

/* 尝试移动玩家；返回 1=移动了，0=没动 */
int  game_try_move(GameState *s, int dx, int dy);

/* 同 game_try_move 但不触发胜利检查（用于动画/寻路批量执行） */
int  game_try_move_instant(GameState *s, int dx, int dy);

/* 撤销：跳过纯移动步，回到上一个推箱动作前 */
void game_undo(GameState *s);

/* 检查并设置 won 标志 */
int  game_check_win(GameState *s);

/* 取 (x,y) 的合并显示字符：含箱子/玩家/目标 */
char game_cell_at(const GameState *s, int x, int y);

/* 工具：该格是否是箱子 */
int  game_is_box_at(const GameState *s, int x, int y);

/* 工具：该格是否是目标 */
int  game_is_goal_at(const GameState *s, int x, int y);

#endif /* GAME_H */
