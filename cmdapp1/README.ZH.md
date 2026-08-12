# cmdapp1 — Windows CMD 批处理推箱子（教学）

> [English](readme.md)


纯 **`cmd.exe` 批处理**，无需安装额外运行时。

## 运行

```bat
cd cmdapp1
main.cmd
```

或在资源管理器中双击 `main.cmd`。

键位：WASD 移动，z 撤销，r 重置，q 退出（输入后回车）。

## 实现说明

- 地图为长度 49 的字符串（7×7），下标 `y*7+x`
- 内部编码：`#` 墙、`.` 目标、`B` 箱子、`*` 箱在目标、`-` 空地（显示为空格）
- 避免 `$`/`*` 未加引号时在批处理中被当作通配符

## 对照

| 目录 | 环境 |
|------|------|
| `cmdapp1`（本目录） | Windows CMD / 批处理 |
| [`../powershellapp1`](../powershellapp1) | PowerShell |
| [`../bashapp1`](../bashapp1) | Bash |
