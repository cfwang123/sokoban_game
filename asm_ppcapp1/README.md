# asm_ppcapp1 — PowerPC / Power ISA 推箱子汇编教学

**不强制在本仓库交叉编译**。完整可玩逻辑见 [`../asm_common`](../asm_common)（C 参考）。

## 工具

powerpc-linux-gnu-as / IBM XL

## 本目录

| 文件 | 说明 |
|------|------|
| `try_move_ppc.S` | 该 ISA 下 `try_move` **教学骨架 / 寄存器约定** |
| 可玩主机 | `../asm_common/host_main.c` + `game.c` |

## 寄存器速查（Power ABI 概要）

| 用途 | 寄存器 |
|------|--------|
| 参数 | r3–r10 |
| 返回 | r3 |
| 链接 | lr |

常见于旧 Mac、部分嵌入式与游戏主机历史资料。


## 算法对照

推箱 `try_move` 核心步骤（各 ISA 汇编应实现同一语义）：

1. 若已胜利则失败  
2. 计算 `nx,ny`；越界或墙则失败  
3. 若是箱子：检查前方；推箱并记 hist；`moves++`；判胜  
4. 否则走路并记 hist  

键位（C 主机）：WASD / z / r / q。
