/* 终端主机：调用 sk_*（C 或汇编实现） */
#include "game.h"
#include <stdio.h>
#include <string.h>
#include <ctype.h>

int main(void)
{
    SkGame g;
    char buf[1024];
    char line[128];
    sk_reset(&g);
    printf("sokoban_asm — wasd 移动, z 撤销, r 重置, q 退出\n");
    printf("(C 或汇编 sk_try_move；见各 asm_*app1)\n");
    for (;;) {
        printf("\n");
        sk_render(&g, buf, (int)sizeof(buf));
        fputs(buf, stdout);
        printf("moves=%d%s\n> ", g.moves, g.won ? " WIN!" : "");
        if (!fgets(line, sizeof(line), stdin))
            break;
        if (line[0] == 0 || line[0] == '\n')
            continue;
        switch (tolower((unsigned char)line[0])) {
        case 'w': sk_try_move(&g, 0, -1); break;
        case 's': sk_try_move(&g, 0, 1); break;
        case 'a': sk_try_move(&g, -1, 0); break;
        case 'd': sk_try_move(&g, 1, 0); break;
        case 'z': sk_undo(&g); break;
        case 'r': sk_reset(&g); break;
        case 'q': return 0;
        default: break;
        }
        if (g.won)
            puts("Level clear!");
    }
    return 0;
}
