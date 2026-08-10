// cppapp1 — C++ 推箱子终端版（教学）
// 编译: g++ -std=c++17 -O2 main.cpp -o sokoban
#include "game.hpp"
#include <iostream>
#include <string>
#include <cctype>

int main() {
    const std::vector<std::string> LEVEL = {
        "#######",
        "#. . .#",
        "# $$$ #",
        "#.$@$.#",
        "# $$$ #",
        "#. . .#",
        "#######",
    };
    auto state = GameState::fromRows(LEVEL, 0);
    std::cout << "sokoban_cpp — wasd 移动, z 撤销, r 重置, q 退出\n";
    while (true) {
        std::cout << "\n" << state.renderAscii();
        std::cout << "moves=" << state.moves << (state.won ? " WIN!" : "") << "\n> ";
        std::string line;
        if (!std::getline(std::cin, line)) break;
        if (line.empty()) continue;
        char ch = static_cast<char>(std::tolower(static_cast<unsigned char>(line[0])));
        if (ch == 'w') state.tryMove(0, -1);
        else if (ch == 's') state.tryMove(0, 1);
        else if (ch == 'a') state.tryMove(-1, 0);
        else if (ch == 'd') state.tryMove(1, 0);
        else if (ch == 'z') state.undo();
        else if (ch == 'r') state = GameState::fromRows(LEVEL, 0);
        else if (ch == 'q') break;
        if (state.won) std::cout << "Level clear!\n";
    }
    return 0;
}
