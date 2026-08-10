# try_move_loongarch.S — LoongArch64 教学骨架
# 国产 ISA；调用约定类似 RISC 风格（a0–a7 传参）
# 完整玩法: ../asm_common/game.c

        .text
        .globl sk_try_move_loongarch_demo
sk_try_move_loongarch_demo:
        li.w    $a0, 0
        jr      $ra

# 教学: 与 MIPS 历史渊源、新编码空间
