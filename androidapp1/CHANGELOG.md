# Changelog / 更新日志

## 1.0.0 — 2026-08-02

### English

**New**
- First Android port of the 2D web app (`html_app`)
- Full level set from `levels.json` (bundled as `assets/levels.json`)
- Tap empty floor: BFS pathfinding to that cell
- Tap an adjacent box: push one step
- Virtual D-pad: tap and hold-to-repeat
- Undo (push steps only), reset, prev/next level
- View answer: play back built-in `solution` when present
- Win overlay with next level; last-level remembered

**UI**
- Compact icon toolbar (prev, level spinner, moves, undo, reset, answer, help, next) — no horizontal scrolling
- Icon D-pad and win “next” control
- Dark theme aligned with the web app

### 中文

**新增**
- 首次将 2D 网页版（`html_app`）移植为原生 Android
- 完整关卡（`levels.json` → `assets/levels.json`）
- 点击空地：BFS 寻路直达
- 点击相邻箱子：向前推一格
- 虚拟方向键：点按 / 长按连发
- 撤销（仅推箱步）、重置、上一关 / 下一关
- 查看答案：有 `solution` 时可动画回放
- 通关遮罩与下一关；记住上次关卡

**界面**
- 紧凑图标工具栏（上一关、关卡、步数、撤销、重置、答案、帮助、下一关），无横向滚动
- 方向键与通关「下一关」均为图标
- 深色主题，风格贴近网页版
