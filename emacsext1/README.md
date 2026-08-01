# emacsext1 — Emacs 推箱子（教学）

单文件 `sokoban.el`：`M-x sokoban`。

## 安装

```elisp
(add-to-list 'load-path "/path/to/sokoban/emacsext1")
(require 'sokoban)
;; 或 (load "sokoban.el")
```

## 键位

| 键 | 功能 |
|----|------|
| h/j/k/l 或方向键 | 移动 |
| u | 撤销推箱 |
| r | 重置 |
| n / p | 下/上一关 |
| q | 关闭缓冲 |

对照：`vimext1` / `nvimext1`（同为编辑器 buffer 游戏）。
