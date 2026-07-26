/**
 * Sokoban C++ Solver v4 - 256-bit support for large classic levels
 * Uses std::bitset<256> for box masks (supports up to 256 cells)
 * BFS search with time limit, corner deadlock, tunnel macro, 2x2 deadlock
 *
 * Compile: g++ -O3 -std=c++17 -march=native -o sokosolve4.exe solver4.cpp
 * Usage:   sokosolve4 <levelId> [timeMs]
 *  --write: write solution back to levels.json
 */
#include <algorithm>
#include <bitset>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <queue>
#include <string>
#include <unordered_set>
#include <vector>

using Clock = std::chrono::steady_clock;
using ms_t = std::chrono::milliseconds;
using BoxMask = std::bitset<256>;

// ---------------- JSON level load ----------------
struct LevelData {
    int id = -999;
    std::string name;
    std::vector<std::string> puzzle;
    std::string solution;
};

static std::string readFile(const std::string& path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) return {};
    return std::string((std::istreambuf_iterator<char>(f)),
                       std::istreambuf_iterator<char>());
}

static bool loadLevelById(const std::string& json, int wantId, LevelData& out) {
    size_t pos = 0;
    while (true) {
        size_t idKey = json.find("\"id\"", pos);
        if (idKey == std::string::npos) return false;
        size_t colon = json.find(':', idKey);
        size_t numStart = json.find_first_of("-0123456789", colon + 1);
        size_t numEnd = numStart;
        if (json[numEnd] == '-') numEnd++;
        while (numEnd < json.size() && json[numEnd] >= '0' && json[numEnd] <= '9') numEnd++;
        int id = std::stoi(json.substr(numStart, numEnd - numStart));
        size_t objStart = json.rfind('{', idKey);
        int depth = 0;
        size_t objEnd = objStart;
        for (; objEnd < json.size(); ++objEnd) {
            if (json[objEnd] == '{') depth++;
            else if (json[objEnd] == '}') { depth--; if (depth == 0) { objEnd++; break; } }
        }
        pos = objEnd;
        if (id != wantId) continue;
        std::string obj = json.substr(objStart, objEnd - objStart);
        out.id = id;
        size_t nk = obj.find("\"name\"");
        if (nk != std::string::npos) {
            size_t q1 = obj.find('"', obj.find(':', nk) + 1);
            size_t q2 = obj.find('"', q1 + 1);
            out.name = obj.substr(q1 + 1, q2 - q1 - 1);
        }
        out.solution.clear();
        size_t sk = obj.find("\"solution\"");
        if (sk != std::string::npos && sk < obj.size()) {
            size_t c2 = obj.find(':', sk);
            size_t q1 = obj.find_first_not_of(" \t\n\r", c2 + 1);
            if (q1 != std::string::npos && obj[q1] == '"') {
                size_t q2 = obj.find('"', q1 + 1);
                out.solution = obj.substr(q1 + 1, q2 - q1 - 1);
            }
        }
        size_t pk = obj.find("\"puzzle\"");
        size_t arr = obj.find('[', pk);
        size_t arrEnd = arr;
        int ad = 0;
        for (; arrEnd < obj.size(); ++arrEnd) {
            if (obj[arrEnd] == '[') ad++;
            else if (obj[arrEnd] == ']') { ad--; if (ad == 0) { arrEnd++; break; } }
        }
        std::string arrS = obj.substr(arr, arrEnd - arr);
        out.puzzle.clear();
        size_t p = 0;
        while (true) {
            size_t q1 = arrS.find('"', p);
            if (q1 == std::string::npos) break;
            size_t q2 = arrS.find('"', q1 + 1);
            out.puzzle.push_back(arrS.substr(q1 + 1, q2 - q1 - 1));
            p = q2 + 1;
        }
        return !out.puzzle.empty();
    }
}

static bool writeSolutionToJson(const std::string& path, int wantId, const std::string& solution) {
    std::string json = readFile(path);
    if (json.empty()) return false;
    size_t pos = 0;
    while (true) {
        size_t idKey = json.find("\"id\"", pos);
        if (idKey == std::string::npos) return false;
        size_t colon = json.find(':', idKey);
        size_t numStart = json.find_first_of("-0123456789", colon + 1);
        size_t numEnd = numStart;
        if (json[numEnd] == '-') numEnd++;
        while (numEnd < json.size() && json[numEnd] >= '0' && json[numEnd] <= '9') numEnd++;
        int id = std::stoi(json.substr(numStart, numEnd - numStart));
        size_t objStart = json.rfind('{', idKey);
        int depth = 0;
        size_t objEnd = objStart;
        for (; objEnd < json.size(); ++objEnd) {
            if (json[objEnd] == '{') depth++;
            else if (json[objEnd] == '}') { depth--; if (depth == 0) { objEnd++; break; } }
        }
        pos = objEnd;
        if (id != wantId) continue;
        size_t sk = json.find("\"solution\"", objStart);
        if (sk == std::string::npos || sk >= objEnd) {
            size_t ins = objEnd - 1;
            std::string add = ",\n    \"solution\": \"" + solution + "\"";
            json.insert(ins, add);
        } else {
            size_t c2 = json.find(':', sk);
            size_t q1 = json.find_first_not_of(" \t\n\r", c2 + 1);
            if (q1 < objEnd && json[q1] == 'n') {
                size_t nend = q1;
                while (nend < objEnd && json[nend] != ',' && json[nend] != '}') nend++;
                json.replace(q1, nend - q1, "\"" + solution + "\"");
            } else if (q1 < objEnd && json[q1] == '"') {
                size_t q2 = json.find('"', q1 + 1);
                json.replace(q1, q2 - q1 + 1, "\"" + solution + "\"");
            } else {
                return false;
            }
        }
        std::ofstream out(path, std::ios::binary);
        out << json;
        return true;
    }
}

// ---------------- State representation ----------------
struct State {
    BoxMask boxes;
    int player;
    int g;
    int h;
    bool operator==(const State& o) const {
        return boxes == o.boxes && player == o.player;
    }
};

struct StateHash {
    size_t operator()(const State& s) const {
        size_t h = 0;
        for (int i = 0; i < 4; i++) {
            auto w = s.boxes.to_ullong();
            h ^= (size_t)(w * 0x9e3779b97f4a7c15ull);
        }
        h ^= (size_t)(s.player * 0x9e3779b97f4a7c15ull);
        return h;
    }
};

// ---------------- Solver ----------------
struct Solver4 {
    int H = 0, WW = 0, N = 0, NB = 0;
    std::vector<int> cellX, cellY;
    std::vector<uint8_t> wall, isGoal, dead;
    std::vector<int16_t> xyToId, goalDist, neigh, pushTo, pushFrom;
    int startPlayer = 0;
    BoxMask startMask;
    BoxMask goalBitMask;

    static constexpr int DX[4] = {0, 0, -1, 1};
    static constexpr int DY[4] = {-1, 1, 0, 0};
    static constexpr char DCH[4] = {'u', 'd', 'l', 'r'};

    int flat(int x, int y) const { return y * WW + x; }

    bool build(const std::vector<std::string>& levelRows) {
        H = (int)levelRows.size();
        WW = 0;
        for (auto& r : levelRows) WW = std::max(WW, (int)r.size());
        std::vector<std::string> rows = levelRows;
        for (auto& r : rows)
            if ((int)r.size() < WW) r.append(WW - (int)r.size(), '#');

        wall.assign(WW * H, 0);
        xyToId.assign(WW * H, -1);
        cellX.clear(); cellY.clear();
        std::vector<int> startBoxes, goals;
        int sx = 0, sy = 0;
        for (int y = 0; y < H; y++) {
            for (int x = 0; x < WW; x++) {
                char c = rows[y][x];
                if (c == '#') { wall[flat(x, y)] = 1; continue; }
                int id = (int)cellX.size();
                cellX.push_back(x);
                cellY.push_back(y);
                xyToId[flat(x, y)] = (int16_t)id;
                if (c == '.' || c == '*' || c == '+') goals.push_back(id);
                if (c == '$' || c == '*') startBoxes.push_back(id);
                if (c == '@' || c == '+') { sx = x; sy = y; }
            }
        }
        N = (int)cellX.size();
        NB = (int)startBoxes.size();
        if (N > 250) {
            std::cerr << "N=" << N << " > 250\n";
            return false;
        }
        isGoal.assign(N, 0);
        goalBitMask.reset();
        for (int g : goals) { isGoal[g] = 1; goalBitMask.set(g); }
        startPlayer = xyToId[flat(sx, sy)];
        startMask.reset();
        for (int b : startBoxes) startMask.set(b);

        neigh.assign(N * 4, -1);
        pushTo.assign(N * 4, -1);
        pushFrom.assign(N * 4, -1);
        for (int i = 0; i < N; i++) {
            int x = cellX[i], y = cellY[i];
            for (int d = 0; d < 4; d++) {
                int nx = x + DX[d], ny = y + DY[d];
                if (nx < 0 || ny < 0 || nx >= WW || ny >= H || wall[flat(nx, ny)]) continue;
                int nid = xyToId[flat(nx, ny)];
                if (nid < 0) continue;
                neigh[i * 4 + d] = (int16_t)nid;
                int fx = x - DX[d], fy = y - DY[d];
                if (fx < 0 || fy < 0 || fx >= WW || fy >= H || wall[flat(fx, fy)]) continue;
                int fid = xyToId[flat(fx, fy)];
                if (fid < 0) continue;
                pushTo[i * 4 + d] = (int16_t)nid;
                pushFrom[i * 4 + d] = (int16_t)fid;
            }
        }

        goalDist.assign(N, 32000);
        dead.assign(N, 0);
        std::vector<int> q;
        q.reserve(N * 2);
        for (int g : goals) { goalDist[g] = 0; q.push_back(g); }
        for (size_t qi = 0; qi < q.size(); qi++) {
            int t = q[qi];
            int x = cellX[t], y = cellY[t], bd = goalDist[t];
            for (int d = 0; d < 4; d++) {
                int Fx = x - DX[d], Fy = y - DY[d];
                int Px = x - 2 * DX[d], Py = y - 2 * DY[d];
                if (Fx < 0 || Fy < 0 || Fx >= WW || Fy >= H || wall[flat(Fx, Fy)]) continue;
                if (Px < 0 || Py < 0 || Px >= WW || Py >= H || wall[flat(Px, Py)]) continue;
                int fid = xyToId[flat(Fx, Fy)];
                if (fid < 0) continue;
                if (goalDist[fid] > bd + 1) { goalDist[fid] = (int16_t)(bd + 1); q.push_back(fid); }
            }
        }
        for (int i = 0; i < N; i++) {
            if (isGoal[i]) continue;
            if (goalDist[i] >= 32000) { dead[i] = 1; continue; }
            int x = cellX[i], y = cellY[i];
            bool u = (y == 0 || wall[flat(x, y - 1)]);
            bool dn = (y == H - 1 || wall[flat(x, y + 1)]);
            bool l = (x == 0 || wall[flat(x - 1, y)]);
            bool r = (x == WW - 1 || wall[flat(x + 1, y)]);
            if ((u && l) || (u && r) || (dn && l) || (dn && r)) dead[i] = 1;
            else if (u && dn && (l || r)) dead[i] = 1;
            else if (l && r && (u || dn)) dead[i] = 1;
        }

        degree.assign(N, 0);
        for (int i = 0; i < N; i++) {
            int deg = 0;
            for (int d = 0; d < 4; d++) if (neigh[i * 4 + d] >= 0) deg++;
            degree[i] = (uint8_t)deg;
        }
        return true;
    }

    std::vector<uint8_t> degree;
    std::vector<uint32_t> visitGen;
    std::vector<int16_t> bfsQ;
    uint32_t gen = 1;

    int computeReach(int player, const BoxMask& mask) {
        ++gen;
        int qh = 0, qt = 0, minR = player;
        bfsQ[qt++] = (int16_t)player;
        visitGen[player] = gen;
        uint32_t g = gen;
        while (qh < qt) {
            int c = bfsQ[qh++];
            if (c < minR) minR = c;
            int base = c << 2;
            for (int d = 0; d < 4; d++) {
                int n = neigh[base + d];
                if (n < 0 || visitGen[n] == g) continue;
                if (mask.test(n)) continue;
                visitGen[n] = g;
                bfsQ[qt++] = (int16_t)n;
            }
        }
        return minR;
    }

    bool canReach(int c) const { return visitGen[c] == gen; }

    int heuristic(const BoxMask& mask) const {
        int h = 0;
        for (int i = 0; i < N; i++) {
            if (!mask.test(i)) continue;
            int d = goalDist[i];
            if (d >= 32000) return 999999;
            h += d;
        }
        return h;
    }

    bool isWin(const BoxMask& mask) const {
        BoxMask onGoal = mask & goalBitMask;
        return onGoal == mask;
    }

    bool is2x2(const BoxMask& mask, int movedTo) const {
        int x = cellX[movedTo], y = cellY[movedTo];
        for (int ox = -1; ox <= 0; ox++) {
            for (int oy = -1; oy <= 0; oy++) {
                bool all = true, anyG = false;
                for (int dx = 0; dx <= 1 && all; dx++) {
                    for (int dy = 0; dy <= 1; dy++) {
                        int cx = x + ox + dx, cy = y + oy + dy;
                        if (cx < 0 || cy < 0 || cx >= WW || cy >= H || wall[flat(cx, cy)]) { all = false; break; }
                        int id = xyToId[flat(cx, cy)];
                        if (id < 0 || !mask.test(id)) { all = false; break; }
                        if (isGoal[id]) anyG = true;
                    }
                }
                if (all && !anyG) return true;
            }
        }
        return false;
    }

    struct PushSeg { int boxFrom, dir, count; };

    std::string reconstruct(const std::vector<State>& states, int ci,
                            const std::vector<int>& parent,
                            const std::vector<PushSeg>& segs) const {
        std::string path;
        int p = ci;
        std::vector<PushSeg> s;
        while (p > 0) { s.push_back(segs[p]); p = parent[p]; }
        std::reverse(s.begin(), s.end());
        for (auto& seg : s)
            for (int i = 0; i < seg.count; i++)
                path.push_back(DCH[seg.dir]);
        return path;
    }

    std::string segsToPlayerPath(const std::vector<PushSeg>& segs) {
        BoxMask mask = startMask;
        int px = startPlayer;
        std::string full;
        for (auto& s : segs) {
            int b = s.boxFrom;
            int d = s.dir;
            int stand = pushFrom[b * 4 + d];
            if (stand < 0) return {};
            std::vector<int16_t> par(N, -2);
            std::vector<uint8_t> pm(N, 0);
            std::vector<int16_t> q(N);
            int qh = 0, qt = 0;
            q[qt++] = (int16_t)px;
            par[px] = -1;
            bool found = false;
            while (qh < qt) {
                int c = q[qh++];
                if (c == stand) { found = true; break; }
                int base = c << 2;
                for (int dd = 0; dd < 4; dd++) {
                    int n = neigh[base + dd];
                    if (n < 0 || par[n] != -2) continue;
                    if (mask.test(n)) continue;
                    par[n] = (int16_t)c;
                    pm[n] = (uint8_t)dd;
                    q[qt++] = (int16_t)n;
                }
            }
            if (!found) return {};
            std::string w;
            int c = stand;
            while (par[c] >= 0) { w.push_back(DCH[pm[c]]); c = par[c]; }
            std::reverse(w.begin(), w.end());
            full += w;
            int curBox = b;
            for (int i = 0; i < s.count; i++) {
                int to = pushTo[curBox * 4 + d];
                if (to < 0) return {};
                full.push_back((char)std::toupper((unsigned char)DCH[d]));
                mask.flip(curBox).flip(to);
                px = curBox;
                curBox = to;
            }
        }
        if (!isWin(mask)) return {};
        return full;
    }

    void ensureBuf() {
        if ((int)visitGen.size() != N) {
            visitGen.assign(N, 0);
            bfsQ.assign(N, 0);
            gen = 1;
        }
    }

    struct Result {
        bool ok = false;
        int ms = 0, nodes = 0, expansions = 0, pushes = 0, visited = 0;
        std::string path, playerPath;
    };

    Result solveBFS(int timeLimitMs = 0) {
        Result res;
        auto T0 = Clock::now();
        ensureBuf();

        int h0 = heuristic(startMask);
        if (h0 >= 999999) return res;

        std::unordered_set<State, StateHash> visited;
        visited.reserve(1 << 24);
        std::queue<int> q;
        std::vector<State> states;
        std::vector<int> parent;
        std::vector<PushSeg> segs;

        states.push_back({startMask, startPlayer, 0, h0});
        parent.push_back(-1);
        segs.push_back({-1, 0, 0});
        visited.insert(states[0]);
        q.push(0);

        int expansions = 0;

        while (!q.empty()) {
            if ((expansions & 65535) == 0 && timeLimitMs > 0) {
                auto elapsed = std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
                if (elapsed > timeLimitMs) {
                    res.ms = (int)elapsed;
                    res.nodes = (int)states.size();
                    res.expansions = expansions;
                    res.visited = (int)visited.size();
                    return res;
                }
            }
            int ci = q.front(); q.pop();
            expansions++;
            State cur = states[ci];

            if (isWin(cur.boxes)) {
                res.ok = true;
                res.path = reconstruct(states, ci, parent, segs);
                std::vector<PushSeg> psegs(segs.begin() + 1, segs.begin() + ci + 1);
                res.playerPath = segsToPlayerPath(psegs);
                if (res.playerPath.empty()) res.playerPath = res.path;
                res.pushes = cur.g;
                res.ms = (int)std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
                res.nodes = (int)states.size();
                res.expansions = expansions;
                res.visited = (int)visited.size();
                return res;
            }

            computeReach(cur.player, cur.boxes);
            BoxMask bm = cur.boxes;
            for (int b = 0; b < N; b++) {
                if (!bm.test(b)) continue;
                int base = b << 2;
                for (int d = 0; d < 4; d++) {
                    int to = pushTo[base + d];
                    if (to < 0) continue;
                    if (cur.boxes.test(to)) continue;
                    int from = pushFrom[base + d];
                    if (!canReach(from)) continue;
                    if (dead[to]) continue;

                    BoxMask nm = cur.boxes;
                    nm.flip(b).flip(to);
                    int fTo = to, fPl = b, pc = 1;
                    int nh = cur.h + (int)goalDist[to] - (int)goalDist[b];

                    while (degree[fTo] == 2 && !isGoal[fTo]) {
                        int nx = pushTo[(fTo << 2) + d];
                        if (nx < 0 || nm.test(nx) || dead[nx]) break;
                        nh += (int)goalDist[nx] - (int)goalDist[fTo];
                        nm.flip(fTo).flip(nx);
                        fPl = fTo;
                        fTo = nx;
                        pc++;
                        if (pc > 12) break;
                    }

                    if (nh < 0) nh = 0;
                    if (nh >= 999999) continue;
                    if (is2x2(nm, fTo)) continue;

                    State ns = {nm, fPl, cur.g + pc, nh};
                    if (visited.find(ns) != visited.end()) continue;
                    visited.insert(ns);

                    int ni = (int)states.size();
                    states.push_back(ns);
                    parent.push_back(ci);
                    segs.push_back({b, (uint8_t)d, (uint8_t)pc});
                    q.push(ni);
                }
            }
        }

        res.ms = (int)std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
        res.nodes = (int)states.size();
        res.expansions = expansions;
        res.visited = (int)visited.size();
        return res;
    }
};

// ---------------- Main ----------------
static std::string findLevelsJson() {
    for (const char* p : {"levels.json", "../levels.json", "../../levels.json"}) {
        auto s = readFile(p);
        if (!s.empty()) return p;
    }
    return {};
}

int main(int argc, char** argv) {
    int levelId = -99999;
    int timeLimit = 10000;
    bool doWrite = false;

    for (int i = 1; i < argc; i++) {
        std::string a = argv[i];
        if (a == "--write") doWrite = true;
        else if (a == "0" || (a.size() && (a[0] == '-' || (a[0] >= '0' && a[0] <= '9')))) {
            if (levelId == -99999) levelId = std::atoi(a.c_str());
            else timeLimit = std::atoi(a.c_str());
        }
    }

    if (levelId == -99999) {
        std::cerr << "Usage: sokosolve4 <id> [timeMs] [--write]\n";
        return 1;
    }

    std::string path = findLevelsJson();
    if (path.empty()) { std::cerr << "levels.json not found\n"; return 1; }

    std::string json = readFile(path);
    LevelData level;
    if (!loadLevelById(json, levelId, level)) {
        std::cerr << "Level id=" << levelId << " not found\n";
        return 1;
    }
    if (!level.solution.empty() && level.solution != "null" && !doWrite) {
        std::cout << "[skip] id=" << levelId << " " << level.name << " already has solution\n";
        return 0;
    }

    std::cout << "\n========== id=" << level.id << " " << level.name << " ==========\n";
    for (auto& r : level.puzzle) std::cout << "  " << r << "\n";

    Solver4 solver;
    if (!solver.build(level.puzzle)) {
        std::cerr << "BUILD FAIL\n";
        return 1;
    }
    std::cout << "N=" << solver.N << " boxes=" << solver.NB << " limit=" << timeLimit << "ms\n";
    std::cout.flush();

    auto res = solver.solveBFS(timeLimit);
    if (!res.ok) {
        std::cout << "FAILED ms=" << res.ms << " nodes=" << res.nodes
                  << " exp=" << res.expansions << " visited=" << res.visited << "\n";
        return 1;
    }

    std::string playerPath = res.playerPath;
    if (playerPath.empty()) playerPath = res.path;

    std::cout << "SOLVED ms=" << res.ms << " pushes=" << res.pushes
              << " nodes=" << res.nodes << " playerMoves=" << playerPath.size() << "\n";
    std::cout << "player: " << playerPath << "\n";

    if (doWrite) {
        writeSolutionToJson(path, levelId, playerPath);
        std::cout << "  Wrote " << path << "\n";
        for (const char* cp : {"c_app/levels.json", "sokoban_linux/levels.json"}) {
            std::string full = path.substr(0, path.rfind('/') + 1) + cp;
            auto s = readFile(full);
            if (!s.empty() && full != path) {
                if (writeSolutionToJson(full, levelId, playerPath))
                    std::cout << "  Wrote " << full << "\n";
            }
        }
    }
    return 0;
}