# chromeext1 — Chrome 扩展推箱子（教学）

> [English](readme.md)


Manifest V3 · popup 画布 · `chrome.storage` 记关卡。

## 加载

1. 打开 `chrome://extensions`  
2. 开启「开发者模式」  
3. 「加载已解压的扩展程序」→ 选择本目录  

点击工具栏图标打开游戏。方向键/WASD，点击空地寻路。

## 结构

```
manifest.json
popup.html / popup.css
js/game.js   # 逻辑
js/popup.js  # UI
icons/
```
