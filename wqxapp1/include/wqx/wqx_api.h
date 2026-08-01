/**
 * @file wqx_api.h
 * @brief 步步高文曲星（WQX）类电子词典 — 教学用 HAL 接口
 *
 * ---------------------------------------------------------------------------
 * 说明（请先读）
 * ---------------------------------------------------------------------------
 * 1. 文曲星各代机型（PC / TC / E 系列等）官方 SDK、分辨率、键值并不统一。
 * 2. 本头文件抽象的是「电子词典上写 C 小游戏时常见能力」：
 *    点阵屏绘制、按键轮询、简易定时、Flash/EEPROM 小存档。
 * 3. 真机开发时：把本接口映射到厂商 SDK（或社区移植层）；
 *    本仓库只演示工程拆分与调用方式，不绑定某一已失传的商业 SDK 路径。
 * 4. 对照其它移植：
 *    - Android View/Canvas  → wqx_draw_*
 *    - Java ME keyPressed   → wqx_key_poll / WQX_KEY_*
 *    - SharedPreferences    → wqx_nv_load/save
 *
 * 典型机型示意（教学，非严格规格）：
 *    - 分辨率常见 160x160 / 240x160 / 320x240 灰阶或单色
 *    - 输入：方向键、确认、退出、数字键或快捷键
 *    - 资源：程序体积与 RAM 都很紧，关卡宜编译进固件
 */

#ifndef WQX_API_H
#define WQX_API_H

#ifdef __cplusplus
extern "C" {
#endif

/* ---- 屏参数：演示工程按 240x160 灰阶逻辑坐标设计，真机可缩放 ---- */
#define WQX_LCD_W 240
#define WQX_LCD_H 160

/* 灰度：0=白/浅底，15=黑（文曲星多为单色/少灰阶，这里用 0..15 便于演示） */
typedef unsigned char wqx_gray_t;

/* 按键位掩码（一次 poll 可组合） */
#define WQX_KEY_UP (1u << 0)
#define WQX_KEY_DOWN (1u << 1)
#define WQX_KEY_LEFT (1u << 2)
#define WQX_KEY_RIGHT (1u << 3)
#define WQX_KEY_OK (1u << 4) /* 确认 / 中键 */
#define WQX_KEY_ESC (1u << 5) /* 退出 / 返回 */
#define WQX_KEY_UNDO (1u << 6) /* 撤销，可映射「返回」长按或独立键 */
#define WQX_KEY_RESET (1u << 7)
#define WQX_KEY_PREV (1u << 8)
#define WQX_KEY_NEXT (1u << 9)
#define WQX_KEY_ANSWER (1u << 10)
#define WQX_KEY_MENU (1u << 11)

/**
 * 系统初始化（开显存、时钟、键扫描）。
 * 真机：对应 SDK 的 app_main 前准备；失败返回非 0。
 */
int wqx_init(void);

/** 退出前释放资源。 */
void wqx_shutdown(void);

/** 清屏为指定灰度。 */
void wqx_clear(wqx_gray_t g);

/** 刷新：把后台缓冲提交到 LCD（部分机型需要显式 flush）。 */
void wqx_flush(void);

/** 画实心矩形。 */
void wqx_fill_rect(int x, int y, int w, int h, wqx_gray_t g);

/** 画矩形边框。 */
void wqx_draw_rect(int x, int y, int w, int h, wqx_gray_t g);

/** 画圆/椭圆近似（目标点、玩家）。 */
void wqx_fill_circle(int cx, int cy, int r, wqx_gray_t g);

/**
 * 点阵字：ASCII/数字简单 6x8 字模（教学用）。
 * 中文机型真机应改用字库 API；此处仅保证「第 n 关」「步数」可显示。
 */
void wqx_draw_text(int x, int y, const char *ascii, wqx_gray_t g);

/** 毫秒级延时（忙等或系统 tick）。 */
void wqx_delay_ms(unsigned ms);

/** 读取当前按键状态（电平/去抖后的位掩码）。 */
unsigned wqx_key_poll(void);

/**
 * 边沿检测辅助：返回「本帧新按下」的键。
 * 实现里应保存上一帧状态；教学 stub 在 wqx_hal_stub.c。
 */
unsigned wqx_key_pressed(void);

/**
 * 非易失小存档（上次关卡号等）。
 * 真机：Flash 扇区 / EEPROM / 厂商「用户参数区」。
 */
int wqx_nv_load_u8(unsigned id, unsigned char *out);
int wqx_nv_save_u8(unsigned id, unsigned char value);

#define WQX_NV_LAST_LEVEL 1

#ifdef __cplusplus
}
#endif

#endif /* WQX_API_H */
