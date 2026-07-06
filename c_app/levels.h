#ifndef LEVELS_H
#define LEVELS_H

/*
 * 关卡数据结构 + JSON 解析（用 cJSON 库）
 */

typedef struct {
    char  name[64];   /* 关卡名（ASCII） */
    char **puzzle;    /* 行字符串数组（堆分配） */
    int    rowCount;  /* 行数 */
    char  *solution;  /* U/D/L/R 字符串（堆分配，可能为空字符串） */
} Level;

typedef struct {
    Level *items;
    int    count;
} LevelSet;

/* 从 path 加载 levels.json，0=成功，非0=失败 */
int  levels_load(const char *path, LevelSet *out);

/* 释放 LevelSet 内所有堆内存 */
void levels_free(LevelSet *set);

#endif /* LEVELS_H */
