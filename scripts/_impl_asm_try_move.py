#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Emit full sk_try_move sources for each asm_*app1 ISA (mirrors game.c)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def w(rel: str, text: str) -> None:
    p = ROOT / rel
    p.write_text(text.replace("\r\n", "\n"), encoding="utf-8")
    print("wrote", rel)


# ─── x86 NASM cdecl ──────────────────────────────────────────────────────────
w(
    "asm_x86app1/try_move_x86.asm",
    r"""; try_move_x86.asm — full sk_try_move (NASM, IA-32 cdecl)
; int sk_try_move(SkGame *g, int dx, int dy)
;   [esp+4]=g [esp+8]=dx [esp+12]=dy → eax
; Layout: ../asm_common/game.h  (map stride 32)
; nasm -f elf32 try_move_x86.asm   OR  nasm -f win32 try_move_x86.asm

        global  sk_try_move
        section .text

sk_try_move:
        push    ebp
        mov     ebp, esp
        push    ebx
        push    esi
        push    edi

        mov     esi, [ebp+8]            ; g
        cmp     dword [esi+1044], 0
        jne     .fail

        mov     eax, [esi+1032]
        add     eax, [ebp+12]
        mov     edi, eax                ; nx
        mov     eax, [esi+1036]
        add     eax, [ebp+16]
        mov     ebx, eax                ; ny

        ; at(nx,ny) → al
        mov     eax, edi
        mov     edx, ebx
        call    .at
        cmp     al, '#'
        je      .fail
        cmp     al, '$'
        je      .push
        cmp     al, '*'
        je      .push

        cmp     dword [esi+1048], 256
        jge     .fail
        mov     eax, [esi+1048]
        imul    eax, 28
        lea     eax, [esi+1052+eax]
        mov     edx, [esi+1032]
        mov     [eax], edx
        mov     edx, [esi+1036]
        mov     [eax+4], edx
        mov     dword [eax+24], 0
        inc     dword [esi+1048]
        mov     [esi+1032], edi
        mov     [esi+1036], ebx
        mov     eax, 1
        jmp     .done

.push:
        mov     ecx, edi
        add     ecx, [ebp+12]           ; bx
        mov     edx, ebx
        add     edx, [ebp+16]           ; by
        push    edx
        push    ecx
        mov     eax, ecx
        ; at(bx,by)
        push    edx
        push    ecx
        call    .at
        add     esp, 8
        pop     ecx                     ; bx
        pop     edx                     ; by
        cmp     al, '#'
        je      .fail
        cmp     al, '$'
        je      .fail
        cmp     al, '*'
        je      .fail
        cmp     dword [esi+1048], 256
        jge     .fail

        push    edx                     ; by
        push    ecx                     ; bx
        mov     eax, [esi+1048]
        imul    eax, 28
        lea     eax, [esi+1052+eax]
        mov     edx, [esi+1032]
        mov     [eax], edx
        mov     edx, [esi+1036]
        mov     [eax+4], edx
        mov     [eax+8], edi            ; bfx=nx
        mov     [eax+12], ebx
        pop     ecx
        pop     edx
        mov     [eax+16], ecx
        mov     [eax+20], edx
        mov     dword [eax+24], 1
        inc     dword [esi+1048]
        push    edx
        push    ecx

        ; clear box cell
        mov     eax, edi
        mov     edx, ebx
        call    .at
        cmp     al, '*'
        mov     al, '.'
        je      .c1
        mov     al, ' '
.c1:    movzx   eax, al
        push    eax
        push    ebx
        push    edi
        call    .set
        add     esp, 12

        pop     ecx                     ; bx
        pop     edx                     ; by
        push    edx
        push    ecx
        mov     eax, ecx
        ; place
        push    edx
        push    ecx
        call    .at
        add     esp, 8
        cmp     al, '.'
        mov     al, '*'
        je      .c2
        mov     al, '$'
.c2:    movzx   eax, al
        pop     ecx
        pop     edx
        push    eax
        push    edx
        push    ecx
        call    .set
        add     esp, 12

        mov     [esi+1032], edi
        mov     [esi+1036], ebx
        inc     dword [esi+1040]
        call    .check_win
        mov     eax, 1
        jmp     .done

.fail:  xor     eax, eax
.done:  pop     edi
        pop     esi
        pop     ebx
        pop     ebp
        ret

; at: eax=x edx=y, esi=g → al
.at:    cmp     eax, 0
        jl      .wall
        cmp     edx, 0
        jl      .wall
        cmp     eax, [esi+1024]
        jge     .wall
        cmp     edx, [esi+1028]
        jge     .wall
        shl     edx, 5
        add     edx, eax
        mov     al, [esi+edx]
        ret
.wall:  mov     al, '#'
        ret

; set: [esp+4]=x [esp+8]=y [esp+12]=c
.set:   mov     eax, [esp+4]
        mov     edx, [esp+8]
        mov     ecx, [esp+12]
        shl     edx, 5
        add     edx, eax
        mov     [esi+edx], cl
        ret

.check_win:
        mov     dword [esi+1044], 1
        xor     edx, edx
.cy:    cmp     edx, [esi+1028]
        jge     .cwd
        xor     eax, eax
.cx:    cmp     eax, [esi+1024]
        jge     .cxd
        mov     ecx, edx
        shl     ecx, 5
        add     ecx, eax
        cmp     byte [esi+ecx], '$'
        jne     .n1
        mov     dword [esi+1044], 0
.n1:    inc     eax
        jmp     .cx
.cxd:   inc     edx
        jmp     .cy
.cwd:   ret
""",
)

# ─── AArch64 ─────────────────────────────────────────────────────────────────
w(
    "asm_aarch64app1/try_move_aarch64.S",
    r"""// try_move_aarch64.S — full sk_try_move (AAPCS64)
// int sk_try_move(SkGame *g, int dx, int dy)  x0=g w1=dx w2=dy → w0
// Matches ../asm_common/game.c

        .text
        .global sk_try_move
#ifndef _WIN32
        .type   sk_try_move, %function
#endif
sk_try_move:
        stp     x29, x30, [sp, #-80]!
        mov     x29, sp
        stp     x19, x20, [sp, #16]
        stp     x21, x22, [sp, #32]
        stp     x23, x24, [sp, #48]
        str     x25, [sp, #64]

        mov     x19, x0                 // g
        mov     w20, w1                 // dx
        mov     w21, w2                 // dy

        ldr     w0, [x19, #1044]
        cbnz    w0, .Lfail

        ldr     w22, [x19, #1032]
        add     w22, w22, w20           // nx
        ldr     w23, [x19, #1036]
        add     w23, w23, w21           // ny

        mov     w0, w22
        mov     w1, w23
        bl      .Lat
        cmp     w0, #35
        b.eq    .Lfail
        cmp     w0, #36
        b.eq    .Lpush
        cmp     w0, #42
        b.eq    .Lpush

        ldr     w0, [x19, #1048]
        cmp     w0, #256
        b.ge    .Lfail
        mov     w1, #28
        mul     w1, w0, w1
        add     x2, x19, #1052
        add     x2, x2, w1, uxtw
        ldr     w3, [x19, #1032]
        str     w3, [x2]
        ldr     w3, [x19, #1036]
        str     w3, [x2, #4]
        str     wzr, [x2, #24]
        add     w0, w0, #1
        str     w0, [x19, #1048]
        str     w22, [x19, #1032]
        str     w23, [x19, #1036]
        mov     w0, #1
        b       .Lret

.Lpush:
        add     w24, w22, w20           // bx
        add     w25, w23, w21           // by
        mov     w0, w24
        mov     w1, w25
        bl      .Lat
        cmp     w0, #35
        b.eq    .Lfail
        cmp     w0, #36
        b.eq    .Lfail
        cmp     w0, #42
        b.eq    .Lfail
        ldr     w0, [x19, #1048]
        cmp     w0, #256
        b.ge    .Lfail

        mov     w1, #28
        mul     w1, w0, w1
        add     x2, x19, #1052
        add     x2, x2, w1, uxtw
        ldr     w3, [x19, #1032]
        str     w3, [x2]
        ldr     w3, [x19, #1036]
        str     w3, [x2, #4]
        str     w22, [x2, #8]
        str     w23, [x2, #12]
        str     w24, [x2, #16]
        str     w25, [x2, #20]
        mov     w3, #1
        str     w3, [x2, #24]
        add     w0, w0, #1
        str     w0, [x19, #1048]

        mov     w0, w22
        mov     w1, w23
        bl      .Lat
        cmp     w0, #42
        mov     w2, #46
        mov     w3, #32
        csel    w2, w2, w3, eq
        mov     w0, w22
        mov     w1, w23
        bl      .Lset

        mov     w0, w24
        mov     w1, w25
        bl      .Lat
        cmp     w0, #46
        mov     w2, #42
        mov     w3, #36
        csel    w2, w2, w3, eq
        mov     w0, w24
        mov     w1, w25
        bl      .Lset

        str     w22, [x19, #1032]
        str     w23, [x19, #1036]
        ldr     w0, [x19, #1040]
        add     w0, w0, #1
        str     w0, [x19, #1040]
        bl      .Lcheck_win
        mov     w0, #1
        b       .Lret

.Lfail:
        mov     w0, #0
.Lret:
        ldr     x25, [sp, #64]
        ldp     x19, x20, [sp, #16]
        ldp     x21, x22, [sp, #32]
        ldp     x23, x24, [sp, #48]
        ldp     x29, x30, [sp], #80
        ret

.Lat:   // w0=x w1=y  x19=g → w0
        tbnz    w0, #31, .Latw
        tbnz    w1, #31, .Latw
        ldr     w2, [x19, #1024]
        cmp     w0, w2
        b.ge    .Latw
        ldr     w2, [x19, #1028]
        cmp     w1, w2
        b.ge    .Latw
        add     x2, x19, w0, uxtw
        add     x2, x2, w1, uxtw #5
        ldrb    w0, [x2]
        ret
.Latw:  mov     w0, #35
        ret

.Lset:  // w0=x w1=y w2=c
        add     x3, x19, w0, uxtw
        add     x3, x3, w1, uxtw #5
        strb    w2, [x3]
        ret

.Lcheck_win:
        mov     w0, #1
        str     w0, [x19, #1044]
        mov     w1, wzr
.Lcy:   ldr     w2, [x19, #1028]
        cmp     w1, w2
        b.ge    .Lcwd
        mov     w0, wzr
.Lcx:   ldr     w2, [x19, #1024]
        cmp     w0, w2
        b.ge    .Lcxd
        add     x3, x19, w0, uxtw
        add     x3, x3, w1, uxtw #5
        ldrb    w2, [x3]
        cmp     w2, #36
        b.ne    1f
        str     wzr, [x19, #1044]
1:      add     w0, w0, #1
        b       .Lcx
.Lcxd:  add     w1, w1, #1
        b       .Lcy
.Lcwd:  ret
""",
)

# ─── ARM32 ───────────────────────────────────────────────────────────────────
w(
    "asm_armapp1/try_move_arm.S",
    r"""@ try_move_arm.S — full sk_try_move (AAPCS ARM)
@ int sk_try_move(SkGame *g, int dx, int dy)  r0=g r1=dx r2=dy → r0

        .text
        .global sk_try_move
        .type   sk_try_move, %function
sk_try_move:
        push    {r4-r11, lr}
        mov     r4, r0
        mov     r5, r1
        mov     r6, r2

        ldr     r0, [r4, #1044]
        cmp     r0, #0
        bne     .Lfail

        ldr     r7, [r4, #1032]
        add     r7, r7, r5
        ldr     r8, [r4, #1036]
        add     r8, r8, r6

        mov     r0, r7
        mov     r1, r8
        bl      .Lat
        cmp     r0, #35
        beq     .Lfail
        cmp     r0, #36
        beq     .Lpush
        cmp     r0, #42
        beq     .Lpush

        ldr     r0, [r4, #1048]
        cmp     r0, #256
        bge     .Lfail
        mov     r1, #28
        mul     r1, r0, r1
        add     r1, r1, #1052
        add     r1, r4, r1
        ldr     r2, [r4, #1032]
        str     r2, [r1]
        ldr     r2, [r4, #1036]
        str     r2, [r1, #4]
        mov     r2, #0
        str     r2, [r1, #24]
        add     r0, r0, #1
        str     r0, [r4, #1048]
        str     r7, [r4, #1032]
        str     r8, [r4, #1036]
        mov     r0, #1
        b       .Lret

.Lpush:
        add     r9, r7, r5
        add     r10, r8, r6
        mov     r0, r9
        mov     r1, r10
        bl      .Lat
        cmp     r0, #35
        beq     .Lfail
        cmp     r0, #36
        beq     .Lfail
        cmp     r0, #42
        beq     .Lfail
        ldr     r0, [r4, #1048]
        cmp     r0, #256
        bge     .Lfail

        mov     r1, #28
        mul     r1, r0, r1
        add     r1, r1, #1052
        add     r1, r4, r1
        ldr     r2, [r4, #1032]
        str     r2, [r1]
        ldr     r2, [r4, #1036]
        str     r2, [r1, #4]
        str     r7, [r1, #8]
        str     r8, [r1, #12]
        str     r9, [r1, #16]
        str     r10, [r1, #20]
        mov     r2, #1
        str     r2, [r1, #24]
        add     r0, r0, #1
        str     r0, [r4, #1048]

        mov     r0, r7
        mov     r1, r8
        bl      .Lat
        cmp     r0, #42
        moveq   r2, #46
        movne   r2, #32
        mov     r0, r7
        mov     r1, r8
        bl      .Lset

        mov     r0, r9
        mov     r1, r10
        bl      .Lat
        cmp     r0, #46
        moveq   r2, #42
        movne   r2, #36
        mov     r0, r9
        mov     r1, r10
        bl      .Lset

        str     r7, [r4, #1032]
        str     r8, [r4, #1036]
        ldr     r0, [r4, #1040]
        add     r0, r0, #1
        str     r0, [r4, #1040]
        bl      .Lcheck_win
        mov     r0, #1
        b       .Lret

.Lfail: mov     r0, #0
.Lret:  pop     {r4-r11, pc}

.Lat:   cmp     r0, #0
        blt     .Latw
        cmp     r1, #0
        blt     .Latw
        ldr     r2, [r4, #1024]
        cmp     r0, r2
        bge     .Latw
        ldr     r2, [r4, #1028]
        cmp     r1, r2
        bge     .Latw
        mov     r2, r1, lsl #5
        add     r2, r2, r0
        ldrb    r0, [r4, r2]
        bx      lr
.Latw:  mov     r0, #35
        bx      lr

.Lset:  mov     r3, r1, lsl #5
        add     r3, r3, r0
        strb    r2, [r4, r3]
        bx      lr

.Lcheck_win:
        mov     r0, #1
        str     r0, [r4, #1044]
        mov     r1, #0
.Lcy:   ldr     r2, [r4, #1028]
        cmp     r1, r2
        bge     .Lcwd
        mov     r0, #0
.Lcx:   ldr     r2, [r4, #1024]
        cmp     r0, r2
        bge     .Lcxd
        mov     r3, r1, lsl #5
        add     r3, r3, r0
        ldrb    r2, [r4, r3]
        cmp     r2, #36
        moveq   r2, #0
        streq   r2, [r4, #1044]
        add     r0, r0, #1
        b       .Lcx
.Lcxd:  add     r1, r1, #1
        b       .Lcy
.Lcwd:  bx      lr
        .size   sk_try_move, .-sk_try_move
""",
)

# ─── Thumb-2 ─────────────────────────────────────────────────────────────────
w(
    "asm_thumbapp1/try_move_thumb.S",
    r"""@ try_move_thumb.S — full sk_try_move (Thumb-2 unified syntax)
@ int sk_try_move(SkGame *g, int dx, int dy)  r0=g r1=dx r2=dy → r0

        .syntax unified
        .thumb
        .text
        .global sk_try_move
        .thumb_func
        .type   sk_try_move, %function
sk_try_move:
        push    {r4-r11, lr}
        mov     r4, r0
        mov     r5, r1
        mov     r6, r2

        ldr     r0, [r4, #1044]
        cmp     r0, #0
        bne     .Lfail

        ldr     r7, [r4, #1032]
        adds    r7, r7, r5
        ldr     r8, [r4, #1036]
        adds    r8, r8, r6

        mov     r0, r7
        mov     r1, r8
        bl      .Lat
        cmp     r0, #35
        beq     .Lfail
        cmp     r0, #36
        beq     .Lpush
        cmp     r0, #42
        beq     .Lpush

        ldr     r0, [r4, #1048]
        cmp     r0, #256
        bge     .Lfail
        movs    r1, #28
        mul     r1, r0, r1
        add     r1, r1, #1052
        add     r1, r4, r1
        ldr     r2, [r4, #1032]
        str     r2, [r1]
        ldr     r2, [r4, #1036]
        str     r2, [r1, #4]
        movs    r2, #0
        str     r2, [r1, #24]
        adds    r0, #1
        str     r0, [r4, #1048]
        str     r7, [r4, #1032]
        str     r8, [r4, #1036]
        movs    r0, #1
        b       .Lret

.Lpush:
        adds    r9, r7, r5
        adds    r10, r8, r6
        mov     r0, r9
        mov     r1, r10
        bl      .Lat
        cmp     r0, #35
        beq     .Lfail
        cmp     r0, #36
        beq     .Lfail
        cmp     r0, #42
        beq     .Lfail
        ldr     r0, [r4, #1048]
        cmp     r0, #256
        bge     .Lfail

        movs    r1, #28
        mul     r1, r0, r1
        add     r1, r1, #1052
        add     r1, r4, r1
        ldr     r2, [r4, #1032]
        str     r2, [r1]
        ldr     r2, [r4, #1036]
        str     r2, [r1, #4]
        str     r7, [r1, #8]
        str     r8, [r1, #12]
        str     r9, [r1, #16]
        str     r10, [r1, #20]
        movs    r2, #1
        str     r2, [r1, #24]
        adds    r0, #1
        str     r0, [r4, #1048]

        mov     r0, r7
        mov     r1, r8
        bl      .Lat
        cmp     r0, #42
        ite     eq
        moveq   r2, #46
        movne   r2, #32
        mov     r0, r7
        mov     r1, r8
        bl      .Lset

        mov     r0, r9
        mov     r1, r10
        bl      .Lat
        cmp     r0, #46
        ite     eq
        moveq   r2, #42
        movne   r2, #36
        mov     r0, r9
        mov     r1, r10
        bl      .Lset

        str     r7, [r4, #1032]
        str     r8, [r4, #1036]
        ldr     r0, [r4, #1040]
        adds    r0, #1
        str     r0, [r4, #1040]
        bl      .Lcheck_win
        movs    r0, #1
        b       .Lret

.Lfail: movs    r0, #0
.Lret:  pop     {r4-r11, pc}

        .thumb_func
.Lat:   cmp     r0, #0
        blt     .Latw
        cmp     r1, #0
        blt     .Latw
        ldr     r2, [r4, #1024]
        cmp     r0, r2
        bge     .Latw
        ldr     r2, [r4, #1028]
        cmp     r1, r2
        bge     .Latw
        lsls    r2, r1, #5
        adds    r2, r2, r0
        ldrb    r0, [r4, r2]
        bx      lr
.Latw:  movs    r0, #35
        bx      lr

        .thumb_func
.Lset:  lsls    r3, r1, #5
        adds    r3, r3, r0
        strb    r2, [r4, r3]
        bx      lr

        .thumb_func
.Lcheck_win:
        movs    r0, #1
        str     r0, [r4, #1044]
        movs    r1, #0
.Lcy:   ldr     r2, [r4, #1028]
        cmp     r1, r2
        bge     .Lcwd
        movs    r0, #0
.Lcx:   ldr     r2, [r4, #1024]
        cmp     r0, r2
        bge     .Lcxd
        lsls    r3, r1, #5
        adds    r3, r3, r0
        ldrb    r2, [r4, r3]
        cmp     r2, #36
        bne     1f
        movs    r2, #0
        str     r2, [r4, #1044]
1:      adds    r0, #1
        b       .Lcx
.Lcxd:  adds    r1, #1
        b       .Lcy
.Lcwd:  bx      lr
        .size   sk_try_move, .-sk_try_move
""",
)

# ─── RISC-V (RV64I; same for RV32 with 32-bit load/store of ints) ────────────
w(
    "asm_riscvapp1/try_move_riscv.S",
    r"""# try_move_riscv.S — full sk_try_move (RISC-V integer calling convention)
# int sk_try_move(SkGame *g, int dx, int dy)  a0=g a1=dx a2=dy → a0
# Written for RV64I (ld/sd of callees); ints are still 32-bit lw/sw.

        .text
        .globl  sk_try_move
        .type   sk_try_move, @function
sk_try_move:
        addi    sp, sp, -64
        sd      ra, 56(sp)
        sd      s0, 48(sp)
        sd      s1, 40(sp)
        sd      s2, 32(sp)
        sd      s3, 24(sp)
        sd      s4, 16(sp)
        sd      s5, 8(sp)
        sd      s6, 0(sp)

        mv      s0, a0
        mv      s1, a1
        mv      s2, a2

        lw      t0, 1044(s0)
        bnez    t0, .Lfail

        lw      s3, 1032(s0)
        addw    s3, s3, s1
        lw      s4, 1036(s0)
        addw    s4, s4, s2

        mv      a0, s3
        mv      a1, s4
        call    .Lat
        li      t0, 35
        beq     a0, t0, .Lfail
        li      t0, 36
        beq     a0, t0, .Lpush
        li      t0, 42
        beq     a0, t0, .Lpush

        lw      t0, 1048(s0)
        li      t1, 256
        bge     t0, t1, .Lfail
        li      t1, 28
        mul     t1, t0, t1
        add     t1, t1, s0
        addi    t1, t1, 1052
        lw      t2, 1032(s0)
        sw      t2, 0(t1)
        lw      t2, 1036(s0)
        sw      t2, 4(t1)
        sw      zero, 24(t1)
        addiw   t0, t0, 1
        sw      t0, 1048(s0)
        sw      s3, 1032(s0)
        sw      s4, 1036(s0)
        li      a0, 1
        j       .Lret

.Lpush:
        addw    s5, s3, s1
        addw    s6, s4, s2
        mv      a0, s5
        mv      a1, s6
        call    .Lat
        li      t0, 35
        beq     a0, t0, .Lfail
        li      t0, 36
        beq     a0, t0, .Lfail
        li      t0, 42
        beq     a0, t0, .Lfail
        lw      t0, 1048(s0)
        li      t1, 256
        bge     t0, t1, .Lfail

        li      t1, 28
        mul     t1, t0, t1
        add     t1, t1, s0
        addi    t1, t1, 1052
        lw      t2, 1032(s0)
        sw      t2, 0(t1)
        lw      t2, 1036(s0)
        sw      t2, 4(t1)
        sw      s3, 8(t1)
        sw      s4, 12(t1)
        sw      s5, 16(t1)
        sw      s6, 20(t1)
        li      t2, 1
        sw      t2, 24(t1)
        addiw   t0, t0, 1
        sw      t0, 1048(s0)

        mv      a0, s3
        mv      a1, s4
        call    .Lat
        li      t0, 42
        li      a2, 32
        bne     a0, t0, 1f
        li      a2, 46
1:      mv      a0, s3
        mv      a1, s4
        call    .Lset

        mv      a0, s5
        mv      a1, s6
        call    .Lat
        li      t0, 46
        li      a2, 36
        bne     a0, t0, 2f
        li      a2, 42
2:      mv      a0, s5
        mv      a1, s6
        call    .Lset

        sw      s3, 1032(s0)
        sw      s4, 1036(s0)
        lw      t0, 1040(s0)
        addiw   t0, t0, 1
        sw      t0, 1040(s0)
        call    .Lcheck_win
        li      a0, 1
        j       .Lret

.Lfail: li      a0, 0
.Lret:  ld      ra, 56(sp)
        ld      s0, 48(sp)
        ld      s1, 40(sp)
        ld      s2, 32(sp)
        ld      s3, 24(sp)
        ld      s4, 16(sp)
        ld      s5, 8(sp)
        ld      s6, 0(sp)
        addi    sp, sp, 64
        ret

.Lat:   bltz    a0, .Latw
        bltz    a1, .Latw
        lw      t0, 1024(s0)
        bge     a0, t0, .Latw
        lw      t0, 1028(s0)
        bge     a1, t0, .Latw
        slli    t0, a1, 5
        add     t0, t0, a0
        add     t0, t0, s0
        lbu     a0, 0(t0)
        ret
.Latw:  li      a0, 35
        ret

.Lset:  slli    t0, a1, 5
        add     t0, t0, a0
        add     t0, t0, s0
        sb      a2, 0(t0)
        ret

.Lcheck_win:
        li      t0, 1
        sw      t0, 1044(s0)
        li      a1, 0
.Lcy:   lw      t0, 1028(s0)
        bge     a1, t0, .Lcwd
        li      a0, 0
.Lcx:   lw      t0, 1024(s0)
        bge     a0, t0, .Lcxd
        slli    t0, a1, 5
        add     t0, t0, a0
        add     t0, t0, s0
        lbu     t1, 0(t0)
        li      t2, 36
        bne     t1, t2, 1f
        sw      zero, 1044(s0)
1:      addi    a0, a0, 1
        j       .Lcx
.Lcxd:  addi    a1, a1, 1
        j       .Lcy
.Lcwd:  ret
        .size   sk_try_move, .-sk_try_move
""",
)

# ─── MIPS32 o32 ──────────────────────────────────────────────────────────────
w(
    "asm_mipsapp1/try_move_mips.S",
    r"""# try_move_mips.S — full sk_try_move (MIPS o32)
# int sk_try_move(SkGame *g, int dx, int dy)  a0=g a1=dx a2=dy → v0
# Branch delay slots filled with nop (or useful insn where noted).

        .text
        .globl  sk_try_move
        .ent    sk_try_move
sk_try_move:
        addiu   $sp, $sp, -48
        sw      $ra, 44($sp)
        sw      $s0, 40($sp)
        sw      $s1, 36($sp)
        sw      $s2, 32($sp)
        sw      $s3, 28($sp)
        sw      $s4, 24($sp)
        sw      $s5, 20($sp)
        sw      $s6, 16($sp)

        move    $s0, $a0
        move    $s1, $a1
        move    $s2, $a2

        lw      $t0, 1044($s0)
        bne     $t0, $zero, .Lfail
        nop

        lw      $s3, 1032($s0)
        addu    $s3, $s3, $s1
        lw      $s4, 1036($s0)
        addu    $s4, $s4, $s2

        move    $a0, $s3
        jal     .Lat
        move    $a1, $s4

        li      $t0, 35
        beq     $v0, $t0, .Lfail
        nop
        li      $t0, 36
        beq     $v0, $t0, .Lpush
        nop
        li      $t0, 42
        beq     $v0, $t0, .Lpush
        nop

        lw      $t0, 1048($s0)
        li      $t1, 256
        slt     $t2, $t0, $t1
        beq     $t2, $zero, .Lfail
        nop
        li      $t1, 28
        mul     $t1, $t0, $t1
        addu    $t1, $t1, $s0
        addiu   $t1, $t1, 1052
        lw      $t2, 1032($s0)
        sw      $t2, 0($t1)
        lw      $t2, 1036($s0)
        sw      $t2, 4($t1)
        sw      $zero, 24($t1)
        addiu   $t0, $t0, 1
        sw      $t0, 1048($s0)
        sw      $s3, 1032($s0)
        sw      $s4, 1036($s0)
        b       .Lret
        li      $v0, 1

.Lpush:
        addu    $s5, $s3, $s1
        addu    $s6, $s4, $s2
        move    $a0, $s5
        jal     .Lat
        move    $a1, $s6

        li      $t0, 35
        beq     $v0, $t0, .Lfail
        nop
        li      $t0, 36
        beq     $v0, $t0, .Lfail
        nop
        li      $t0, 42
        beq     $v0, $t0, .Lfail
        nop
        lw      $t0, 1048($s0)
        li      $t1, 256
        slt     $t2, $t0, $t1
        beq     $t2, $zero, .Lfail
        nop

        li      $t1, 28
        mul     $t1, $t0, $t1
        addu    $t1, $t1, $s0
        addiu   $t1, $t1, 1052
        lw      $t2, 1032($s0)
        sw      $t2, 0($t1)
        lw      $t2, 1036($s0)
        sw      $t2, 4($t1)
        sw      $s3, 8($t1)
        sw      $s4, 12($t1)
        sw      $s5, 16($t1)
        sw      $s6, 20($t1)
        li      $t2, 1
        sw      $t2, 24($t1)
        addiu   $t0, $t0, 1
        sw      $t0, 1048($s0)

        move    $a0, $s3
        jal     .Lat
        move    $a1, $s4
        li      $a2, 32
        li      $t0, 42
        bne     $v0, $t0, 1f
        nop
        li      $a2, 46
1:      move    $a0, $s3
        jal     .Lset
        move    $a1, $s4

        move    $a0, $s5
        jal     .Lat
        move    $a1, $s6
        li      $a2, 36
        li      $t0, 46
        bne     $v0, $t0, 2f
        nop
        li      $a2, 42
2:      move    $a0, $s5
        jal     .Lset
        move    $a1, $s6

        sw      $s3, 1032($s0)
        sw      $s4, 1036($s0)
        lw      $t0, 1040($s0)
        addiu   $t0, $t0, 1
        sw      $t0, 1040($s0)
        jal     .Lcheck_win
        nop
        b       .Lret
        li      $v0, 1

.Lfail: move    $v0, $zero
.Lret:  lw      $ra, 44($sp)
        lw      $s0, 40($sp)
        lw      $s1, 36($sp)
        lw      $s2, 32($sp)
        lw      $s3, 28($sp)
        lw      $s4, 24($sp)
        lw      $s5, 20($sp)
        lw      $s6, 16($sp)
        addiu   $sp, $sp, 48
        jr      $ra
        nop

.Lat:   bltz    $a0, .Latw
        nop
        bltz    $a1, .Latw
        nop
        lw      $t0, 1024($s0)
        slt     $t1, $a0, $t0
        beq     $t1, $zero, .Latw
        nop
        lw      $t0, 1028($s0)
        slt     $t1, $a1, $t0
        beq     $t1, $zero, .Latw
        nop
        sll     $t0, $a1, 5
        addu    $t0, $t0, $a0
        addu    $t0, $t0, $s0
        jr      $ra
        lbu     $v0, 0($t0)
.Latw:  jr      $ra
        li      $v0, 35

.Lset:  sll     $t0, $a1, 5
        addu    $t0, $t0, $a0
        addu    $t0, $t0, $s0
        jr      $ra
        sb      $a2, 0($t0)

.Lcheck_win:
        li      $t0, 1
        sw      $t0, 1044($s0)
        move    $t1, $zero
.Lcy:   lw      $t0, 1028($s0)
        slt     $t2, $t1, $t0
        beq     $t2, $zero, .Lcwd
        nop
        move    $t3, $zero
.Lcx:   lw      $t0, 1024($s0)
        slt     $t2, $t3, $t0
        beq     $t2, $zero, .Lcxd
        nop
        sll     $t0, $t1, 5
        addu    $t0, $t0, $t3
        addu    $t0, $t0, $s0
        lbu     $t4, 0($t0)
        li      $t5, 36
        bne     $t4, $t5, 1f
        nop
        sw      $zero, 1044($s0)
1:      b       .Lcx
        addiu   $t3, $t3, 1
.Lcxd:  b       .Lcy
        addiu   $t1, $t1, 1
.Lcwd:  jr      $ra
        nop
        .end    sk_try_move
""",
)

# ─── PowerPC 32-bit ──────────────────────────────────────────────────────────
w(
    "asm_ppcapp1/try_move_ppc.S",
    r"""# try_move_ppc.S — full sk_try_move (PowerPC 32-bit)
# int sk_try_move(SkGame *g, int dx, int dy)  r3=g r4=dx r5=dy → r3

        .text
        .globl  sk_try_move
        .type   sk_try_move, @function
sk_try_move:
        mflr    0
        stwu    1, -80(1)
        stw     0, 84(1)
        stw     14, 8(1)
        stw     15, 12(1)
        stw     16, 16(1)
        stw     17, 20(1)
        stw     18, 24(1)
        stw     19, 28(1)
        stw     20, 32(1)

        mr      14, 3
        mr      15, 4
        mr      16, 5

        lwz     3, 1044(14)
        cmpwi   3, 0
        bne     .Lfail

        lwz     17, 1032(14)
        add     17, 17, 15
        lwz     18, 1036(14)
        add     18, 18, 16

        mr      3, 17
        mr      4, 18
        bl      .Lat
        cmpwi   3, 35
        beq     .Lfail
        cmpwi   3, 36
        beq     .Lpush
        cmpwi   3, 42
        beq     .Lpush

        lwz     3, 1048(14)
        cmpwi   3, 256
        bge     .Lfail
        mulli   4, 3, 28
        add     4, 4, 14
        addi    4, 4, 1052
        lwz     5, 1032(14)
        stw     5, 0(4)
        lwz     5, 1036(14)
        stw     5, 4(4)
        li      5, 0
        stw     5, 24(4)
        addi    3, 3, 1
        stw     3, 1048(14)
        stw     17, 1032(14)
        stw     18, 1036(14)
        li      3, 1
        b       .Lret

.Lpush:
        add     19, 17, 15
        add     20, 18, 16
        mr      3, 19
        mr      4, 20
        bl      .Lat
        cmpwi   3, 35
        beq     .Lfail
        cmpwi   3, 36
        beq     .Lfail
        cmpwi   3, 42
        beq     .Lfail
        lwz     3, 1048(14)
        cmpwi   3, 256
        bge     .Lfail

        mulli   4, 3, 28
        add     4, 4, 14
        addi    4, 4, 1052
        lwz     5, 1032(14)
        stw     5, 0(4)
        lwz     5, 1036(14)
        stw     5, 4(4)
        stw     17, 8(4)
        stw     18, 12(4)
        stw     19, 16(4)
        stw     20, 20(4)
        li      5, 1
        stw     5, 24(4)
        addi    3, 3, 1
        stw     3, 1048(14)

        mr      3, 17
        mr      4, 18
        bl      .Lat
        cmpwi   3, 42
        li      5, 46
        beq     1f
        li      5, 32
1:      mr      3, 17
        mr      4, 18
        bl      .Lset

        mr      3, 19
        mr      4, 20
        bl      .Lat
        cmpwi   3, 46
        li      5, 42
        beq     2f
        li      5, 36
2:      mr      3, 19
        mr      4, 20
        bl      .Lset

        stw     17, 1032(14)
        stw     18, 1036(14)
        lwz     3, 1040(14)
        addi    3, 3, 1
        stw     3, 1040(14)
        bl      .Lcheck_win
        li      3, 1
        b       .Lret

.Lfail: li      3, 0
.Lret:  lwz     14, 8(1)
        lwz     15, 12(1)
        lwz     16, 16(1)
        lwz     17, 20(1)
        lwz     18, 24(1)
        lwz     19, 28(1)
        lwz     20, 32(1)
        lwz     0, 84(1)
        mtlr    0
        addi    1, 1, 80
        blr

.Lat:   cmpwi   3, 0
        blt     .Latw
        cmpwi   4, 0
        blt     .Latw
        lwz     5, 1024(14)
        cmpw    3, 5
        bge     .Latw
        lwz     5, 1028(14)
        cmpw    4, 5
        bge     .Latw
        slwi    5, 4, 5
        add     5, 5, 3
        lbzx    3, 14, 5
        blr
.Latw:  li      3, 35
        blr

.Lset:  slwi    6, 4, 5
        add     6, 6, 3
        stbx    5, 14, 6
        blr

.Lcheck_win:
        li      3, 1
        stw     3, 1044(14)
        li      4, 0
.Lcy:   lwz     5, 1028(14)
        cmpw    4, 5
        bge     .Lcwd
        li      3, 0
.Lcx:   lwz     5, 1024(14)
        cmpw    3, 5
        bge     .Lcxd
        slwi    5, 4, 5
        add     5, 5, 3
        lbzx    6, 14, 5
        cmpwi   6, 36
        bne     1f
        li      6, 0
        stw     6, 1044(14)
1:      addi    3, 3, 1
        b       .Lcx
.Lcxd:  addi    4, 4, 1
        b       .Lcy
.Lcwd:  blr
        .size   sk_try_move, .-sk_try_move
""",
)

# ─── LoongArch64 ─────────────────────────────────────────────────────────────
w(
    "asm_loongarchapp1/try_move_loongarch.S",
    r"""# try_move_loongarch.S — full sk_try_move (LoongArch64)
# int sk_try_move(SkGame *g, int dx, int dy)  a0=g a1=dx a2=dy → a0

        .text
        .globl  sk_try_move
        .type   sk_try_move, @function
sk_try_move:
        addi.d  $sp, $sp, -64
        st.d    $ra, $sp, 56
        st.d    $fp, $sp, 48
        st.d    $s0, $sp, 40
        st.d    $s1, $sp, 32
        st.d    $s2, $sp, 24
        st.d    $s3, $sp, 16
        st.d    $s4, $sp, 8
        st.d    $s5, $sp, 0

        move    $fp, $a0
        move    $s0, $a1
        move    $s1, $a2

        ld.w    $t0, $fp, 1044
        bnez    $t0, .Lfail

        ld.w    $s2, $fp, 1032
        add.w   $s2, $s2, $s0
        ld.w    $s3, $fp, 1036
        add.w   $s3, $s3, $s1

        move    $a0, $s2
        move    $a1, $s3
        bl      .Lat
        li.w    $t0, 35
        beq     $a0, $t0, .Lfail
        li.w    $t0, 36
        beq     $a0, $t0, .Lpush
        li.w    $t0, 42
        beq     $a0, $t0, .Lpush

        ld.w    $t0, $fp, 1048
        li.w    $t1, 256
        bge     $t0, $t1, .Lfail
        li.w    $t1, 28
        mul.w   $t1, $t0, $t1
        add.d   $t1, $fp, $t1
        addi.d  $t1, $t1, 1052
        ld.w    $t2, $fp, 1032
        st.w    $t2, $t1, 0
        ld.w    $t2, $fp, 1036
        st.w    $t2, $t1, 4
        st.w    $zero, $t1, 24
        addi.w  $t0, $t0, 1
        st.w    $t0, $fp, 1048
        st.w    $s2, $fp, 1032
        st.w    $s3, $fp, 1036
        li.w    $a0, 1
        b       .Lret

.Lpush:
        add.w   $s4, $s2, $s0
        add.w   $s5, $s3, $s1
        move    $a0, $s4
        move    $a1, $s5
        bl      .Lat
        li.w    $t0, 35
        beq     $a0, $t0, .Lfail
        li.w    $t0, 36
        beq     $a0, $t0, .Lfail
        li.w    $t0, 42
        beq     $a0, $t0, .Lfail
        ld.w    $t0, $fp, 1048
        li.w    $t1, 256
        bge     $t0, $t1, .Lfail

        li.w    $t1, 28
        mul.w   $t1, $t0, $t1
        add.d   $t1, $fp, $t1
        addi.d  $t1, $t1, 1052
        ld.w    $t2, $fp, 1032
        st.w    $t2, $t1, 0
        ld.w    $t2, $fp, 1036
        st.w    $t2, $t1, 4
        st.w    $s2, $t1, 8
        st.w    $s3, $t1, 12
        st.w    $s4, $t1, 16
        st.w    $s5, $t1, 20
        li.w    $t2, 1
        st.w    $t2, $t1, 24
        addi.w  $t0, $t0, 1
        st.w    $t0, $fp, 1048

        move    $a0, $s2
        move    $a1, $s3
        bl      .Lat
        li.w    $t0, 42
        li.w    $a2, 32
        bne     $a0, $t0, 1f
        li.w    $a2, 46
1:      move    $a0, $s2
        move    $a1, $s3
        bl      .Lset

        move    $a0, $s4
        move    $a1, $s5
        bl      .Lat
        li.w    $t0, 46
        li.w    $a2, 36
        bne     $a0, $t0, 2f
        li.w    $a2, 42
2:      move    $a0, $s4
        move    $a1, $s5
        bl      .Lset

        st.w    $s2, $fp, 1032
        st.w    $s3, $fp, 1036
        ld.w    $t0, $fp, 1040
        addi.w  $t0, $t0, 1
        st.w    $t0, $fp, 1040
        bl      .Lcheck_win
        li.w    $a0, 1
        b       .Lret

.Lfail: li.w    $a0, 0
.Lret:  ld.d    $ra, $sp, 56
        ld.d    $fp, $sp, 48
        ld.d    $s0, $sp, 40
        ld.d    $s1, $sp, 32
        ld.d    $s2, $sp, 24
        ld.d    $s3, $sp, 16
        ld.d    $s4, $sp, 8
        ld.d    $s5, $sp, 0
        addi.d  $sp, $sp, 64
        jr      $ra

.Lat:   blt     $a0, $zero, .Latw
        blt     $a1, $zero, .Latw
        ld.w    $t0, $fp, 1024
        bge     $a0, $t0, .Latw
        ld.w    $t0, $fp, 1028
        bge     $a1, $t0, .Latw
        slli.d  $t0, $a1, 5
        add.d   $t0, $t0, $a0
        add.d   $t0, $t0, $fp
        ld.bu   $a0, $t0, 0
        jr      $ra
.Latw:  li.w    $a0, 35
        jr      $ra

.Lset:  slli.d  $t0, $a1, 5
        add.d   $t0, $t0, $a0
        add.d   $t0, $t0, $fp
        st.b    $a2, $t0, 0
        jr      $ra

.Lcheck_win:
        li.w    $t0, 1
        st.w    $t0, $fp, 1044
        move    $a1, $zero
.Lcy:   ld.w    $t0, $fp, 1028
        bge     $a1, $t0, .Lcwd
        move    $a0, $zero
.Lcx:   ld.w    $t0, $fp, 1024
        bge     $a0, $t0, .Lcxd
        slli.d  $t0, $a1, 5
        add.d   $t0, $t0, $a0
        add.d   $t0, $t0, $fp
        ld.bu   $t1, $t0, 0
        li.w    $t2, 36
        bne     $t1, $t2, 1f
        st.w    $zero, $fp, 1044
1:      addi.w  $a0, $a0, 1
        b       .Lcx
.Lcxd:  addi.w  $a1, $a1, 1
        b       .Lcy
.Lcwd:  jr      $ra
        .size   sk_try_move, .-sk_try_move
""",
)

# ─── AVR (teaching, avr-gcc ABI) ─────────────────────────────────────────────
w(
    "asm_avrapp1/try_move_avr.S",
    r"""; try_move_avr.S — full sk_try_move (AVR / avr-gcc ABI)
;
; int sk_try_move(SkGame *g, int dx, int dy)
;   r25:r24 = g, r23:r22 = dx, r21:r20 = dy → r25:r24 (0/1)
; Mini-level coordinates fit in 8 bits; field offsets match game.h (LE int32).
; avr-gcc -mmcu=atmega328p -c try_move_avr.S

        .global sk_try_move
        .type   sk_try_move, @function

sk_try_move:
        push    r2
        push    r3
        push    r4
        push    r6
        push    r8
        push    r9
        push    r10
        push    r11
        push    r12
        push    r16
        push    r17
        push    r28
        push    r29

        movw    r28, r24                ; Y = g
        mov     r2, r22                 ; dx
        mov     r3, r20                 ; dy

        ldd     r16, Y+1044
        tst     r16
        brne    .Lfail

        ldd     r4, Y+1032
        add     r4, r2                  ; nx
        ldd     r6, Y+1036
        add     r6, r3                  ; ny

        mov     r24, r4
        mov     r22, r6
        rcall   at_cell
        cpi     r24, '#'
        breq    .Lfail
        cpi     r24, '$'
        breq    .Lpush
        cpi     r24, '*'
        breq    .Lpush

        ldd     r16, Y+1048
        cpi     r16, 255
        brsh    .Lfail
        ldi     r24, 0
        rcall   hist_write
        std     Y+1032, r4
        std     Y+1036, r6
        ldi     r24, 1
        clr     r25
        rjmp    .Lret

.Lpush:
        mov     r8, r4
        add     r8, r2                  ; bx
        mov     r9, r6
        add     r9, r3                  ; by
        mov     r24, r8
        mov     r22, r9
        rcall   at_cell
        cpi     r24, '#'
        breq    .Lfail
        cpi     r24, '$'
        breq    .Lfail
        cpi     r24, '*'
        breq    .Lfail
        ldd     r16, Y+1048
        cpi     r16, 255
        brsh    .Lfail

        ldi     r24, 1
        rcall   hist_write
        mov     r24, r4
        mov     r22, r6
        rcall   at_cell
        cpi     r24, '*'
        ldi     r20, '.'
        breq    1f
        ldi     r20, ' '
1:      mov     r24, r4
        mov     r22, r6
        rcall   set_cell
        mov     r24, r8
        mov     r22, r9
        rcall   at_cell
        cpi     r24, '.'
        ldi     r20, '*'
        breq    2f
        ldi     r20, '$'
2:      mov     r24, r8
        mov     r22, r9
        rcall   set_cell
        std     Y+1032, r4
        std     Y+1036, r6
        ldd     r16, Y+1040
        inc     r16
        std     Y+1040, r16
        rcall   check_win
        ldi     r24, 1
        clr     r25
        rjmp    .Lret

.Lfail: clr     r24
        clr     r25
.Lret:  pop     r29
        pop     r28
        pop     r17
        pop     r16
        pop     r12
        pop     r11
        pop     r10
        pop     r9
        pop     r8
        pop     r6
        pop     r4
        pop     r3
        pop     r2
        ret

at_cell:
        tst     r24
        brmi    .wall
        tst     r22
        brmi    .wall
        ldd     r16, Y+1024
        cp      r24, r16
        brsh    .wall
        ldd     r16, Y+1028
        cp      r22, r16
        brsh    .wall
        mov     r30, r22
        clr     r31
        ldi     r16, 5
.m:     lsl     r30
        rol     r31
        dec     r16
        brne    .m
        add     r30, r24
        adc     r31, r1
        add     r30, r28
        adc     r31, r29
        ld      r24, Z
        ret
.wall:  ldi     r24, '#'
        ret

set_cell:
        mov     r30, r22
        clr     r31
        ldi     r16, 5
.ms:    lsl     r30
        rol     r31
        dec     r16
        brne    .ms
        add     r30, r24
        adc     r31, r1
        add     r30, r28
        adc     r31, r29
        st      Z, r20
        ret

; r24 = is_push; uses r4=nx r6=ny r8=bx r9=by when push
hist_write:
        mov     r12, r24
        ldd     r16, Y+1048
        movw    r30, r28
        ldi     r18, lo8(1052)
        ldi     r19, hi8(1052)
        add     r30, r18
        adc     r31, r19
        ldi     r18, 28
        mul     r16, r18
        add     r30, r0
        adc     r31, r1
        clr     r1
        ldd     r18, Y+1032
        st      Z+, r18
        st      Z+, r1
        st      Z+, r1
        st      Z+, r1
        ldd     r18, Y+1036
        st      Z+, r18
        st      Z+, r1
        st      Z+, r1
        st      Z+, r1
        st      Z+, r4
        st      Z+, r1
        st      Z+, r1
        st      Z+, r1
        st      Z+, r6
        st      Z+, r1
        st      Z+, r1
        st      Z+, r1
        st      Z+, r8
        st      Z+, r1
        st      Z+, r1
        st      Z+, r1
        st      Z+, r9
        st      Z+, r1
        st      Z+, r1
        st      Z+, r1
        st      Z+, r12
        st      Z+, r1
        st      Z+, r1
        st      Z+, r1
        inc     r16
        std     Y+1048, r16
        ret

check_win:
        ldi     r16, 1
        std     Y+1044, r16
        clr     r10
.cy:    ldd     r16, Y+1028
        cp      r10, r16
        brsh    .cwd
        clr     r11
.cx:    ldd     r16, Y+1024
        cp      r11, r16
        brsh    .cxd
        mov     r24, r11
        mov     r22, r10
        rcall   at_cell
        cpi     r24, '$'
        brne    1f
        std     Y+1044, r1
1:      inc     r11
        rjmp    .cx
.cxd:   inc     r10
        rjmp    .cy
.cwd:   ret
        .size   sk_try_move, .-sk_try_move
""",
)

# ─── Z80 ─────────────────────────────────────────────────────────────────────
w(
    "asm_z80app1/try_move_z80.asm",
    r"""; try_move_z80.asm — full sk_try_move (Z80 teaching)
;
; Convention (sjasmplus / similar):
;   HL = SkGame*
;   B  = dx, C = dy   (signed 8-bit)
;   A  = 1 success / 0 fail
; Field layout matches game.h; uses low bytes of int32 coords.

        PUBLIC  sk_try_move

        SECTION code

sk_try_move:
        ld      (game_ptr), hl
        ld      a, b
        ld      (v_dx), a
        ld      a, c
        ld      (v_dy), a

        ld      hl, (game_ptr)
        ld      de, 1044
        add     hl, de
        ld      a, (hl)
        or      a
        jp      nz, fail

        ld      hl, (game_ptr)
        ld      de, 1032
        add     hl, de
        ld      a, (hl)
        ld      b, a
        ld      a, (v_dx)
        add     a, b
        ld      (v_nx), a

        ld      hl, (game_ptr)
        ld      de, 1036
        add     hl, de
        ld      a, (hl)
        ld      b, a
        ld      a, (v_dy)
        add     a, b
        ld      (v_ny), a

        ld      a, (v_nx)
        ld      b, a
        ld      a, (v_ny)
        ld      c, a
        call    at_cell
        cp      '#'
        jp      z, fail
        cp      '$'
        jr      z, do_push
        cp      '*'
        jr      z, do_push

        call    hist_is_full
        jp      c, fail
        xor     a
        call    hist_write
        ld      a, (v_nx)
        call    set_px
        ld      a, (v_ny)
        call    set_py
        ld      a, 1
        ret

do_push:
        ld      a, (v_nx)
        ld      b, a
        ld      a, (v_dx)
        add     a, b
        ld      (v_bx), a
        ld      a, (v_ny)
        ld      b, a
        ld      a, (v_dy)
        add     a, b
        ld      (v_by), a

        ld      a, (v_bx)
        ld      b, a
        ld      a, (v_by)
        ld      c, a
        call    at_cell
        cp      '#'
        jp      z, fail
        cp      '$'
        jp      z, fail
        cp      '*'
        jp      z, fail
        call    hist_is_full
        jp      c, fail

        ld      a, 1
        call    hist_write

        ld      a, (v_nx)
        ld      b, a
        ld      a, (v_ny)
        ld      c, a
        call    at_cell
        cp      '*'
        ld      a, '.'
        jr      z, .c1
        ld      a, ' '
.c1:    ld      e, a
        ld      a, (v_nx)
        ld      b, a
        ld      a, (v_ny)
        ld      c, a
        ld      a, e
        call    set_cell

        ld      a, (v_bx)
        ld      b, a
        ld      a, (v_by)
        ld      c, a
        call    at_cell
        cp      '.'
        ld      a, '*'
        jr      z, .c2
        ld      a, '$'
.c2:    ld      e, a
        ld      a, (v_bx)
        ld      b, a
        ld      a, (v_by)
        ld      c, a
        ld      a, e
        call    set_cell

        ld      a, (v_nx)
        call    set_px
        ld      a, (v_ny)
        call    set_py
        ld      hl, (game_ptr)
        ld      de, 1040
        add     hl, de
        inc     (hl)
        call    check_win
        ld      a, 1
        ret

fail:   xor     a
        ret

; B=x C=y → A
at_cell:
        bit     7, b
        jr      nz, wall
        bit     7, c
        jr      nz, wall
        ld      hl, (game_ptr)
        ld      de, 1024
        add     hl, de
        ld      a, b
        cp      (hl)
        jr      nc, wall
        ld      hl, (game_ptr)
        ld      de, 1028
        add     hl, de
        ld      a, c
        cp      (hl)
        jr      nc, wall
        ld      h, 0
        ld      l, c
        add     hl, hl
        add     hl, hl
        add     hl, hl
        add     hl, hl
        add     hl, hl
        ld      e, b
        ld      d, 0
        add     hl, de
        ld      de, (game_ptr)
        add     hl, de
        ld      a, (hl)
        ret
wall:   ld      a, '#'
        ret

; B=x C=y A=char
set_cell:
        push    af
        ld      h, 0
        ld      l, c
        add     hl, hl
        add     hl, hl
        add     hl, hl
        add     hl, hl
        add     hl, hl
        ld      e, b
        ld      d, 0
        add     hl, de
        ld      de, (game_ptr)
        add     hl, de
        pop     af
        ld      (hl), a
        ret

set_px: ld      hl, (game_ptr)
        ld      de, 1032
        add     hl, de
        ld      (hl), a
        ret

set_py: ld      hl, (game_ptr)
        ld      de, 1036
        add     hl, de
        ld      (hl), a
        ret

; CF=1 if hist_n >= 255
hist_is_full:
        ld      hl, (game_ptr)
        ld      de, 1048
        add     hl, de
        ld      a, (hl)
        cp      255
        ret                             ; C if A<255, NC if A>=255 — invert:
        ; Actually CP n: C set if A < n. We want C if full (A>=255).
        ; So: cp 255 / ccf  if we had A<=254 C=1... messy.
        ; Use:
hist_is_full:
        ld      hl, (game_ptr)
        ld      de, 1048
        add     hl, de
        ld      a, (hl)
        cp      255
        ccf                             ; if A<255 C=1 → CCF → C=0 ok; if A>=255 C=0 → C=1 full
        ret

; A = is_push
hist_write:
        ld      (v_push), a
        ld      hl, (game_ptr)
        ld      de, 1052
        add     hl, de
        push    hl
        ld      hl, (game_ptr)
        ld      de, 1048
        add     hl, de
        ld      a, (hl)
        ld      e, a
        ld      d, 0
        ld      l, e
        ld      h, d
        add     hl, hl
        add     hl, hl
        add     hl, hl
        add     hl, hl
        add     hl, hl                  ; *32
        push    hl
        ld      l, e
        ld      h, d
        add     hl, hl
        add     hl, hl                  ; *4
        pop     de
        ex      de, hl
        or      a
        sbc     hl, de                  ; *28
        pop     de
        add     hl, de                  ; entry

        push    hl
        ld      hl, (game_ptr)
        ld      de, 1032
        add     hl, de
        ld      a, (hl)
        pop     hl
        call    st_i32
        push    hl
        ld      hl, (game_ptr)
        ld      de, 1036
        add     hl, de
        ld      a, (hl)
        pop     hl
        call    st_i32
        ld      a, (v_nx)
        call    st_i32
        ld      a, (v_ny)
        call    st_i32
        ld      a, (v_bx)
        call    st_i32
        ld      a, (v_by)
        call    st_i32
        ld      a, (v_push)
        ld      (hl), a

        ld      hl, (game_ptr)
        ld      de, 1048
        add     hl, de
        inc     (hl)
        ret

st_i32: ld      (hl), a
        inc     hl
        ld      (hl), 0
        inc     hl
        ld      (hl), 0
        inc     hl
        ld      (hl), 0
        inc     hl
        ret

check_win:
        ld      hl, (game_ptr)
        ld      de, 1044
        add     hl, de
        ld      (hl), 1
        ld      c, 0
.cy:    ld      hl, (game_ptr)
        ld      de, 1028
        add     hl, de
        ld      a, c
        cp      (hl)
        ret     nc
        ld      b, 0
.cx:    ld      hl, (game_ptr)
        ld      de, 1024
        add     hl, de
        ld      a, b
        cp      (hl)
        jr      nc, .nx
        push    bc
        call    at_cell
        pop     bc
        cp      '$'
        jr      nz, .n1
        ld      hl, (game_ptr)
        ld      de, 1044
        add     hl, de
        ld      (hl), 0
.n1:    inc     b
        jr      .cx
.nx:    inc     c
        jr      .cy

        SECTION bss
game_ptr:   dw 0
v_dx:       db 0
v_dy:       db 0
v_nx:       db 0
v_ny:       db 0
v_bx:       db 0
v_by:       db 0
v_push:     db 0
""",
)

# Fix duplicate hist_is_full in Z80 - I accidentally left two definitions
z80_path = ROOT / "asm_z80app1/try_move_z80.asm"
z80 = z80_path.read_text(encoding="utf-8")
# remove the broken first hist_is_full stub
bad = """; CF=1 if hist_n >= 255
hist_is_full:
        ld      hl, (game_ptr)
        ld      de, 1048
        add     hl, de
        ld      a, (hl)
        cp      255
        ret                             ; C if A<255, NC if A>=255 — invert:
        ; Actually CP n: C set if A < n. We want C if full (A>=255).
        ; So: cp 255 / ccf  if we had A<=254 C=1... messy.
        ; Use:
hist_is_full:
"""
good = """; CF=1 if hist full (n >= 255)
hist_is_full:
"""
if bad in z80:
    z80_path.write_text(z80.replace(bad, good), encoding="utf-8")
    print("fixed z80 hist_is_full")

# ─── 6502 ca65 ───────────────────────────────────────────────────────────────
w(
    "asm_6502app1/try_move_6502.s",
    r"""; try_move_6502.s — full sk_try_move (ca65 / 65C02 teaching)
;
; Entry:  A = dx, X = dy (signed 8-bit)
;         zero-page game_ptr → SkGame (same layout as game.h)
; Return: A = 1 / 0
; Import: .importzp game_ptr

        .export sk_try_move
        .export sk_try_move_6502
        .importzp game_ptr

        .zeropage
tmp0:   .res 1
tmp1:   .res 1
tmp2:   .res 1
v_dx:   .res 1
v_dy:   .res 1
v_nx:   .res 1
v_ny:   .res 1
v_bx:   .res 1
v_by:   .res 1
v_ch:   .res 1
v_push: .res 1
ptr:    .res 2

        .code

sk_try_move_6502:
sk_try_move:
        sta     v_dx
        stx     v_dy

        lda     #<(1044)
        ldx     #>(1044)
        jsr     load_u8
        bne     fail

        lda     #<(1032)
        ldx     #>(1032)
        jsr     load_u8
        clc
        adc     v_dx
        sta     v_nx
        lda     #<(1036)
        ldx     #>(1036)
        jsr     load_u8
        clc
        adc     v_dy
        sta     v_ny

        lda     v_nx
        ldx     v_ny
        jsr     at_cell
        sta     v_ch
        cmp     #'#'
        beq     fail
        cmp     #'$'
        beq     do_push
        cmp     #'*'
        beq     do_push

        jsr     hist_full
        bcs     fail
        lda     #0
        sta     v_push
        jsr     hist_write
        lda     v_nx
        jsr     store_px
        lda     v_ny
        jsr     store_py
        lda     #1
        rts

do_push:
        lda     v_nx
        clc
        adc     v_dx
        sta     v_bx
        lda     v_ny
        clc
        adc     v_dy
        sta     v_by
        lda     v_bx
        ldx     v_by
        jsr     at_cell
        cmp     #'#'
        beq     fail
        cmp     #'$'
        beq     fail
        cmp     #'*'
        beq     fail
        jsr     hist_full
        bcs     fail
        lda     #1
        sta     v_push
        jsr     hist_write

        lda     v_nx
        ldx     v_ny
        jsr     at_cell
        cmp     #'*'
        lda     #'.'
        beq     :+
        lda     #' '
:       sta     v_ch
        lda     v_nx
        ldx     v_ny
        ldy     v_ch
        jsr     set_cell

        lda     v_bx
        ldx     v_by
        jsr     at_cell
        cmp     #'.'
        lda     #'*'
        beq     :+
        lda     #'$'
:       sta     v_ch
        lda     v_bx
        ldx     v_by
        ldy     v_ch
        jsr     set_cell

        lda     v_nx
        jsr     store_px
        lda     v_ny
        jsr     store_py
        lda     #<(1040)
        ldx     #>(1040)
        jsr     load_u8
        clc
        adc     #1
        jsr     store_moves
        jsr     check_win
        lda     #1
        rts

fail:   lda     #0
        rts

; ---- helpers ----
; A=lo X=hi offset → load byte to A
load_u8:
        clc
        adc     game_ptr
        sta     ptr
        txa
        adc     game_ptr+1
        sta     ptr+1
        ldy     #0
        lda     (ptr),y
        rts

store_px:
        sta     tmp0
        lda     #<(1032)
        clc
        adc     game_ptr
        sta     ptr
        lda     #>(1032)
        adc     game_ptr+1
        sta     ptr+1
        ldy     #0
        lda     tmp0
        sta     (ptr),y
        rts

store_py:
        sta     tmp0
        lda     #<(1036)
        clc
        adc     game_ptr
        sta     ptr
        lda     #>(1036)
        adc     game_ptr+1
        sta     ptr+1
        ldy     #0
        lda     tmp0
        sta     (ptr),y
        rts

store_moves:
        sta     tmp0
        lda     #<(1040)
        clc
        adc     game_ptr
        sta     ptr
        lda     #>(1040)
        adc     game_ptr+1
        sta     ptr+1
        ldy     #0
        lda     tmp0
        sta     (ptr),y
        rts

; A=x X=y → A
at_cell:
        sta     tmp0
        stx     tmp1
        lda     tmp0
        bmi     wall
        lda     tmp1
        bmi     wall
        lda     #<(1024)
        ldx     #>(1024)
        jsr     load_u8
        cmp     tmp0
        beq     wall
        bcc     wall
        lda     #<(1028)
        ldx     #>(1028)
        jsr     load_u8
        cmp     tmp1
        beq     wall
        bcc     wall
        lda     tmp1
        asl     a
        asl     a
        asl     a
        asl     a
        asl     a
        clc
        adc     tmp0
        clc
        adc     game_ptr
        sta     ptr
        lda     game_ptr+1
        adc     #0
        sta     ptr+1
        ldy     #0
        lda     (ptr),y
        rts
wall:   lda     #'#'
        rts

; A=x X=y Y=char
set_cell:
        sta     tmp0
        stx     tmp1
        sty     tmp2
        lda     tmp1
        asl     a
        asl     a
        asl     a
        asl     a
        asl     a
        clc
        adc     tmp0
        clc
        adc     game_ptr
        sta     ptr
        lda     game_ptr+1
        adc     #0
        sta     ptr+1
        ldy     #0
        lda     tmp2
        sta     (ptr),y
        rts

; C=1 if full
hist_full:
        lda     #<(1048)
        ldx     #>(1048)
        jsr     load_u8
        cmp     #255
        rts

hist_write:
        ; ptr = game + 1052 + n*28
        lda     #0
        sta     ptr
        sta     ptr+1
        lda     #<(1048)
        ldx     #>(1048)
        jsr     load_u8
        sta     tmp0
        beq     .hp0
:       clc
        lda     ptr
        adc     #28
        sta     ptr
        lda     ptr+1
        adc     #0
        sta     ptr+1
        dec     tmp0
        bne     :-
.hp0:   clc
        lda     ptr
        adc     game_ptr
        sta     ptr
        lda     ptr+1
        adc     game_ptr+1
        sta     ptr+1
        clc
        lda     ptr
        adc     #<(1052)
        sta     ptr
        lda     ptr+1
        adc     #>(1052)
        sta     ptr+1

        lda     #<(1032)
        ldx     #>(1032)
        jsr     load_u8
        ldy     #0
        sta     (ptr),y
        lda     #<(1036)
        ldx     #>(1036)
        jsr     load_u8
        ldy     #4
        sta     (ptr),y
        lda     v_nx
        ldy     #8
        sta     (ptr),y
        lda     v_ny
        ldy     #12
        sta     (ptr),y
        lda     v_bx
        ldy     #16
        sta     (ptr),y
        lda     v_by
        ldy     #20
        sta     (ptr),y
        lda     v_push
        ldy     #24
        sta     (ptr),y

        lda     #<(1048)
        clc
        adc     game_ptr
        sta     ptr
        lda     #>(1048)
        adc     game_ptr+1
        sta     ptr+1
        ldy     #0
        lda     (ptr),y
        clc
        adc     #1
        sta     (ptr),y
        rts

check_win:
        lda     #<(1044)
        clc
        adc     game_ptr
        sta     ptr
        lda     #>(1044)
        adc     game_ptr+1
        sta     ptr+1
        ldy     #0
        lda     #1
        sta     (ptr),y
        lda     #0
        sta     tmp1
.cy:    lda     #<(1028)
        ldx     #>(1028)
        jsr     load_u8
        cmp     tmp1
        beq     .cwd
        bcc     .cwd
        lda     #0
        sta     tmp0
.cx:    lda     #<(1024)
        ldx     #>(1024)
        jsr     load_u8
        cmp     tmp0
        beq     .cxd
        bcc     .cxd
        lda     tmp0
        ldx     tmp1
        jsr     at_cell
        cmp     #'$'
        bne     .n1
        lda     #<(1044)
        clc
        adc     game_ptr
        sta     ptr
        lda     #>(1044)
        adc     game_ptr+1
        sta     ptr+1
        ldy     #0
        tya
        sta     (ptr),y
.n1:    inc     tmp0
        jmp     .cx
.cxd:   inc     tmp1
        jmp     .cy
.cwd:   rts
""",
)

print("all ISA sources written")
