# asm_riscvapp1 — RISC-V (RV32/RV64) 推箱子汇编教学

**不强制在本仓库交叉编译**。完整可玩逻辑见 [`../asm_common`](../asm_common)（C 参考）。

## 工具

riscv64-unknown-elf-as / clang --target=riscv64

## 本目录

| 文件 | 说明 |
|------|------|
| `try_move_riscv.S` | 该 ISA 下 `try_move` **教学骨架 / 寄存器约定** |
| 可玩主机 | `../asm_common/host_main.c` + `game.c` |

## 寄存器速查（RISC-V 调用约定）

| 用途 | 寄存器 |
|------|--------|
| 参数 | a0–a7 |
| 返回 | a0 |
| 需保存 | s0–s11 |
| 返回地址 | ra |

```bash
cc -O2 -o sokoban ../asm_common/host_main.c ../asm_common/game.c
```


## 算法对照

推箱 `try_move` 核心步骤（各 ISA 汇编应实现同一语义）：

1. 若已胜利则失败  
2. 计算 `nx,ny`；越界或墙则失败  
3. 若是箱子：检查前方；推箱并记 hist；`moves++`；判胜  
4. 否则走路并记 hist  

键位（C 主机）：WASD / z / r / q。
