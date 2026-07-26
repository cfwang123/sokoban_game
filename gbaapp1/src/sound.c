#include "sound.h"
#include "gba.h"

void sound_init(void)
{
	REG_SOUNDCNT_X = 0x0080; /* master enable */
	REG_SOUNDCNT_L = 0xFF77;
	REG_SOUNDCNT_H = 0x0002;
	REG_SOUNDBIAS = 0x200;
}

static void beep(u16 rate, u16 duty_len, u16 env)
{
	REG_SOUND1CNT_L = 0x0000;
	REG_SOUND1CNT_H = env | duty_len;
	REG_SOUND1CNT_X = rate | 0x8000;
}

void sfx_move(void) { beep(0x700 | 0x0400, 0x80, 0xF200); }
void sfx_push(void) { beep(0x500 | 0x0300, 0x80, 0xF400); }
void sfx_block(void) { beep(0x200 | 0x0100, 0xC0, 0xF100); }
void sfx_undo(void) { beep(0x600 | 0x0500, 0x40, 0xF200); }
void sfx_win(void) { beep(0x7C0 | 0x0600, 0x80, 0xF700); }
void sfx_menu(void) { beep(0x680 | 0x0400, 0x40, 0xF200); }
