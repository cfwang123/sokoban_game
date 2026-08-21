# jsfuckapp1 — 纯 JSFuck 可玩推箱子

> [English](README.md)


[JSFuck](https://jsfuck.com/)：只用 **`[]()!+`** 六个字符写合法 JavaScript。  
**整局游戏**编码为纯 JSFuck；`main.py` / `play.html` 只负责启动，不写玩法。

## 检查结果（可玩）

```bash
cd jsfuckapp1
node generate.js --check   # 重新编码 + 推一步烟雾测试
python -X utf8 main.py --test
python -X utf8 main.py     # 或: node sokoban.jsfuck.js
```

键位：WASD 移动，`z` 撤销，`r` 重置，`q` 退出。

浏览器：打开 `play.html`（加载 `sokoban.browser.jsfuck.js`）。

## 文件

| 文件 | 说明 |
|------|------|
| **`sokoban.jsfuck.js`** | 纯 JSFuck 终端游戏（Node 执行） |
| **`sokoban.browser.jsfuck.js`** | 纯 JSFuck 浏览器游戏 |
| `game_src.js` | 可读 Node 源（维护用） |
| `game_src_browser.js` | 可读浏览器源（维护用） |
| `jsfuck_lib.js` | 编码器 |
| `generate.js` | 从可读源生成纯 JSFuck |
| `main.py` | 启动器 / `--test` / `--rebuild` |

## 生成

```bash
node generate.js --check
# 或
python -X utf8 main.py --rebuild
```

## 说明

- 可读源**不使用** `require`（JSFuck 的 `eval` 作用域里没有 `require`），Node 版用 `process.stdin`。
- 关卡为标准 7×7 迷你图（含 `# $$$ #`）。
- 纯度：生成物仅含 `[]()!+`（及换行空白，加载时忽略空白亦可）。
