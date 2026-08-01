# wxgame1 — 微信小游戏推箱子（教学）

Canvas 2D + 触摸虚拟键 + 点击寻路。用**微信开发者工具**打开本目录（appid 测试号）。

```
wxgame1/
  game.js           # 入口
  game.json
  project.config.json
  js/game.js        # 逻辑
  js/levels_mini.js # 迷你关卡
```

对照 `html_app`：同为 JS Canvas，API 换成 `wx.createCanvas` / `wx.onTouchEnd`。
