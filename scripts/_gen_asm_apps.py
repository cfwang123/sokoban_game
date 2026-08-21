#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate asm_*app1 teaching folders with ISA-specific try_move notes + readme."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (dir, title, tool, notes, try_move_filename, try_move_body)
ARCHS = []


def add(dir_name, title, tools, body_file, body, extra_readme=""):
    ARCHS.append((dir_name, title, tools, body_file, body, extra_readme))


# --- x86-64 System V (GAS) ---
add(
    "asm_x64app1",
    "x86-64 (AMD64) System V",
    "gcc / as / gas（Linux/macOS/WSL）；Windows 可用 MinGW",
    "try_move_x64.s",
    r"""# try_move_x64.s — 教学：x86-64 System V ABI 版 sk_try_move 骨架
# 完整可玩逻辑见 ../asm_common/game.c；本文件演示寄存器约定与控制流。
#
# ABI: int sk_try_move(SkGame *g, int dx, int dy)
#   rdi = g, esi = dx, edx = dy, 返回 eax
#
# SkGame 布局（与 game.h 一致，教学用偏移）:
#   0: map[32*32]
#   1024: width, height, px, py, moves, won, hist_n ...
#
# 汇编（Linux）:
#   as --64 -o try_move_x64.o try_move_x64.s
# 链接参考（需自行导出完整符号时）:
#   默认请用: cc ../asm_common/host_main.c ../asm_common/game.c

        .text
        .globl  sk_try_move_x64_demo
        .type   sk_try_move_x64_demo, @function
# 演示：仅返回 0（未修改状态）。真正玩法用 C 实现。
sk_try_move_x64_demo:
        xorl    %eax, %eax
        ret
        .size   sk_try_move_x64_demo, .-sk_try_move_x64_demo

# --- 教学伪代码对应 C sk_try_move ---
# if (g->won) return 0;
# nx = g->px + dx; ny = g->py + dy;
# ch = map[ny][nx];
# if (ch == '#') return 0;
# if (ch == '$' || ch == '*') { /* 推箱 */ ... }
# /* 走路 */ g->px = nx; g->py = ny; return 1;
""",
    """## 寄存器速查（System V AMD64）

| 用途 | 寄存器 |
|------|--------|
| 第 1–6 参数 | rdi, rsi, rdx, rcx, r8, r9 |
| 返回值 | rax |
| 被调用者保存 | rbx, rbp, r12–r15 |
| 栈 | rsp 16 字节对齐 |

可选本机可玩（C 参考）:

```bash
cc -O2 -o sokoban ../asm_common/host_main.c ../asm_common/game.c
./sokoban
```
""",
)

add(
    "asm_x86app1",
    "x86 (IA-32)",
    "nasm / gas i386；`as --32` 或 `nasm -f elf32`",
    "try_move_x86.asm",
    r"""; try_move_x86.asm — NASM IA-32 教学骨架（cdecl）
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
""",
    """## 寄存器速查（IA-32 cdecl）

| 用途 | 寄存器 |
|------|--------|
| 参数 | 栈上推入 |
| 返回 | eax |
| 需保存 | ebx, esi, edi, ebp |

```bash
cc -O2 -o sokoban ../asm_common/host_main.c ../asm_common/game.c
./sokoban
```
""",
)

add(
    "asm_armapp1",
    "ARM32 (AArch32 ARM 模式)",
    "arm-linux-gnueabihf-as / arm-none-eabi-as",
    "try_move_arm.S",
    r"""@ try_move_arm.S — ARM32 教学骨架（AAPCS）
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
""",
    """## 寄存器速查（AAPCS）

| 用途 | 寄存器 |
|------|--------|
| 参数 | r0–r3 |
| 返回 | r0 |
| 需保存 | r4–r11, lr |

```bash
cc -O2 -o sokoban ../asm_common/host_main.c ../asm_common/game.c
```
""",
)

add(
    "asm_thumbapp1",
    "ARM Thumb / Thumb-2",
    "arm-none-eabi-as -mthumb；或 clang --target=arm-none-eabi -mthumb",
    "try_move_thumb.S",
    r"""@ try_move_thumb.S — Thumb-2 教学骨架
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
""",
    """## Thumb 要点

- 入口需 `.thumb_func` 保证 LSB 正确
- Cortex-M 仅 Thumb-2
- 与 `asm_armapp1` 对照同一算法的两种编码

```bash
cc -O2 -o sokoban ../asm_common/host_main.c ../asm_common/game.c
```
""",
)

add(
    "asm_riscvapp1",
    "RISC-V (RV32/RV64)",
    "riscv64-unknown-elf-as / clang --target=riscv64",
    "try_move_riscv.S",
    r"""# try_move_riscv.S — RISC-V 教学骨架（RV64I / ILP32 类似）
# int sk_try_move(SkGame *g, int dx, int dy)
#   a0=g, a1=dx, a2=dy, 返回 a0
# 完整玩法: ../asm_common/game.c

        .text
        .globl sk_try_move_riscv_demo
sk_try_move_riscv_demo:
        li      a0, 0
        ret

# 教学: 固定 32 寄存器、load-store、无条件码（用分支）
""",
    """## 寄存器速查（RISC-V 调用约定）

| 用途 | 寄存器 |
|------|--------|
| 参数 | a0–a7 |
| 返回 | a0 |
| 需保存 | s0–s11 |
| 返回地址 | ra |

```bash
cc -O2 -o sokoban ../asm_common/host_main.c ../asm_common/game.c
```
""",
)

add(
    "asm_mipsapp1",
    "MIPS32",
    "mips-linux-gnu-as / spim / mars（模拟器）",
    "try_move_mips.S",
    r"""# try_move_mips.S — MIPS 教学骨架（o32）
# int sk_try_move(SkGame *g, int dx, int dy)
#   a0=g, a1=dx, a2=dy, 返回 v0
# 完整玩法: ../asm_common/game.c

        .text
        .globl sk_try_move_mips_demo
sk_try_move_mips_demo:
        move    $v0, $zero
        jr      $ra
        nop                 # 延迟槽

# 教学: 分支延迟槽、$t/$s 寄存器、HI/LO 乘除
""",
    """## 寄存器速查（o32）

| 用途 | 寄存器 |
|------|--------|
| 参数 | $a0–$a3 |
| 返回 | $v0, $v1 |
| 需保存 | $s0–$s7 |
| 返回地址 | $ra |

可用 MARS/SPIM 学习指令；完整游戏用 C 参考。
""",
)

add(
    "asm_ppcapp1",
    "PowerPC / Power ISA",
    "powerpc-linux-gnu-as / IBM XL",
    "try_move_ppc.S",
    r"""# try_move_ppc.S — PowerPC 教学骨架
# int sk_try_move(SkGame *g, int dx, int dy)
#   r3=g, r4=dx, r5=dy, 返回 r3
# 完整玩法: ../asm_common/game.c

        .text
        .globl sk_try_move_ppc_demo
sk_try_move_ppc_demo:
        li      3, 0
        blr

# 教学: 条件寄存器 CR、链接寄存器 LR、r0 特殊
""",
    """## 寄存器速查（Power ABI 概要）

| 用途 | 寄存器 |
|------|--------|
| 参数 | r3–r10 |
| 返回 | r3 |
| 链接 | lr |

常见于旧 Mac、部分嵌入式与游戏主机历史资料。
""",
)

add(
    "asm_avrapp1",
    "AVR (8-bit MCU)",
    "avr-as / avr-gcc",
    "try_move_avr.S",
    r"""; try_move_avr.S — AVR 教学骨架（ATmega 风格）
; 8 位寄存器 r0–r31；参数多通过寄存器对传递
; 完整玩法: ../asm_common/game.c（主机侧）
; 本文件演示推箱判定伪指令序列

        .global sk_try_move_avr_demo
sk_try_move_avr_demo:
        clr     r24           ; 返回 0 (16-bit 在 r25:r24)
        clr     r25
        ret

; 教学: X/Y/Z 指针寄存器、SREG 状态、Harvard 架构
""",
    """## AVR 要点

- Arduino 底层即 AVR 汇编友好
- 数据/程序空间分离
- 适合对照 `arduinoapp1` 教学

主机可玩：

```bash
cc -O2 -o sokoban ../asm_common/host_main.c ../asm_common/game.c
```
""",
)

add(
    "asm_z80app1",
    "Z80",
    "z80-asm / sjasmplus / Pasmo；或在线模拟器",
    "try_move_z80.asm",
    r"""; try_move_z80.asm — Z80 教学骨架
; 8 位经典机（Spectrum、Game Boy 前身相关生态）
; 完整玩法算法见 ../asm_common/game.c
;
; HL = game 指针（教学假设）
; DE = dx,dy 打包等 — 具体由宿主约定

        PUBLIC sk_try_move_z80_demo
sk_try_move_z80_demo:
        ld      a, 0
        ret

; 教学: AF/BC/DE/HL、影子寄存器、IX/IY
""",
    """## Z80 要点

- 广泛用于 8 位家用机与计算器
- 与 8080 兼容子集
- 完整交互需模拟器；逻辑对照 C 参考
""",
)

add(
    "asm_6502app1",
    "6502 / 65C02",
    "ca65 / nesasm / VICE 等",
    "try_move_6502.s",
    r"""; try_move_6502.s — 6502 教学骨架（ca65 语法风格）
; 与仓库 fcapp1（NES）同源生态
; 完整玩法见 ../asm_common/game.c 与 ../fcapp1

        .export sk_try_move_6502_demo
sk_try_move_6502_demo:
        lda #0
        rts

; 教学: A/X/Y、零页、绝对/间接寻址、无乘除指令
; 推箱状态宜放零页: player_x, player_y, ...
""",
    """## 6502 要点

- NES、Apple II、C64 等
- 本仓库已有可运行 NES 版：[`../fcapp1`](../fcapp1)
- 本目录强调**纯汇编教学片段**与寻址方式

```bash
cc -O2 -o sokoban ../asm_common/host_main.c ../asm_common/game.c
```
""",
)

add(
    "asm_aarch64app1",
    "AArch64 (ARM64)",
    "aarch64-linux-gnu-as / clang",
    "try_move_aarch64.S",
    r"""// try_move_aarch64.S — AArch64 教学骨架
// int sk_try_move(SkGame *g, int dx, int dy)
//   x0=g, w1=dx, w2=dy, 返回 w0
// 完整玩法: ../asm_common/game.c

        .text
        .global sk_try_move_aarch64_demo
sk_try_move_aarch64_demo:
        mov     w0, #0
        ret

// 教学: 31 个 64 位通用寄存器、W 寄存器 32 位视图、SP/XZR
""",
    """## 寄存器速查（AAPCS64）

| 用途 | 寄存器 |
|------|--------|
| 参数 | x0–x7 |
| 返回 | x0 |
| 需保存 | x19–x28 |
| 链接 | x30 (lr) |

Apple Silicon / 现代 Android 手机主力 ISA。
""",
)

add(
    "asm_loongarchapp1",
    "LoongArch（龙芯）",
    "loongarch64-unknown-linux-gnu-as / 龙芯工具链",
    "try_move_loongarch.S",
    r"""# try_move_loongarch.S — LoongArch64 教学骨架
# 国产 ISA；调用约定类似 RISC 风格（a0–a7 传参）
# 完整玩法: ../asm_common/game.c

        .text
        .globl sk_try_move_loongarch_demo
sk_try_move_loongarch_demo:
        li.w    $a0, 0
        jr      $ra

# 教学: 与 MIPS 历史渊源、新编码空间
""",
    """## LoongArch 要点

- 龙芯自主指令集
- Linux 主线已支持
- 对照 RISC-V / MIPS 学习调用约定差异
""",
)


def write_arch(dir_name, title, tools, body_file, body, extra):
    d = ROOT / dir_name
    d.mkdir(parents=True, exist_ok=True)
    (d / body_file).write_text(body.strip() + "\n", encoding="utf-8")
    readme = f"""# {dir_name} — {title} 推箱子汇编教学

**不强制在本仓库交叉编译**。完整可玩逻辑见 [`../asm_common`](../asm_common)（C 参考）。

## 工具

{tools}

## 本目录

| 文件 | 说明 |
|------|------|
| `{body_file}` | 该 ISA 下 `try_move` **教学骨架 / 寄存器约定** |
| 可玩主机 | `../asm_common/host_main.c` + `game.c` |

{extra}

## 算法对照

推箱 `try_move` 核心步骤（各 ISA 汇编应实现同一语义）：

1. 若已胜利则失败  
2. 计算 `nx,ny`；越界或墙则失败  
3. 若是箱子：检查前方；推箱并记 hist；`moves++`；判胜  
4. 否则走路并记 hist  

键位（C 主机）：WASD / z / r / q。
"""
    (d / "README.md").write_text(readme, encoding="utf-8")
    (d / "CHANGELOG.md").write_text(
        f"""# Changelog

## 1.0.0 — 2026-08-10

- 初版 {title} 汇编教学骨架 + 指向 asm_common 可玩实现
""",
        encoding="utf-8",
    )
    # thin Makefile
    (d / "Makefile").write_text(
        f"""# 默认构建 C 参考实现（无需交叉汇编器）
CC ?= cc
CFLAGS ?= -O2 -Wall
COMMON = ../asm_common

.PHONY: all run clean
all: sokoban
sokoban: $(COMMON)/host_main.c $(COMMON)/game.c $(COMMON)/game.h
\t$(CC) $(CFLAGS) -o sokoban $(COMMON)/host_main.c $(COMMON)/game.c -I$(COMMON)

run: sokoban
\t./sokoban

clean:
\trm -f sokoban *.o
""",
        encoding="utf-8",
    )
    print("wrote", dir_name)


def main():
    for a in ARCHS:
        write_arch(*a)
    print("done", len(ARCHS), "asm apps")


if __name__ == "__main__":
    main()
