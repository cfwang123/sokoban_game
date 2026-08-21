# vscodeext1 — VS Code 推箱子扩展（教学）

> [English](README.md)


命令面板运行 **「Sokoban: Open Game」**，在 Webview 中游玩。

## 开发

```bash
cd vscodeext1
npm install
npm run compile
```

在 VS Code 中：`F5` 启动「扩展开发主机」，执行命令 `Sokoban: Open Game`。

## 结构

```
package.json          # 扩展清单
src/extension.ts      # activate + Webview HTML
tsconfig.json
```

本仓库可不安装 npm；源码可直接阅读。打包可用 `vsce package`（需 devDependency）。
