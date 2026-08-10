#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pyqtapp1 — PyQt5/PyQt6 推箱子（教学）

不强制本仓库编译。本机有 PyQt 时可直接运行:

  pip install PyQt5
  python -X utf8 main.py

优先 PyQt5，其次 PyQt6 / PySide6。
"""
from __future__ import annotations

import sys

from game import LEVEL, GameState, cell_key

CELL = 40
PAD = 16

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QColor, QPainter, QKeyEvent
    from PyQt5.QtWidgets import QApplication, QWidget
except ImportError:
    try:
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QColor, QPainter, QKeyEvent
        from PyQt6.QtWidgets import QApplication, QWidget
    except ImportError:
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QColor, QPainter, QKeyEvent
        from PySide6.QtWidgets import QApplication, QWidget


def _key_enum(name: str):
    """兼容 Qt5 Key_* / Qt6 Key 枚举。"""
    k = getattr(Qt, "Key", None)
    if k is not None and hasattr(k, name):
        return getattr(k, name)
    return getattr(Qt, name)


class Board(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.state = GameState.from_rows(LEVEL)
        self.setWindowTitle("Sokoban PyQt")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus if hasattr(Qt, "FocusPolicy") else Qt.StrongFocus)
        w = PAD * 2 + self.state.width * CELL
        h = PAD * 2 + self.state.height * CELL + 28
        self.setFixedSize(w, h)

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(26, 26, 46))
        s = self.state
        for y in range(s.height):
            for x in range(s.width):
                k = cell_key(x, y)
                rx, ry = PAD + x * CELL, PAD + y * CELL
                if k in s.walls:
                    p.fillRect(rx, ry, CELL, CELL, QColor(74, 74, 106))
                else:
                    p.fillRect(rx, ry, CELL, CELL, QColor(58, 58, 85))
                    p.setPen(QColor(68, 68, 102))
                    p.drawRect(rx, ry, CELL, CELL)
                    if k in s.goals:
                        p.setBrush(QColor(233, 69, 96))
                        p.setPen(Qt.PenStyle.NoPen if hasattr(Qt, "PenStyle") else Qt.NoPen)
                        p.drawEllipse(rx + CELL // 2 - 6, ry + CELL // 2 - 6, 12, 12)
                    if k in s.boxes:
                        on = k in s.goals
                        p.fillRect(rx + 4, ry + 4, CELL - 8, CELL - 8,
                                    QColor(46, 204, 113) if on else QColor(243, 156, 18))
                if s.player == (x, y):
                    p.setBrush(QColor(52, 152, 219))
                    p.setPen(Qt.PenStyle.NoPen if hasattr(Qt, "PenStyle") else Qt.NoPen)
                    r = int(CELL * 0.35)
                    p.drawEllipse(rx + CELL // 2 - r, ry + CELL // 2 - r, r * 2, r * 2)
        p.setPen(QColor(255, 255, 255))
        flag = " WIN" if s.won else ""
        p.drawText(8, PAD + s.height * CELL + 18, f"moves={s.moves}{flag}  WASD Z R Q")

    def keyPressEvent(self, e: QKeyEvent) -> None:
        key = e.key()
        mapping = {
            _key_enum("Key_W"): (0, -1),
            _key_enum("Key_Up"): (0, -1),
            _key_enum("Key_S"): (0, 1),
            _key_enum("Key_Down"): (0, 1),
            _key_enum("Key_A"): (-1, 0),
            _key_enum("Key_Left"): (-1, 0),
            _key_enum("Key_D"): (1, 0),
            _key_enum("Key_Right"): (1, 0),
        }
        if key in mapping:
            dx, dy = mapping[key]
            self.state.try_move(dx, dy)
        elif key == _key_enum("Key_Z"):
            self.state.undo()
        elif key == _key_enum("Key_R"):
            self.state = GameState.from_rows(LEVEL)
        elif key in (_key_enum("Key_Q"), _key_enum("Key_Escape")):
            self.close()
            return
        self.update()


def main() -> None:
    app = QApplication(sys.argv)
    w = Board()
    w.show()
    # Qt5 exec_ / Qt6 exec
    if hasattr(app, "exec"):
        sys.exit(app.exec())
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
