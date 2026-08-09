#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pygameapp1 — 推箱子图形版（仿 html_app 2D）。

配色、操作与网页版对齐：方向键/WASD、点击寻路、撤销推箱、答案回放等。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import pygame
except ImportError:
    print("需要 pygame：pip install pygame")
    sys.exit(1)

from game import GameState, cell_key, find_path

# ---- 与 html_app 对齐的常量 ----
CELL = 40
PADDING = 20
TOOLBAR_H = 52
FOOTER_H = 40
HOLD_DELAY_MS = 180
HOLD_INTERVAL_MS = 90
ANIM_INTERVAL_MS = 60

# 颜色（html_app / style.css）
COL_BG = (26, 26, 46)           # #1a1a2e
COL_PANEL = (22, 33, 62)        # #16213e
COL_FLOOR = (58, 58, 85)        # #3a3a55
COL_FLOOR_LINE = (68, 68, 102)  # #444466
COL_WALL = (74, 74, 106)        # #4a4a6a
COL_WALL_HI = (90, 90, 122)     # #5a5a7a
COL_WALL_SH = (42, 42, 74)      # #2a2a4a
COL_GOAL = (233, 69, 96)        # #e94560
COL_GOAL_RING = (255, 107, 129) # #ff6b81
COL_BOX = (243, 156, 18)        # #f39c12
COL_BOX_EDGE = (230, 126, 34)   # #e67e22
COL_BOX_HI = (245, 176, 65)     # #f5b041
COL_BOX_MARK = (211, 84, 0)     # #d35400
COL_BOX_ON = (46, 204, 113)     # #2ecc71
COL_BOX_ON_EDGE = (39, 174, 96) # #27ae60
COL_BOX_ON_HI = (88, 214, 141)  # #58d68d
COL_BOX_ON_MARK = (30, 132, 73) # #1e8449
COL_PLAYER = (52, 152, 219)     # #3498db
COL_PLAYER_EDGE = (41, 128, 185)  # #2980b9
COL_TEXT = (238, 238, 238)      # #eee
COL_ACCENT = (233, 69, 96)      # #e94560
COL_BTN = (15, 52, 96)          # #0f3460
COL_BTN_BORDER = (83, 52, 131)  # #533483
COL_OVERLAY = (0, 0, 0, 160)


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def load_levels() -> List[Dict[str, Any]]:
    """优先加载仓库根 levels.json，失败则用内置演示关。"""
    candidates = [
        script_dir() / "levels.json",
        script_dir().parent / "levels.json",
    ]
    for p in candidates:
        if p.is_file():
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                return data
    return [
        {
            "id": 0,
            "name": "Demo",
            "puzzle": [
                "#######",
                "#. . .#",
                "# $$$ #",
                "#.$@$.#",
                "# $$$ #",
                "#. . .#",
                "#######",
            ],
            "solution": None,
        }
    ]


def last_level_path() -> Path:
    return script_dir() / "lastlevel.ini"


def load_last_level(n: int) -> int:
    p = last_level_path()
    if not p.is_file():
        return 0
    try:
        text = p.read_text(encoding="utf-8").strip()
        idx = int(text)
        if 0 <= idx < n:
            return idx
    except (ValueError, OSError):
        pass
    return 0


def save_last_level(index: int) -> None:
    try:
        last_level_path().write_text(str(index), encoding="utf-8")
    except OSError:
        pass


class SokobanApp:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("推箱子 — pygameapp1 (仿 html_app)")
        self.levels = load_levels()
        self.level_index = load_last_level(len(self.levels))
        self.state: Optional[GameState] = None
        self.font = pygame.font.SysFont("microsoftyahei,simhei,segoeui,arial", 18)
        self.font_lg = pygame.font.SysFont("microsoftyahei,simhei,segoeui,arial", 28, bold=True)
        self.font_sm = pygame.font.SysFont("microsoftyahei,simhei,segoeui,arial", 14)

        # 动画 / 答案
        self.anim_queue: List[Tuple[int, int]] = []
        self.anim_timer = 0
        self.input_locked = False
        self.ai_active = False

        # 按住方向键连发
        self.hold_dir: Optional[Tuple[int, int]] = None
        self.hold_key: Optional[int] = None
        self.hold_first_at = 0
        self.hold_last_at = 0
        self.hold_started = False

        self.show_help = False
        self.board_offset = (PADDING, TOOLBAR_H + PADDING)

        self.screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.load_level(self.level_index)

    def load_level(self, index: int) -> None:
        if index < 0 or index >= len(self.levels):
            return
        self.stop_ai()
        self.clear_anim()
        raw = self.levels[index]
        puzzle = raw.get("puzzle") or []
        self.state = GameState.from_rows(list(puzzle), index)
        self.level_index = index
        save_last_level(index)
        self.resize_window()

    def reset_level(self) -> None:
        if self.state is None:
            return
        self.load_level(self.state.level_index)

    def clear_anim(self) -> None:
        self.anim_queue = []
        self.anim_timer = 0
        self.input_locked = False

    def stop_ai(self) -> None:
        self.ai_active = False
        self.clear_anim()

    def has_solution(self, index: int) -> bool:
        sol = self.levels[index].get("solution")
        return bool(sol and str(sol).strip())

    def solution_queue(self, index: int) -> List[Tuple[int, int]]:
        sol = self.levels[index].get("solution") or ""
        mapping = {
            "U": (0, -1),
            "D": (0, 1),
            "L": (-1, 0),
            "R": (1, 0),
        }
        out: List[Tuple[int, int]] = []
        for ch in str(sol):
            d = mapping.get(ch.upper())
            if d:
                out.append(d)
        return out

    def start_answer(self) -> None:
        if self.state is None or self.state.won:
            return
        if not self.has_solution(self.state.level_index):
            return
        self.reset_level()
        queue = self.solution_queue(self.state.level_index)
        if not queue:
            return
        self.ai_active = True
        self.anim_queue = queue
        self.input_locked = True
        self.anim_timer = 0

    def toggle_answer(self) -> None:
        if self.ai_active:
            self.stop_ai()
        else:
            self.start_answer()

    def resize_window(self) -> None:
        if self.state is None:
            return
        w = self.state.width * CELL + PADDING * 2
        h = self.state.height * CELL + PADDING * 2 + TOOLBAR_H + FOOTER_H
        w = max(w, 420)
        h = max(h, 360)
        self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        self.board_offset = (PADDING, TOOLBAR_H + PADDING)

    def try_move(self, dx: int, dy: int) -> bool:
        if self.state is None or self.input_locked:
            return False
        return self.state.try_move(dx, dy)

    def undo(self) -> None:
        if self.state is None or self.input_locked or self.ai_active:
            return
        self.state.undo()

    def board_pixel_to_cell(self, mx: int, my: int) -> Optional[Tuple[int, int]]:
        ox, oy = self.board_offset
        gx = (mx - ox) // CELL
        gy = (my - oy) // CELL
        if self.state is None:
            return None
        if gx < 0 or gy < 0 or gx >= self.state.width or gy >= self.state.height:
            return None
        return int(gx), int(gy)

    def on_click(self, mx: int, my: int) -> None:
        if self.state is None or self.state.won or self.input_locked or self.ai_active:
            return
        cell = self.board_pixel_to_cell(mx, my)
        if cell is None:
            return
        gx, gy = cell
        gk = cell_key(gx, gy)
        # 点相邻箱子 → 推一格
        if gk in self.state.boxes:
            dx = gx - self.state.player[0]
            dy = gy - self.state.player[1]
            if abs(dx) + abs(dy) == 1:
                self.try_move(dx, dy)
            return
        # 点空地 → BFS 瞬时走完
        if gk not in self.state.walls and gk not in self.state.boxes:
            path = find_path(self.state, gx, gy)
            if path:
                for dx, dy in path:
                    self.state.try_move(dx, dy)
                    if self.state.won:
                        break

    def clear_hold(self) -> None:
        self.hold_dir = None
        self.hold_key = None
        self.hold_started = False

    def start_hold(self, key: int, dx: int, dy: int) -> None:
        now = pygame.time.get_ticks()
        self.try_move(dx, dy)
        self.hold_dir = (dx, dy)
        self.hold_key = key
        self.hold_first_at = now
        self.hold_last_at = now
        self.hold_started = False

    def update_hold(self) -> None:
        if self.hold_dir is None or self.input_locked or self.ai_active:
            return
        now = pygame.time.get_ticks()
        if not self.hold_started:
            if now - self.hold_first_at >= HOLD_DELAY_MS:
                self.hold_started = True
                self.hold_last_at = now
                self.try_move(*self.hold_dir)
        else:
            if now - self.hold_last_at >= HOLD_INTERVAL_MS:
                self.hold_last_at = now
                self.try_move(*self.hold_dir)

    def update_anim(self, dt_ms: int) -> None:
        if not self.anim_queue or self.state is None:
            return
        self.anim_timer += dt_ms
        while self.anim_timer >= ANIM_INTERVAL_MS and self.anim_queue:
            self.anim_timer -= ANIM_INTERVAL_MS
            dx, dy = self.anim_queue.pop(0)
            self.state.try_move(dx, dy)
            if self.state.won:
                self.anim_queue = []
                break
        if not self.anim_queue:
            self.input_locked = False
            if self.ai_active:
                self.ai_active = False

    def draw_board(self, surf: pygame.Surface) -> None:
        if self.state is None:
            return
        ox, oy = self.board_offset
        st = self.state
        # 地板
        for y in range(st.height):
            for x in range(st.width):
                px = ox + x * CELL
                py = oy + y * CELL
                pygame.draw.rect(surf, COL_FLOOR, (px, py, CELL, CELL))
                pygame.draw.rect(surf, COL_FLOOR_LINE, (px, py, CELL, CELL), 1)

        # 墙
        for k in st.walls:
            x, y = map(int, k.split(","))
            px = ox + x * CELL
            py = oy + y * CELL
            pygame.draw.rect(surf, COL_WALL, (px, py, CELL, CELL))
            pygame.draw.rect(surf, COL_WALL_HI, (px, py, CELL, 3))
            pygame.draw.rect(surf, COL_WALL_HI, (px, py, 3, CELL))
            pygame.draw.rect(surf, COL_WALL_SH, (px, py + CELL - 3, CELL, 3))
            pygame.draw.rect(surf, COL_WALL_SH, (px + CELL - 3, py, 3, CELL))

        # 目标点
        for k in st.goals:
            x, y = map(int, k.split(","))
            cx = ox + x * CELL + CELL // 2
            cy = oy + y * CELL + CELL // 2
            pygame.draw.circle(surf, COL_GOAL, (cx, cy), 6)
            pygame.draw.circle(surf, COL_GOAL_RING, (cx, cy), 6, 2)

        # 箱子
        for k in st.boxes:
            x, y = map(int, k.split(","))
            px = ox + x * CELL + 4
            py = oy + y * CELL + 4
            size = CELL - 8
            on_goal = k in st.goals
            fill = COL_BOX_ON if on_goal else COL_BOX
            edge = COL_BOX_ON_EDGE if on_goal else COL_BOX_EDGE
            hi = COL_BOX_ON_HI if on_goal else COL_BOX_HI
            mark = COL_BOX_ON_MARK if on_goal else COL_BOX_MARK
            pygame.draw.rect(surf, fill, (px, py, size, size))
            pygame.draw.rect(surf, edge, (px, py, size, size), 2)
            pygame.draw.rect(surf, hi, (px + 2, py + 2, size - 4, 3))
            pygame.draw.rect(surf, hi, (px + 2, py + 2, 3, size - 4))
            cx = px + size // 2
            cy = py + size // 2
            pygame.draw.line(surf, mark, (cx - 6, cy), (cx + 6, cy), 2)
            pygame.draw.line(surf, mark, (cx, cy - 6), (cx, cy + 6), 2)

        # 玩家
        px, py = st.player
        cx = ox + px * CELL + CELL // 2
        cy = oy + py * CELL + CELL // 2
        r = int(CELL * 0.35)
        pygame.draw.circle(surf, COL_PLAYER, (cx, cy), r)
        pygame.draw.circle(surf, COL_PLAYER_EDGE, (cx, cy), r, 2)
        pygame.draw.circle(surf, (255, 255, 255), (cx - 4, cy - 3), 3)
        pygame.draw.circle(surf, (255, 255, 255), (cx + 4, cy - 3), 3)
        pygame.draw.circle(surf, COL_BG, (cx - 4, cy - 3), 2)
        pygame.draw.circle(surf, COL_BG, (cx + 4, cy - 3), 2)

    def draw_toolbar(self, surf: pygame.Surface) -> None:
        pygame.draw.rect(surf, COL_PANEL, (0, 0, surf.get_width(), TOOLBAR_H))
        name = ""
        if 0 <= self.level_index < len(self.levels):
            name = self.levels[self.level_index].get("name") or ""
        title = f"第 {self.level_index + 1}/{len(self.levels)} 关"
        if name:
            title += f" · {name}"
        moves = self.state.moves if self.state else 0
        line1 = self.font.render(title, True, COL_ACCENT)
        line2 = self.font_sm.render(
            f"步数: {moves}    [Z]撤销 [R]重置 [N/P]关卡 [F1]答案 [H]帮助",
            True,
            COL_TEXT,
        )
        surf.blit(line1, (12, 6))
        surf.blit(line2, (12, 28))

    def draw_footer(self, surf: pygame.Surface) -> None:
        y = surf.get_height() - FOOTER_H
        pygame.draw.rect(surf, COL_PANEL, (0, y, surf.get_width(), FOOTER_H))
        status = ""
        if self.ai_active:
            status = f"执行答案中...（剩余 {len(self.anim_queue)} 步）"
        elif self.state and self.state.won:
            status = "已过关 — 按空格进入下一关"
        elif self.state and self.has_solution(self.state.level_index):
            status = "本关有答案 · 点击空地可寻路"
        else:
            status = "本关暂无答案 · 点击空地可寻路"
        text = self.font_sm.render(status, True, COL_TEXT)
        surf.blit(text, (12, y + 12))

    def draw_win_overlay(self, surf: pygame.Surface) -> None:
        if self.state is None or not self.state.won:
            return
        overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        overlay.fill(COL_OVERLAY)
        surf.blit(overlay, (0, 0))
        box_w, box_h = 280, 140
        bx = (surf.get_width() - box_w) // 2
        by = (surf.get_height() - box_h) // 2
        pygame.draw.rect(surf, COL_PANEL, (bx, by, box_w, box_h), border_radius=12)
        pygame.draw.rect(surf, COL_BTN_BORDER, (bx, by, box_w, box_h), 2, border_radius=12)
        t1 = self.font_lg.render("恭喜过关！", True, COL_ACCENT)
        t2 = self.font.render(f"共用 {self.state.moves} 步完成", True, COL_TEXT)
        t3 = self.font_sm.render("空格 / 点击继续下一关", True, COL_TEXT)
        surf.blit(t1, (bx + (box_w - t1.get_width()) // 2, by + 24))
        surf.blit(t2, (bx + (box_w - t2.get_width()) // 2, by + 68))
        surf.blit(t3, (bx + (box_w - t3.get_width()) // 2, by + 100))

    def draw_help(self, surf: pygame.Surface) -> None:
        if not self.show_help:
            return
        overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        overlay.fill(COL_OVERLAY)
        surf.blit(overlay, (0, 0))
        lines = [
            "快捷键",
            "方向键 / WASD — 移动",
            "Z — 撤销推箱",
            "R — 重置本关",
            "F1 — 查看/停止答案",
            "PageUp / P — 上一关",
            "PageDown / N — 下一关",
            "空格 — 通关后下一关",
            "H — 关闭本帮助",
            "点击空地 — BFS 寻路",
            "点击邻箱 — 推一格",
        ]
        box_w, box_h = 320, 28 + len(lines) * 22
        bx = (surf.get_width() - box_w) // 2
        by = (surf.get_height() - box_h) // 2
        pygame.draw.rect(surf, COL_PANEL, (bx, by, box_w, box_h), border_radius=12)
        pygame.draw.rect(surf, COL_BTN_BORDER, (bx, by, box_w, box_h), 2, border_radius=12)
        for i, line in enumerate(lines):
            color = COL_ACCENT if i == 0 else COL_TEXT
            font = self.font if i == 0 else self.font_sm
            t = font.render(line, True, color)
            surf.blit(t, (bx + 20, by + 12 + i * 22))

    def next_level(self) -> None:
        if self.level_index + 1 < len(self.levels):
            self.load_level(self.level_index + 1)

    def prev_level(self) -> None:
        if self.level_index > 0:
            self.load_level(self.level_index - 1)

    def handle_keydown(self, e: pygame.event.Event) -> None:
        if e.key == pygame.K_h:
            self.show_help = not self.show_help
            return
        if self.show_help:
            if e.key in (pygame.K_ESCAPE, pygame.K_h):
                self.show_help = False
            return

        if e.key == pygame.K_z:
            self.undo()
            return
        if e.key == pygame.K_r:
            self.reset_level()
            return
        if e.key == pygame.K_F1:
            self.toggle_answer()
            return
        if e.key == pygame.K_SPACE:
            if self.state and self.state.won:
                self.next_level()
            return
        if e.key in (pygame.K_PAGEUP, pygame.K_p):
            self.prev_level()
            return
        if e.key in (pygame.K_PAGEDOWN, pygame.K_n):
            self.next_level()
            return

        key_map = {
            pygame.K_UP: (0, -1),
            pygame.K_w: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_s: (0, 1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_a: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_d: (1, 0),
        }
        d = key_map.get(e.key)
        if d is None:
            return
        if self.input_locked or self.ai_active:
            return
        self.start_hold(e.key, d[0], d[1])

    def handle_keyup(self, e: pygame.event.Event) -> None:
        if self.hold_key == e.key:
            self.clear_hold()

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(60)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    self.handle_keydown(e)
                elif e.type == pygame.KEYUP:
                    self.handle_keyup(e)
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if self.show_help:
                        self.show_help = False
                    elif self.state and self.state.won:
                        self.next_level()
                    else:
                        self.on_click(*e.pos)
                elif e.type == pygame.VIDEORESIZE:
                    # 保持可拉伸，棋盘仍按关卡尺寸居中偏左上
                    pass

            self.update_hold()
            self.update_anim(dt)

            self.screen.fill(COL_BG)
            self.draw_toolbar(self.screen)
            self.draw_board(self.screen)
            self.draw_footer(self.screen)
            self.draw_win_overlay(self.screen)
            self.draw_help(self.screen)
            pygame.display.flip()

        pygame.quit()


def main() -> None:
    # Windows 下避免控制台编码问题
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    app = SokobanApp()
    app.run()


if __name__ == "__main__":
    main()
