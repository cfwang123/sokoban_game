/**
 * Arduino 推箱子教学（UNO/Nano + 可选 SSD1306）。
 * 串口：WASD 移动，Z 撤销，R 重置，N 下一关。
 * OLED：取消注释 USE_OLED 并接 I2C（需 Adafruit 库，本演示默认串口）。
 */
#include "game_core.h"

// #define USE_OLED

GameCore g;

void drawBoard() {
  Serial.println();
  Serial.print(F("LV"));
  Serial.print(g.level + 1);
  Serial.print(F(" M"));
  Serial.print(g.moves);
  if (g.won) Serial.print(F(" WIN"));
  Serial.println();
  for (int y = 0; y < g.h; y++) {
    for (int x = 0; x < g.w; x++) {
      int i = gc_idx(&g, x, y);
      char c = ' ';
      if (g.px == x && g.py == y) c = g.goals[i] ? '+' : '@';
      else if (g.boxes[i]) c = g.goals[i] ? '*' : '$';
      else if (g.walls[i]) c = '#';
      else if (g.goals[i]) c = '.';
      Serial.write(c);
    }
    Serial.println();
  }
}

void setup() {
  Serial.begin(115200);
  while (!Serial) { /* Leonardo */ }
  gc_load(&g, 0);
  Serial.println(F("sokoban arduino — WASD Z R N"));
  drawBoard();
}

void loop() {
  if (!Serial.available()) return;
  char c = Serial.read();
  int redraw = 1;
  switch (c) {
    case 'w': case 'W': gc_try_move(&g, 0, -1); break;
    case 's': case 'S': gc_try_move(&g, 0, 1); break;
    case 'a': case 'A': gc_try_move(&g, -1, 0); break;
    case 'd': case 'D': gc_try_move(&g, 1, 0); break;
    case 'z': case 'Z': gc_undo(&g); break;
    case 'r': case 'R': gc_load(&g, g.level); break;
    case 'n': case 'N': gc_load(&g, g.level + 1); break;
    default: redraw = 0; break;
  }
  if (redraw) drawBoard();
}
