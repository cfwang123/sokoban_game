# nvimext1 — Neovim Lua 推箱子（教学）

纯 Lua 实现：`:Sokoban` 打开 tab + buffer，hjkl 游玩。

## 安装

lazy.nvim 示例：

```lua
{
  dir = "/path/to/sokoban/nvimext1",
  name = "sokoban",
  lazy = false,
}
```

或：

```lua
vim.opt.rtp:prepend("/path/to/sokoban/nvimext1")
```

## 键位

与 `vimext1` 相同：`hjkl`、`u`、`r`、`n`/`p`、`q`。

## 对照

| Vim | Neovim |
|-----|--------|
| Vimscript autoload | `lua/sokoban/init.lua` |
| `nnoremap <buffer>` | `vim.keymap.set` |
| `setline` | `nvim_buf_set_lines` |
