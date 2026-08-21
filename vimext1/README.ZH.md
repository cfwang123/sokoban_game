# vimext1 — Vim 推箱子插件（教学）

> [English](README.md)


Vimscript：`:Sokoban` 打开专用 buffer，hjkl 移动。

## 安装

```vim
set runtimepath+=/path/to/sokoban/vimext1
```

或链到 `~/.vim/pack/plugins/start/sokoban`。

## 命令

| 命令 | 说明 |
|------|------|
| `:Sokoban` | 开始游戏 |

缓冲区内：`hjkl`/`方向键` 移动，`u` 撤销，`r` 重置，`n`/`p` 换关，`q` 关闭。
