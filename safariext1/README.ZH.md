# safariext1 — Safari 扩展推箱子（教学）

> [English](README.md)


**Safari Web Extension** 资源（Manifest V3 popup），玩法同 `chromeext1`。

## 目录

```
Resources/
  manifest.json
  popup.html / popup.css
  js/game.js / js/popup.js
  icons/
docs/XCODE.md          # 如何用 Xcode 包装
```

## 运行

必须在 **Mac + Xcode** 中创建 Safari Extension App，把 `Resources/` 放进工程（见 `docs/XCODE.md`）。  
Windows 上可阅读源码，无法本地加载到 Safari。

键位：方向键/WASD、点空地寻路、Z 撤销、R 重置。
