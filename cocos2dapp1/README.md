# cocos2dapp1 — Cocos2d 风格推箱子（教学）

**无需安装 Cocos Creator**：浏览器打开 `index.html`，用 Canvas + 简易 Director/Layer 循环演示 2D 引擎结构。

```bash
cd cocos2dapp1
python -m http.server 8768
# http://localhost:8768/
```

| 概念 | 本教学映射 |
|------|------------|
| Director | `Director.runScene` |
| Layer / Scene | `GameLayer` |
| scheduleUpdate | `requestAnimationFrame` → `update`/`draw` |
| 输入 | `keydown` |

玩法核心在 `js/game-core.js`，可迁入 **Cocos Creator** 的 `cc.Component` 脚本。

键位：WASD / 方向键，Z 撤销，R 重置。
