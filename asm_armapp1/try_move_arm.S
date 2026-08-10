@ try_move_arm.S — ARM32 教学骨架（AAPCS）
@ int sk_try_move(SkGame *g, int dx, int dy)
@   r0=g, r1=dx, r2=dy, 返回 r0
@ 完整玩法: ../asm_common/game.c

        .text
        .global sk_try_move_arm_demo
        .type sk_try_move_arm_demo, %function
sk_try_move_arm_demo:
        mov     r0, #0
        bx      lr
        .size sk_try_move_arm_demo, .-sk_try_move_arm_demo

@ 教学: 条件执行 (EQ/NE)、ldr/str、堆栈 stmfd/ldmfd
