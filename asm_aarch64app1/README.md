# asm_aarch64app1 — AArch64 (ARM64) 推箱子汇编教学

**不强制在本仓库交叉编译**。完整可玩逻辑见 [`../asm_common`](../asm_common)（C 参考）。

## 工具

aarch64-linux-gnu-as / clang

## 本目录

| 文件 | 说明 |
|------|------|
| `try_move_aarch64.S` | 该 ISA 下 `try_move` **教学骨架 / 寄存器约定** |
| 可玩主机 | `../asm_common/host_main.c` + `game.c` |

## 寄存器速查（AAPCS64）

| 用途 | 寄存器 |
|------|--------|
| 参数 | x0–x7 |
| 返回 | x0 |
| 需保存 | x19–x28 |
| 链接 | x30 (lr) |

Apple Silicon / 现代 Android 手机主力 ISA。


## 算法对照

推箱 `try_move` 核心步骤（各 ISA 汇编应实现同一语义）：

1. 若已胜利则失败  
2. 计算 `nx,ny`；越界或墙则失败  
3. 若是箱子：检查前方；推箱并记 hist；`moves++`；判胜  
4. 否则走路并记 hist  

键位（C 主机）：WASD / z / r / q。
