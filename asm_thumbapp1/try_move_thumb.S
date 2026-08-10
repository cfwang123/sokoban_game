@ try_move_thumb.S — Thumb-2 教学骨架
@ .thumb / .thumb_func；指令 16/32 位混合
@ 完整玩法: ../asm_common/game.c

        .syntax unified
        .thumb
        .text
        .global sk_try_move_thumb_demo
        .thumb_func
sk_try_move_thumb_demo:
        movs    r0, #0
        bx      lr

@ 教学: Thumb 代码密度高，常用于 MCU；与 ARM 模式通过 bx 切换
