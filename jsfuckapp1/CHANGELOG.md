# Changelog

## 2026-08-10

- **可玩修复**：去掉 `require('readline')`（eval 中无 require），改用 `process.stdin`
- 修正关卡字符串为 `# $$$ #`（原先误为 `# $ #`）
- `generate.js --check`：编码 Node/浏览器两套纯 JSFuck 并烟雾测试推箱
- `main.py --test`：纯度 + 启动 + `moves=1` 推箱
