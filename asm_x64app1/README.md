# asm_x64app1 — x86-64 (AMD64) System V 推箱子汇编教学

**不强制在本仓库交叉编译**。完整可玩逻辑见 [`../asm_common`](../asm_common)（C 参考）。

## 工具

gcc / as / gas（Linux/macOS/WSL）；Windows 可用 MinGW

## 本目录

| 文件 | 说明 |
|------|------|
| `try_move_x64.s` | 该 ISA 下 `try_move` **教学骨架 / 寄存器约定** |
| 可玩主机 | `../asm_common/host_main.c` + `game.c` |

## 寄存器速查（System V AMD64）

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


## 算法对照

推箱 `try_move` 核心步骤（各 ISA 汇编应实现同一语义）：

1. 若已胜利则失败  
2. 计算 `nx,ny`；越界或墙则失败  
3. 若是箱子：检查前方；推箱并记 hist；`moves++`；判胜  
4. 否则走路并记 hist  

键位（C 主机）：WASD / z / r / q。
