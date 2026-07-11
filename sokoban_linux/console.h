#ifndef CONSOLE_H
#define CONSOLE_H

#include <stddef.h>   /* wchar_t */

/*
 * 跨平台控制台封装：颜色 / 光标 / 输入
 * Windows: console_win.c  (Win32 Console API)
 * Linux:   console_linux.c (ncurses)
 */

/* ---- 跨平台按键虚拟码 ---- */
#ifdef _WIN32
/* Windows: 使用 windows.h 中已有的 VK_* 定义 */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#else
/* Linux: 自定义 VK_* 兼容码，console_linux.c 负责映射 */
#define VK_UP      0x1001
#define VK_DOWN    0x1002
#define VK_LEFT    0x1003
#define VK_RIGHT   0x1004
#define VK_F1      0x1005
#define VK_F2      0x1006
#define VK_SPACE   0x20
#define VK_RETURN  0x0D
#define VK_BACK    0x08
#define VK_ESCAPE  0x1B
#define VK_PRIOR   0x1007  /* PageUp */
#define VK_NEXT    0x1008  /* PageDown */
#endif

/* 一格显示单元：字符 + 颜色属性 (低4位前景, 高4位背景) */
typedef struct {
    wchar_t        ch;    /* Unicode 字符 */
    unsigned short attr;  /* 颜色属性 */
} Cell;

/* 事件类型 */
enum {
    EV_NONE = 0,    /* 超时无事件 */
    EV_KEY,         /* 键盘按下：k1=虚拟按键码, k2=UnicodeChar */
    EV_MOUSE,       /* 鼠标点击：mx,my=字符坐标 */
    EV_RESIZE,      /* 窗口大小改变 */
};

/* 初始化控制台 */
void con_init(void);

/* 还原控制台 */
void con_shutdown(void);

/* 清屏并把光标移到 (0,0) */
void con_clear(void);

/* 取控制台可见区尺寸（字符列/行） */
void con_get_size(int *w, int *h);

/*
 * 差异刷新：把 front 中与 back 不同的格子写入控制台，并同步更新 back。
 * w,h: 缓冲区尺寸；ox,oy: 在控制台中的起始偏移。
 * 若 back 为 NULL 或某格 attr==0xFFFF，视为"未知"强制写入。
 */
void con_present(const Cell *front, Cell *back, int w, int h, int ox, int oy);

/*
 * 读取一个输入事件，最多等待 waitMs 毫秒。
 * 输出参数：outType / k1 / k2 / mx / my（见 EV_* 枚举）
 * 返回 outType。
 */
int con_read_event(int *outType, int *k1, int *k2, int *mx, int *my, int waitMs);

/* 排空输入缓冲队列中所有未读事件 */
void con_flush_input(void);

/* 设置窗口标题 */
void con_set_title(const wchar_t *title);

/* 获取毫秒级时间戳（用于计时） */
unsigned long con_get_tick(void);

/*
 * 颜色属性常量（数值 = FG | BG，按 Win32 Console 颜色位定义）
 *   FG: bit0=蓝 bit1=绿 bit2=红 bit3=强度
 *   BG: bit4=蓝 bit5=绿 bit6=红 bit7=强度
 */
#define ATTR_WALL        0x87   /* 灰字 暗灰底  (#墙) */
#define ATTR_FLOOR       0x10   /* 黑字 深蓝底  (-地板) */
#define ATTR_GOAL        0x1C   /* 亮红字 深蓝底 (.目标) */
#define ATTR_BOX         0x16   /* 棕字 深蓝底 ($箱未到位) */
#define ATTR_BOX_GOAL    0x1A   /* 亮绿字 深蓝底 (*箱已到位) */
#define ATTR_PLAYER      0x1B   /* 亮青字 深蓝底 (@玩家) */
#define ATTR_PLAYER_GOAL 0x1D   /* 亮紫字 深蓝底 (+玩家在目标) */
#define ATTR_STATUSBAR   0x8F   /* 白字 暗灰底 (状态栏) */
#define ATTR_WINMSG      0x1D   /* 亮紫字 深蓝底 (过关提示) */

#endif /* CONSOLE_H */
