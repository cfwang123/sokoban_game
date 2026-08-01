/* 自动生成：演示关卡表（文曲星工程） */
#ifndef WQX_LEVELS_DATA_H
#define WQX_LEVELS_DATA_H

#define WQX_LEVEL_COUNT 20

typedef struct {
    const char *name;
    const char *const *rows; /* NULL 结尾 */
    const char *solution;    /* 可为空串 */
} WqxLevel;

extern const WqxLevel g_wqx_levels[WQX_LEVEL_COUNT];

#endif
