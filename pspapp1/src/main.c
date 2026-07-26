/*
 * Sokoban — PSP homebrew
 * Build with pspdev → EBOOT.PBP (same pipeline as starstrike)
 */
#include <pspuser.h>
#include <pspkernel.h>

#include "gfx.h"
#include "game.h"

PSP_MODULE_INFO("Sokoban", 0, 1, 0);
PSP_MAIN_THREAD_ATTR(THREAD_ATTR_USER | THREAD_ATTR_VFPU);
PSP_HEAP_SIZE_KB(-256);

static int exit_request = 0;

static int exit_callback(int arg1, int arg2, void *common)
{
    (void)arg1;
    (void)arg2;
    (void)common;
    exit_request = 1;
    return 0;
}

static int callback_thread(SceSize args, void *argp)
{
    int cbid;
    (void)args;
    (void)argp;
    cbid = sceKernelCreateCallback("Exit Callback", exit_callback, NULL);
    sceKernelRegisterExitCallback(cbid);
    sceKernelSleepThreadCB();
    return 0;
}

static int setup_callbacks(void)
{
    int thid = sceKernelCreateThread("update_thread", callback_thread, 0x11, 0xFA0, 0, 0);
    if (thid >= 0)
        sceKernelStartThread(thid, 0, 0);
    return thid;
}

int main(int argc, char *argv[])
{
    (void)argc;
    (void)argv;

    setup_callbacks();
    gfx_init();
    game_init();

    while (!exit_request && game_running()) {
        game_update();
        game_draw();
    }

    gfx_shutdown();
    sceKernelExitGame();
    return 0;
}
