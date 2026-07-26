#include "gba.h"
#include "game.h"
#include "gfx.h"
#include "sound.h"

int main(void)
{
	u16 prev = 0;
	u16 hold = 0;
	u8 hold_t = 0;

	gfx_init();
	sound_init();
	game_init();

	game_draw();
	vid_vsync();
	gfx_flip();

	for (;;) {
		u16 keys = key_poll();
		u16 pressed = (u16)(keys & ~prev);
		u16 dpad = keys & (KEY_UP | KEY_DOWN | KEY_LEFT | KEY_RIGHT);
		u16 dpad_press = 0;

		if (dpad) {
			if (pressed & dpad) {
				dpad_press = pressed & dpad;
				hold = dpad;
				hold_t = 0;
			} else if ((keys & hold) == hold && hold) {
				hold_t++;
				if (hold_t == 14 || (hold_t > 14 && (hold_t % 5) == 0))
					dpad_press = hold;
			}
		} else {
			hold = 0;
			hold_t = 0;
		}

		{
			u16 effective = pressed;
			if (g.state == ST_PLAY)
				effective = (u16)((pressed & ~(KEY_UP | KEY_DOWN | KEY_LEFT | KEY_RIGHT)) | dpad_press);
			game_update(keys, effective);
		}

		if (g.need_redraw) {
			game_draw();
			vid_vsync();
			gfx_flip();
		} else {
			vid_vsync();
		}

		prev = keys;
	}
	return 0;
}
