# asm_loongarchapp1 — LoongArch（龙芯） 推箱子汇编教学

**不强制在本仓库交叉编译**。完整可玩逻辑见 [`../asm_common`](../asm_common)（C 参考）。

## 工具

loongarch64-unknown-linux-gnu-as / 龙芯工具链

## 本目录

| 文件 | 说明 |
|------|------|
| `try_move_loongarch.S` | 该 ISA 下 `try_move` **教学骨架 / 寄存器约定** |
| 可玩主机 | `../asm_common/host_main.c` + `game.c` |

## LoongArch 要点

- 龙芯自主指令集
- Linux 主线已支持
- 对照 RISC-V / MIPS 学习调用约定差异


## 算法对照

推箱 `try_move` 核心步骤（各 ISA 汇编应实现同一语义）：

1. 若已胜利则失败  
2. 计算 `nx,ny`；越界或墙则失败  
3. 若是箱子：检查前方；推箱并记 hist；`moves++`；判胜  
4. 否则走路并记 hist  

键位（C 主机）：WASD / z / r / q。
