# 用 Xcode 包装 Safari Web Extension

Safari 扩展 = **macOS/iOS App** + **Safari Web Extension** 目标。

## 步骤（Mac + Xcode 14+）

1. Xcode → File → New → Project → **Safari Extension App**（或多平台 App + 添加 Safari Extension）。  
2. 将本仓库 `safariext1/Resources/` 内容替换/同步到工程的 `Resources`（`manifest.json`、popup、icons、js）。  
3. 签名 Team、Bundle ID。  
4. Run：启动容器 App，在 Safari → 设置 → 扩展 中启用。  
5. 工具栏图标 → popup 游戏。

## 与 Chrome 差异

| | Chrome | Safari |
|--|--------|--------|
| 加载 | 解压目录 | 需 Xcode 签名包装 |
| API | `chrome.*` | WebExtensions + `browser.*` |
| 分发 | Chrome 商店 / 企业 | App Store / 公证 |

本仓库**只提供 Web 资源与说明**，不提交完整 `.xcodeproj`（避免绑定本机签名）。
