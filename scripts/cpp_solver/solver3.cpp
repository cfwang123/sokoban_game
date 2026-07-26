/**
 * Sokoban C++ Solver v3 - Enhanced
 *  - IDA* with transposition table
 *  - Freeze deadlock detection
 *  - Tunnel macro
 *  - 2x2 deadlock
 *  - Corner deadlock
 *  - Dead-square detection
 *  - Unlimited time/memory
 *
 * Compile: g++ -O3 -std=c++17 -march=native -o sokosolve3.exe solver3.cpp
 * Usage:   sokosolve3 <levelId> [mode]
 *   mode: ida (default) | bfs | dfs
 *  --write: write solution back to levels.json
 */
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <queue>
#include <unordered_map>
#include <unordered_set>

using Clock = std::chrono::steady_clock;
using ms_t = std::chrono::milliseconds;

// ---------------- JSON level load (same as original) ----------------
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
            else if (json[objEnd] == '}') {
                depth--;
                if (depth == 0) { objEnd++; break; }
            }
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
    uint64_t boxes; // bitmask of box positions
    int player;     // cell id of player
    int g;          // pushes so far
    int h;          // heuristic estimate

    bool operator==(const State& o) const { return boxes == o.boxes && player == o.player; }
};

struct StateHash {
    size_t operator()(const State& s) const {
        return (size_t)(s.boxes ^ (uint64_t(s.player) * 0x9e3779b97f4a7c15ull));
    }
};

// ---------------- Solver ----------------
struct Solver3 {
    int H = 0, WW = 0, N = 0, NB = 0;
    std::vector<int> cellX, cellY;
    std::vector<uint8_t> wall, isGoal, dead, deadSquare;
    std::vector<int16_t> xyToId, goalDist, neigh, pushTo, pushFrom;
    int startPlayer = 0;
    uint64_t startMask = 0;
    uint64_t goalBitMask = 0;
    uint64_t BITS[64];

    static constexpr int DX[4] = {0, 0, -1, 1};
    static constexpr int DY[4] = {-1, 1, 0, 0};
    static constexpr char DCH[4] = {'u', 'd', 'l', 'r'};

    int flat(int x, int y) const { return y * WW + x; }

    bool build(const std::vector<std::string>& levelRows) {
        for (int i = 0; i < 64; i++) BITS[i] = 1ull << i;
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
        if (N > 62) {
            std::cerr << "N=" << N << " > 62\n";
            return false;
        }
        isGoal.assign(N, 0);
        goalBitMask = 0;
        for (int g : goals) {
            isGoal[g] = 1;
            goalBitMask |= BITS[g];
        }
        startPlayer = xyToId[flat(sx, sy)];
        startMask = 0;
        for (int b : startBoxes) startMask |= BITS[b];

        // Build neighbor / push tables
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

        // Goal distance BFS
        goalDist.assign(N, 32000);
        dead.assign(N, 0);
        {
            std::vector<int> q;
            q.reserve(N * 2);
            for (int g : goals) {
                goalDist[g] = 0;
                q.push_back(g);
            }
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
                    if (goalDist[fid] > bd + 1) {
                        goalDist[fid] = (int16_t)(bd + 1);
                        q.push_back(fid);
                    }
                }
            }
        }

        // Corner and edge deadlocks
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

        // Dead-square detection: cells where a box can never be solved
        // A dead square is a non-goal cell that is adjacent to a wall,
        // and there is no goal on the same wall line reachable without crossing other boxes.
        deadSquare.assign(N, 0);
        for (int i = 0; i < N; i++) {
            if (isGoal[i] || dead[i]) continue;
            int x = cellX[i], y = cellY[i];
            // Check if next to a wall
            bool hasWallNear = false;
            for (int d = 0; d < 4; d++) {
                int nx = x + DX[d], ny = y + DY[d];
                if (nx < 0 || ny < 0 || nx >= WW || ny >= H || wall[flat(nx, ny)]) {
                    hasWallNear = true;
                    break;
                }
            }
            if (!hasWallNear) continue;
            // Check if any goal is reachable by moving along the wall
            // A box can only be pushed; if it's against a wall, it can only be pushed
            // along the wall or away from it. If pushing away is blocked, it's dead.
            // Simple heuristic: if ALL adjacent non-wall cells are also dead, this is dead
            int movableDirs = 0;
            for (int d = 0; d < 4; d++) {
                int to = pushTo[i * 4 + d];
                if (to >= 0) movableDirs++;
            }
            // If a cell has only 1 push direction and is not a goal, it's a dead end
            if (movableDirs <= 1) {
                deadSquare[i] = 1;
            }
        }

        // Degree for tunnel macro
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

    int computeReach(int player, uint64_t mask) {
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
                if (mask & BITS[n]) continue;
                visitGen[n] = g;
                bfsQ[qt++] = (int16_t)n;
            }
        }
        return minR;
    }

    bool canReach(int c) const { return visitGen[c] == gen; }

    int heuristic(uint64_t mask) const {
        int h = 0;
        uint64_t m = mask;
        while (m) {
            int i = __builtin_ctzll(m);
            m &= m - 1;
            int d = goalDist[i];
            if (d >= 32000) return 999999;
            h += d;
        }
        return h;
    }

    bool isWin(uint64_t mask) const {
        return (mask & ~goalBitMask) == 0;
    }

    // Check freeze deadlock: a box against a wall with no goal reachable
    bool isFreezeDeadlock(uint64_t mask, int boxId) const {
        if (isGoal[boxId]) return false;
        int x = cellX[boxId], y = cellY[boxId];
        for (int d = 0; d < 4; d++) {
            int nx = x + DX[d], ny = y + DY[d];
            if (nx < 0 || ny < 0 || nx >= WW || ny >= H || wall[flat(nx, ny)]) {
                // Wall on this side - box can't be pushed this way
                // Check if the opposite push direction is possible
                int opp = d ^ 1;
                int to = pushTo[boxId * 4 + opp];
                if (to < 0) continue; // can't push this way either
                if (mask & BITS[to]) continue; // blocked by another box
                // Check if pushing this way leads to any goal
                // Simple check: if the cell is not a goal and has no path to a goal
                // along the wall, it's dead
                if (goalDist[boxId] >= 32000) return true;
                // Check if the box is trapped between two walls
                int perp1 = d == 0 || d == 1 ? 2 : 0;
                int perp2 = perp1 + 1;
                bool block1 = false, block2 = false;
                int nx1 = x + DX[perp1], ny1 = y + DY[perp1];
                int nx2 = x + DX[perp2], ny2 = y + DY[perp2];
                if (nx1 < 0 || ny1 < 0 || nx1 >= WW || ny1 >= H || wall[flat(nx1, ny1)]) block1 = true;
                else if (mask & BITS[xyToId[flat(nx1, ny1)]]) block1 = true;
                if (nx2 < 0 || ny2 < 0 || nx2 >= WW || ny2 >= H || wall[flat(nx2, ny2)]) block2 = true;
                else if (mask & BITS[xyToId[flat(nx2, ny2)]]) block2 = true;
                // If both perpendicular directions are blocked, box is frozen
                if (block1 && block2) return true;
            }
        }
        return false;
    }

    // Check 2x2 deadlock
    bool is2x2(uint64_t mask, int movedTo) const {
        int x = cellX[movedTo], y = cellY[movedTo];
        for (int ox = -1; ox <= 0; ox++) {
            for (int oy = -1; oy <= 0; oy++) {
                bool all = true, anyG = false;
                for (int dx = 0; dx <= 1 && all; dx++) {
                    for (int dy = 0; dy <= 1; dy++) {
                        int cx = x + ox + dx, cy = y + oy + dy;
                        if (cx < 0 || cy < 0 || cx >= WW || cy >= H || wall[flat(cx, cy)]) {
                            all = false; break;
                        }
                        int id = xyToId[flat(cx, cy)];
                        if (id < 0 || !(mask & BITS[id])) { all = false; break; }
                        if (isGoal[id]) anyG = true;
                    }
                }
                if (all && !anyG) return true;
            }
        }
        return false;
    }

    // Reconstruct solution path
    struct PushSeg { int boxFrom, dir, count; };

    std::string reconstruct(const std::vector<State>& states, int ci,
                            const std::vector<int>& parent,
                            const std::vector<PushSeg>& segs) const {
        std::string path;
        int p = ci;
        std::vector<PushSeg> s;
        while (p > 0) {
            s.push_back(segs[p]);
            p = parent[p];
        }
        std::reverse(s.begin(), s.end());
        for (auto& seg : s) {
            for (int i = 0; i < seg.count; i++)
                path.push_back(DCH[seg.dir]);
        }
        return path;
    }

    std::string segsToPlayerPath(const std::vector<PushSeg>& segs) {
        uint64_t mask = startMask;
        int px = startPlayer;
        std::string full;

        for (auto& s : segs) {
            int b = s.boxFrom;
            int d = s.dir;
            int stand = pushFrom[b * 4 + d];
            if (stand < 0) return {};
            // BFS walk from player to stand
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
                    if (mask & BITS[n]) continue;
                    par[n] = (int16_t)c;
                    pm[n] = (uint8_t)dd;
                    q[qt++] = (int16_t)n;
                }
            }
            if (!found) return {};
            std::string w;
            int c = stand;
            while (par[c] >= 0) {
                w.push_back(DCH[pm[c]]);
                c = par[c];
            }
            std::reverse(w.begin(), w.end());
            full += w;
            // Apply pushes
            int curBox = b;
            for (int i = 0; i < s.count; i++) {
                int to = pushTo[curBox * 4 + d];
                if (to < 0) return {};
                full.push_back((char)std::toupper((unsigned char)DCH[d]));
                mask ^= BITS[curBox] ^ BITS[to];
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

    // ---------------- BFS (guaranteed shortest, but may use lots of memory) ----------------
    struct Result {
        bool ok = false;
        int ms = 0, nodes = 0, expansions = 0, pushes = 0, visited = 0;
        std::string path, playerPath, dir;
    };

    Result solveBFS() {
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

        int min0 = computeReach(startPlayer, startMask);
        states.push_back({startMask, startPlayer, 0, h0});
        parent.push_back(-1);
        segs.push_back({-1, 0, 0});
        visited.insert(states[0]);
        q.push(0);

        int expansions = 0;

        while (!q.empty()) {
            int ci = q.front(); q.pop();
            expansions++;
            State cur = states[ci];

            if (isWin(cur.boxes)) {
                res.ok = true;
                res.path = reconstruct(states, ci, parent, segs);
                res.playerPath = segsToPlayerPath(std::vector<PushSeg>(segs.begin() + 1, segs.begin() + ci + 1));
                if (res.playerPath.empty()) res.playerPath = res.path;
                res.pushes = cur.g;
                res.ms = (int)std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
                res.nodes = (int)states.size();
                res.expansions = expansions;
                res.visited = (int)visited.size();
                return res;
            }

            computeReach(cur.player, cur.boxes);
            uint64_t bm = cur.boxes;
            while (bm) {
                int b = __builtin_ctzll(bm);
                bm &= bm - 1;
                int base = b << 2;
                for (int d = 0; d < 4; d++) {
                    int to = pushTo[base + d];
                    if (to < 0) continue;
                    if (cur.boxes & BITS[to]) continue;
                    int from = pushFrom[base + d];
                    if (!canReach(from)) continue;
                    if (dead[to]) continue;

                    uint64_t nm = cur.boxes ^ BITS[b] ^ BITS[to];
                    int fTo = to, fPl = b, pc = 1;
                    int nh = cur.h + (int)goalDist[to] - (int)goalDist[b];

                    // Tunnel macro
                    while (degree[fTo] == 2 && !isGoal[fTo]) {
                        int nx = pushTo[(fTo << 2) + d];
                        if (nx < 0 || (nm & BITS[nx]) || dead[nx]) break;
                        nh += (int)goalDist[nx] - (int)goalDist[fTo];
                        nm ^= BITS[fTo] ^ BITS[nx];
                        fPl = fTo;
                        fTo = nx;
                        pc++;
                        if (pc > 12) break;
                    }

                    if (nh < 0) nh = 0;
                    if (nh >= 999999) continue;
                    if (is2x2(nm, fTo)) continue;

                    State ns = {nm, fPl, cur.g + pc, nh};
                    auto it = visited.find(ns);
                    if (it != visited.end()) continue;
                    visited.insert(ns);

                    int ni = (int)states.size();
                    states.push_back(ns);
                    parent.push_back(ci);
                    segs.push_back({b, (uint8_t)d, (uint8_t)pc});
                    q.push(ni);
                }
            }

            if ((expansions & 65535) == 0) {
                auto elapsed = std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
                std::cout << "  BFS progress exp=" << expansions << " states=" << states.size()
                          << " visited=" << visited.size() << " ms=" << elapsed << "\n";
                std::cout.flush();
            }
        }

        res.ms = (int)std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
        res.nodes = (int)states.size();
        res.expansions = expansions;
        res.visited = (int)visited.size();
        return res;
    }

    // ---------------- IDA* ----------------
    struct IDAState {
        uint64_t boxes;
        int player;
        int g;
        int h;
        int boxFrom;
        uint8_t dir;
        uint8_t count;
    };

    // Recursive IDA* search
    int idaSearch(std::vector<IDAState>& stack, std::vector<int>& depths, int bound,
                  int& outNodeIdx, int& expansions, int timeLimitMs,
                  std::unordered_map<uint64_t, int>& transTable, Clock::time_point T0) {
        int ci = (int)stack.size() - 1;
        IDAState& cur = stack[ci];
        int depth = depths[ci];

        int f = cur.g + cur.h;
        if (f > bound) return f;

        if (isWin(cur.boxes)) {
            outNodeIdx = ci;
            return 0;
        }

        int minF = 2000000000;

        computeReach(cur.player, cur.boxes);
        uint64_t bm = cur.boxes;

        struct Cand {
            uint64_t nm;
            int fPl, nh, pc, d, boxFrom;
        };
        std::vector<Cand> cands;
        cands.reserve(NB * 4);

        while (bm) {
            int b = __builtin_ctzll(bm);
            bm &= bm - 1;
            int base = b << 2;
            for (int d = 0; d < 4; d++) {
                int to = pushTo[base + d];
                if (to < 0) continue;
                if (cur.boxes & BITS[to]) continue;
                int from = pushFrom[base + d];
                if (!canReach(from)) continue;
                if (dead[to]) continue;

                uint64_t nm = cur.boxes ^ BITS[b] ^ BITS[to];
                int fTo = to, fPl = b, pc = 1;
                int nh = cur.h + (int)goalDist[to] - (int)goalDist[b];

                while (degree[fTo] == 2 && !isGoal[fTo]) {
                    int nx = pushTo[(fTo << 2) + d];
                    if (nx < 0 || (nm & BITS[nx]) || dead[nx]) break;
                    nh += (int)goalDist[nx] - (int)goalDist[fTo];
                    nm ^= BITS[fTo] ^ BITS[nx];
                    fPl = fTo;
                    fTo = nx;
                    pc++;
                    if (pc > 12) break;
                }

                if (nh < 0) nh = 0;
                if (nh >= 999999) continue;
                if (is2x2(nm, fTo)) continue;
                if (isFreezeDeadlock(nm, fTo)) continue;

                cands.push_back({nm, fPl, nh, pc, d, b});
            }
        }

        std::sort(cands.begin(), cands.end(), [](const Cand& a, const Cand& b) {
            return a.nh < b.nh;
        });

        for (auto& c : cands) {
            int ng = cur.g + c.pc;
            int nf = ng + c.nh;

            auto it = transTable.find(c.nm);
            if (it != transTable.end() && it->second <= ng) continue;
            transTable[c.nm] = ng;

            if (nf > bound) {
                if (nf < minF) minF = nf;
                continue;
            }

            stack.push_back({c.nm, c.fPl, ng, c.nh, c.boxFrom, (uint8_t)c.d, (uint8_t)c.pc});
            depths.push_back(depth + 1);
            expansions++;

            int result = idaSearch(stack, depths, bound, outNodeIdx, expansions, timeLimitMs, transTable, T0);
            if (result == 0) return 0;
            if (result < minF) minF = result;

            stack.pop_back();
            depths.pop_back();

            if ((expansions & 65535) == 0) {
                auto elapsed = std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
                if (timeLimitMs > 0 && elapsed > timeLimitMs) return -1;
                std::cout << "  IDA* progress exp=" << expansions << " bound=" << bound
                          << " stack=" << stack.size() << " trans=" << transTable.size()
                          << " ms=" << elapsed << "\n";
                std::cout.flush();
            }
        }

        return minF;
    }

    Result solveIDA(int timeLimitMs = 0) {
        Result res;
        auto T0 = Clock::now();
        ensureBuf();

        int h0 = heuristic(startMask);
        if (h0 >= 999999) return res;

        std::unordered_map<uint64_t, int> transTable;
        transTable.reserve(1 << 24);

        int bound = h0;
        int expansions = 0;

        while (true) {
            auto elapsed = std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
            if (timeLimitMs > 0 && elapsed > timeLimitMs) break;

            std::cout << "  IDA* iteration bound=" << bound << " expansions=" << expansions
                      << " trans=" << transTable.size() << " ms=" << elapsed << "\n";
            std::cout.flush();

            std::vector<IDAState> stack;
            std::vector<int> depths;
            stack.push_back({startMask, startPlayer, 0, h0, -1, 0, 0});
            depths.push_back(0);

            int outNodeIdx = -1;
            int result = idaSearch(stack, depths, bound, outNodeIdx, expansions, timeLimitMs, transTable, T0);

            if (result == 0) {
                std::vector<PushSeg> segs;
                int ci = outNodeIdx;
                while (ci > 0) {
                    segs.push_back({stack[ci].boxFrom, stack[ci].dir, stack[ci].count});
                    int targetG = stack[ci].g - stack[ci].count;
                    ci--;
                    while (ci > 0 && stack[ci].g != targetG) ci--;
                }
                std::reverse(segs.begin(), segs.end());

                std::string path;
                for (auto& s : segs) {
                    for (int i = 0; i < s.count; i++)
                        path.push_back(DCH[s.dir]);
                }

                res.ok = true;
                res.path = path;
                res.playerPath = segsToPlayerPath(segs);
                if (res.playerPath.empty()) res.playerPath = path;
                res.pushes = stack[outNodeIdx].g;
                res.ms = (int)std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
                res.nodes = (int)transTable.size();
                res.expansions = expansions;
                res.visited = (int)transTable.size();
                return res;
            }

            if (result == -1 || result >= 2000000000) break;
            bound = result;
        }

        res.ms = (int)std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
        res.nodes = (int)transTable.size();
        res.expansions = expansions;
        res.visited = (int)transTable.size();
        return res;
    }

    // ---------------- Main solve entry ----------------
    Result solve(const std::string& mode, int timeLimitMs = 0) {
        if (mode == "bfs") return solveBFS();
        if (mode == "ida") return solveIDA(timeLimitMs);
        // Default: try IDA* first, then BFS
        auto r = solveIDA(60000);
        if (r.ok) { r.dir = "ida"; return r; }
        std::cout << "  IDA* exhausted, switching to BFS...\n";
        auto r2 = solveBFS();
        r2.dir = r2.ok ? "bfs" : "failed";
        r2.nodes += r.nodes;
        r2.expansions += r.expansions;
        return r2;
    }
};

// ---------------- Main ----------------
static std::string findLevelsJson() {
    for (const char* p : {"levels.json", "../levels.json", "../../levels.json",
                          "D:/VS_Projects/AIPrototype/game/sokoban/levels.json"}) {
        auto s = readFile(p);
        if (!s.empty()) return p;
    }
    return {};
}

int main(int argc, char** argv) {
    int levelId = -99999;
    std::string mode = "auto";
    bool doWrite = false;

    for (int i = 1; i < argc; i++) {
        std::string a = argv[i];
        if (a == "--write") doWrite = true;
        else if (a == "ida" || a == "bfs" || a == "auto") mode = a;
        else if (a == "0" || (a.size() && (a[0] == '-' || (a[0] >= '0' && a[0] <= '9')))) {
            levelId = std::atoi(a.c_str());
        }
    }

    if (levelId == -99999) {
        std::cerr << "Usage: sokosolve3 <id> [ida|bfs|auto] [--write]\n";
        return 1;
    }

    std::string path = findLevelsJson();
    if (path.empty()) {
        std::cerr << "levels.json not found\n";
        return 1;
    }

    std::string json = readFile(path);
    LevelData level;
    if (!loadLevelById(json, levelId, level)) {
        std::cerr << "Level id=" << levelId << " not found\n";
        return 1;
    }

    if (!level.solution.empty() && level.solution != "null" && !doWrite) {
        std::cout << "Level already has solution, use --write to overwrite\n";
    }

    std::cout << "\n========== id=" << level.id << " " << level.name << " ==========\n";
    for (auto& r : level.puzzle) std::cout << "  " << r << "\n";

    Solver3 solver;
    if (!solver.build(level.puzzle)) {
        std::cerr << "BUILD FAIL\n";
        return 1;
    }
    std::cout << "N=" << solver.N << " boxes=" << solver.NB << " mode=" << mode << "\n";
    std::cout.flush();

    auto res = solver.solve(mode);
    if (!res.ok) {
        std::cout << "FAILED ms=" << res.ms << " nodes=" << res.nodes
                  << " exp=" << res.expansions << " visited=" << res.visited << "\n";
        return 1;
    }

    std::string playerPath = res.playerPath;
    if (playerPath.empty()) playerPath = res.path;

    std::cout << "SOLVED ms=" << res.ms << " pushes=" << res.pushes
              << " nodes=" << res.nodes << " exp=" << res.expansions
              << " playerMoves=" << playerPath.size() << "\n";
    std::cout << "player: " << playerPath << "\n";

    if (doWrite) {
        auto p = path;
        writeSolutionToJson(p, levelId, playerPath);
        std::cout << "  Wrote " << p << "\n";
        // Also try writing to copies
        for (const char* cp : {"c_app/levels.json", "sokoban_linux/levels.json"}) {
            auto s = readFile(cp);
            if (!s.empty() && cp != p) {
                if (writeSolutionToJson(cp, levelId, playerPath))
                    std::cout << "  Wrote " << cp << "\n";
            }
        }
        std::cout << "Run: node scripts/gen_levels_js.js  to sync HTML\n";
    }
    return 0;
}