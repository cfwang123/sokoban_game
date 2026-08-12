# angularapp1 — Angular 推箱子（教学）

> [English](readme.md)


## 立刻可玩（不编译）

打开 **`play.html`**（或本地静态服务）：

```bash
cd angularapp1
python -m http.server 8767
# http://localhost:8767/play.html
```

## Angular 组件源码（对照学习）

| 路径 | 说明 |
|------|------|
| `src/app/game-core.ts` | 纯 TS 玩法 |
| `src/app/app.component.ts` | standalone `AppComponent` 模板 + 键盘 |

可选本机：`ng new` 后拷入上述文件并设为根组件，再 `ng serve`。**不要求在本仓库配置 Angular CLI。**

键位：WASD / 方向键，Z 撤销，R 重置。

对照：React [`../reactapp1`](../reactapp1) · Vue [`../vueapp1`](../vueapp1)
