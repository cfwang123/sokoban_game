# asm_avrapp1 — AVR (8-bit MCU) 推箱子汇编教学

**不强制在本仓库交叉编译**。完整可玩逻辑见 [`../asm_common`](../asm_common)（C 参考）。

## 工具

avr-as / avr-gcc

## 本目录

| 文件 | 说明 |
|------|------|
| `try_move_avr.S` | 该 ISA 下 `try_move` **教学骨架 / 寄存器约定** |
| 可玩主机 | `../asm_common/host_main.c` + `game.c` |

## AVR 要点

- Arduino 底层即 AVR 汇编友好
- 数据/程序空间分离
- 适合对照 `arduinoapp1` 教学

主机可玩：

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
