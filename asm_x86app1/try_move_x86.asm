; try_move_x86.asm — NASM IA-32 教学骨架（cdecl）
; int sk_try_move(SkGame *g, int dx, int dy)  — 栈传参
; [esp+4]=g [esp+8]=dx [esp+12]=dy
;
; 完整玩法: ../asm_common/game.c
; 汇编: nasm -f elf32 try_move_x86.asm

        global sk_try_move_x86_demo
        section .text
sk_try_move_x86_demo:
        xor     eax, eax        ; 返回 0：演示用
        ret

; 教学：cdecl 调用方清栈；ebx/esi/edi 需保存
