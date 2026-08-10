/* try_move_x64.S — full sk_try_move for x86-64
 *
 * Matches ../asm_common/game.c (same SkGame layout / semantics).
 *
 * ABI (selected at assemble time):
 *   Windows / MinGW (_WIN64):  g=rcx, dx=edx, dy=r8d  → eax
 *   System V (Linux/macOS):    g=rdi, dx=esi, dy=edx  → eax
 *
 * Build (this machine, MinGW):
 *   gcc -c try_move_x64.S -o try_move_x64.o
 *   gcc -O2 -DSK_USE_ASM_TRY_MOVE -o sokoban \
 *       ../asm_common/host_main.c ../asm_common/game.c try_move_x64.o -I../asm_common
 *
 * Offsets (game.h):
 *   0 map[32*32], 1024 width, 1028 height, 1032 px, 1036 py,
 *   1040 moves, 1044 won, 1048 hist_n, 1052 hist[256] (28 bytes/entry)
 *   map index = y * 32 + x
 */
        .text
        .globl  sk_try_move
#if defined(_WIN32) || defined(__CYGWIN__)
        .def    sk_try_move; .scl 2; .type 32; .endef
#else
        .type   sk_try_move, @function
#endif
sk_try_move:
        pushq   %rbx
        pushq   %rbp
        pushq   %r12
        pushq   %r13
        pushq   %r14
        pushq   %r15

#if defined(_WIN64) || (defined(_WIN32) && defined(__x86_64__))
        movq    %rcx, %r12              /* g */
        movslq  %edx, %r13              /* dx */
        movslq  %r8d, %r14              /* dy */
#else
        movq    %rdi, %r12
        movslq  %esi, %r13
        movslq  %edx, %r14
#endif

        /* if (g->won) return 0 */
        cmpl    $0, 1044(%r12)
        jne     .Lfail

        /* nx = px+dx, ny = py+dy */
        movl    1032(%r12), %r15d
        addl    %r13d, %r15d            /* nx */
        movl    1036(%r12), %ebp
        addl    %r14d, %ebp             /* ny */

        /* ch = at(nx, ny) → ebx */
        movl    %r15d, %edi
        movl    %ebp, %esi
        /* inline at */
        cmpl    $0, %edi
        jl      .Lat_wall1
        cmpl    $0, %esi
        jl      .Lat_wall1
        cmpl    1024(%r12), %edi
        jge     .Lat_wall1
        cmpl    1028(%r12), %esi
        jge     .Lat_wall1
        movslq  %esi, %rax
        shlq    $5, %rax
        movslq  %edi, %rcx
        addq    %rcx, %rax
        movzbl  (%r12,%rax), %ebx
        jmp     .Lat_done1
.Lat_wall1:
        movl    $35, %ebx               /* '#' */
.Lat_done1:

        cmpl    $35, %ebx
        je      .Lfail
        cmpl    $36, %ebx               /* '$' */
        je      .Lpush
        cmpl    $42, %ebx               /* '*' */
        je      .Lpush

        /* ---- walk ---- */
        cmpl    $256, 1048(%r12)
        jge     .Lfail
        movl    1048(%r12), %eax
        imull   $28, %eax, %ecx
        leaq    1052(%r12,%rcx), %rcx
        movl    1032(%r12), %eax
        movl    %eax, (%rcx)
        movl    1036(%r12), %eax
        movl    %eax, 4(%rcx)
        movl    $0, 24(%rcx)
        addl    $1, 1048(%r12)
        movl    %r15d, 1032(%r12)
        movl    %ebp, 1036(%r12)
        movl    $1, %eax
        jmp     .Lret

.Lpush:
        /* bx = nx+dx, by = ny+dy  → r8d, r9d */
        movl    %r15d, %r8d
        addl    %r13d, %r8d
        movl    %ebp, %r9d
        addl    %r14d, %r9d

        /* ch = at(bx, by) */
        movl    %r8d, %edi
        movl    %r9d, %esi
        cmpl    $0, %edi
        jl      .Lat_wall2
        cmpl    $0, %esi
        jl      .Lat_wall2
        cmpl    1024(%r12), %edi
        jge     .Lat_wall2
        cmpl    1028(%r12), %esi
        jge     .Lat_wall2
        movslq  %esi, %rax
        shlq    $5, %rax
        movslq  %edi, %rcx
        addq    %rcx, %rax
        movzbl  (%r12,%rax), %eax
        jmp     .Lat_done2
.Lat_wall2:
        movl    $35, %eax
.Lat_done2:

        cmpl    $35, %eax
        je      .Lfail
        cmpl    $36, %eax
        je      .Lfail
        cmpl    $42, %eax
        je      .Lfail
        cmpl    $256, 1048(%r12)
        jge     .Lfail

        /* hist push */
        movl    1048(%r12), %eax
        imull   $28, %eax, %ecx
        leaq    1052(%r12,%rcx), %rcx
        movl    1032(%r12), %eax
        movl    %eax, (%rcx)
        movl    1036(%r12), %eax
        movl    %eax, 4(%rcx)
        movl    %r15d, 8(%rcx)
        movl    %ebp, 12(%rcx)
        movl    %r8d, 16(%rcx)
        movl    %r9d, 20(%rcx)
        movl    $1, 24(%rcx)
        addl    $1, 1048(%r12)

        /* setc(nx,ny, *?'.':' ') */
        movslq  %ebp, %rax
        shlq    $5, %rax
        movslq  %r15d, %rcx
        addq    %rcx, %rax
        movzbl  (%r12,%rax), %edx
        cmpl    $42, %edx
        movl    $46, %edx               /* '.' */
        movl    $32, %ecx               /* ' ' */
        cmovne  %ecx, %edx
        movb    %dl, (%r12,%rax)

        /* setc(bx,by, .?'*':'$') */
        movslq  %r9d, %rax
        shlq    $5, %rax
        movslq  %r8d, %rcx
        addq    %rcx, %rax
        movzbl  (%r12,%rax), %edx
        cmpl    $46, %edx
        movl    $42, %edx               /* '*' */
        movl    $36, %ecx               /* '$' */
        cmovne  %ecx, %edx
        movb    %dl, (%r12,%rax)

        movl    %r15d, 1032(%r12)
        movl    %ebp, 1036(%r12)
        addl    $1, 1040(%r12)

        /* check_win */
        movl    $1, 1044(%r12)
        xorl    %esi, %esi              /* y */
.Lcy:
        cmpl    1028(%r12), %esi
        jge     .Lcw_done
        xorl    %edi, %edi
.Lcx:
        cmpl    1024(%r12), %edi
        jge     .Lcx_done
        movslq  %esi, %rax
        shlq    $5, %rax
        movslq  %edi, %rcx
        addq    %rcx, %rax
        cmpb    $36, (%r12,%rax)
        jne     1f
        movl    $0, 1044(%r12)
1:
        addl    $1, %edi
        jmp     .Lcx
.Lcx_done:
        addl    $1, %esi
        jmp     .Lcy
.Lcw_done:
        movl    $1, %eax
        jmp     .Lret

.Lfail:
        xorl    %eax, %eax
.Lret:
        popq    %r15
        popq    %r14
        popq    %r13
        popq    %r12
        popq    %rbp
        popq    %rbx
        ret
#if !defined(_WIN32) && !defined(__CYGWIN__)
        .size   sk_try_move, .-sk_try_move
#endif
