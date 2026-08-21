# firefoxext1 — Firefox 扩展推箱子（教学）

> [English](README.md)


WebExtensions · Manifest V3（gecko id 见 `manifest.json`）。

## 加载

1. `about:debugging#/runtime/this-firefox`  
2. 「临时载入附加组件」→ 选本目录的 `manifest.json`  

或用 `web-ext run`（需 npm `web-ext`）。

与 Chrome 差异：`browser_specific_settings.gecko`；存储 API 在 Firefox 中兼容 `browser.storage` / `chrome.storage` 垫片。本 demo 使用 `chrome.storage`（Firefox 提供兼容）。
