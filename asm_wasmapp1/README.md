# asm_wasmapp1 — WebAssembly（WAT）推箱子教学

**WebAssembly Text Format** 可视为一种“汇编”：线性内存 + 导出函数。

## 立刻可玩（无需编译）

打开 `index.html`（建议本地 HTTP）：

```bash
cd asm_wasmapp1
python -m http.server 8790
# http://localhost:8790/
```

- 交互由 `main.js` 主机完成（与 `sokoban.wat` **同语义**，保证无 wabt 也能玩）
- **`sokoban.wat`**：完整 WAT 源码，可用 [wabt](https://github.com/WebAssembly/wabt) `wat2wasm` 或 `wasmtime` 学习

```bash
# 可选：
wat2wasm sokoban.wat -o sokoban.wasm
wasmtime sokoban.wasm   # 需自行写宿主调用 export
```

键位：WASD / 方向键，Z 撤销，R 重置。

## 对照

| 目录 | ISA |
|------|-----|
| [`../asm_x64app1`](../asm_x64app1) | x86-64 原生汇编骨架 |
| [`../asm_common`](../asm_common) | C 参考实现 |
| `asm_wasmapp1`（本目录） | WASM / WAT |
