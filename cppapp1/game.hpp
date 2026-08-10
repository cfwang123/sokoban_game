// 推箱子核心逻辑（C++ 教学）
#pragma once
#include <string>
#include <unordered_set>
#include <vector>
#include <utility>

struct Hist {
    int px, py;
    std::string boxFrom, boxTo; // empty boxFrom => walk only
    bool isPush = false;
};

struct GameState {
    std::unordered_set<std::string> walls, goals, boxes;
    int px = 0, py = 0;
    int moves = 0;
    bool won = false;
    int width = 0, height = 0;
    std::vector<Hist> hist;

    static std::string key(int x, int y) {
        return std::to_string(x) + "," + std::to_string(y);
    }

    static GameState fromRows(const std::vector<std::string>& rows, int index = 0) {
        GameState s;
        int maxX = 0, maxY = 0;
        for (int y = 0; y < (int)rows.size(); ++y) {
            maxY = y;
            const auto& row = rows[y];
            for (int x = 0; x < (int)row.size(); ++x) {
                if (x > maxX) maxX = x;
                char ch = row[x];
                auto k = key(x, y);
                switch (ch) {
                case '#': s.walls.insert(k); break;
                case '.': s.goals.insert(k); break;
                case '$': s.boxes.insert(k); break;
                case '*': s.boxes.insert(k); s.goals.insert(k); break;
                case '@': s.px = x; s.py = y; break;
                case '+': s.px = x; s.py = y; s.goals.insert(k); break;
                default: break;
                }
            }
        }
        s.width = maxX + 1;
        s.height = maxY + 1;
        (void)index;
        return s;
    }

    void checkWin() {
        for (const auto& b : boxes) {
            if (!goals.count(b)) { won = false; return; }
        }
        won = true;
    }

    bool tryMove(int dx, int dy) {
        if (won) return false;
        int nx = px + dx, ny = py + dy;
        auto nk = key(nx, ny);
        if (walls.count(nk)) return false;
        if (boxes.count(nk)) {
            int bx = nx + dx, by = ny + dy;
            auto bk = key(bx, by);
            if (walls.count(bk) || boxes.count(bk)) return false;
            hist.push_back(Hist{px, py, nk, bk, true});
            boxes.erase(nk);
            boxes.insert(bk);
            px = nx; py = ny;
            ++moves;
            checkWin();
            return true;
        }
        hist.push_back(Hist{px, py, "", "", false});
        px = nx; py = ny;
        return true;
    }

    bool undo() {
        if (won || hist.empty()) return false;
        while (!hist.empty()) {
            Hist e = hist.back();
            hist.pop_back();
            if (e.isPush) {
                px = e.px; py = e.py;
                boxes.erase(e.boxTo);
                boxes.insert(e.boxFrom);
                if (moves > 0) --moves;
                won = false;
                return true;
            }
            px = e.px; py = e.py;
        }
        return true;
    }

    std::string renderAscii() const {
        std::string out;
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                auto k = key(x, y);
                if (px == x && py == y) out += goals.count(k) ? '+' : '@';
                else if (boxes.count(k)) out += goals.count(k) ? '*' : '$';
                else if (walls.count(k)) out += '#';
                else if (goals.count(k)) out += '.';
                else out += ' ';
            }
            out += '\n';
        }
        return out;
    }
};
