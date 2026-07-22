/**
 * Sokoban C++ 高速求解器 v2
 *
 * 优化：
 *  - uint64 箱掩码 + ctz 枚举箱子
 *  - 无 string 热路径（隧道用 dir+count）
 *  - 开放寻址哈希表（visited）
 *  - 四叉堆
 *  - 增量启发
 *  - Greedy-BF + Greedy-DFS
 *  - 2x2 / 反向死格 / 隧道宏
 *
 * 编译: g++ -O3 -std=c++17 -march=native -o sokosolve.exe solver.cpp
 * 用法: sokosolve <levelId> [timeMs] [mode]
 *   mode: bf | dfs | auto | wastar
 * 写出答案: sokosolve <id> <ms> <mode> --write
 */
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

using Clock = std::chrono::steady_clock;
using ms_t = std::chrono::milliseconds;

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
        size_t sk = obj.find("\"solution\"");
        if (sk != std::string::npos) {
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
            else if (obj[arrEnd] == ']') {
                ad--;
                if (ad == 0) { arrEnd++; break; }
            }
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

// 把 solution 写回 levels.json（简单替换：找到 id 块后改 solution 字段）
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
            else if (json[objEnd] == '}') {
                depth--;
                if (depth == 0) { objEnd++; break; }
            }
        }
        pos = objEnd;
        if (id != wantId) continue;

        // within [objStart, objEnd)
        size_t sk = json.find("\"solution\"", objStart);
        if (sk == std::string::npos || sk >= objEnd) {
            // insert before closing brace
            size_t ins = objEnd - 1;
            std::string add = ",\n    \"solution\": \"" + solution + "\"";
            json.insert(ins, add);
        } else {
            size_t c2 = json.find(':', sk);
            size_t q1 = json.find_first_not_of(" \t\n\r", c2 + 1);
            if (q1 < objEnd && json[q1] == 'n') {
                // null
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

// ---------------- Open-addressing map: VisKey -> g ----------------
struct VisKey {
    uint64_t mask;
    uint16_t minR;
};

struct VisEntry {
    uint64_t mask;
    uint16_t minR;
    int g;
    uint8_t used; // 0 empty, 1 used
};

struct VisMap {
    std::vector<VisEntry> tab;
    size_t maskBits = 0;
    size_t count = 0;

    void clear(size_t capPow2 = 1 << 20) {
        tab.assign(capPow2, VisEntry{0, 0, 0, 0});
        maskBits = capPow2 - 1;
        count = 0;
    }

    static size_t hash(uint64_t m, uint16_t r) {
        uint64_t x = m ^ (uint64_t(r) * 0x9e3779b97f4a7c15ull);
        x ^= x >> 30;
        x *= 0xbf58476d1ce4e5b9ull;
        x ^= x >> 27;
        x *= 0x94d049bb133111ebull;
        x ^= x >> 31;
        return (size_t)x;
    }

    // return true if should expand (new or better g)
    bool tryInsert(uint64_t m, uint16_t r, int g) {
        if (count * 10 > tab.size() * 7) rehash();
        size_t i = hash(m, r) & maskBits;
        for (;;) {
            VisEntry& e = tab[i];
            if (!e.used) {
                e.used = 1;
                e.mask = m;
                e.minR = r;
                e.g = g;
                count++;
                return true;
            }
            if (e.mask == m && e.minR == r) {
                if (g < e.g) {
                    e.g = g;
                    return true;
                }
                return false;
            }
            i = (i + 1) & maskBits;
        }
    }

    void rehash() {
        auto old = std::move(tab);
        size_t nsz = old.size() * 2;
        tab.assign(nsz, VisEntry{0, 0, 0, 0});
        maskBits = nsz - 1;
        count = 0;
        for (auto& e : old) {
            if (e.used) tryInsert(e.mask, e.minR, e.g);
        }
    }
};

// ---------------- Solver ----------------
struct Solver {
    int H = 0, WW = 0, N = 0, NB = 0;
    std::vector<int> cellX, cellY;
    std::vector<uint8_t> wall, isGoal, dead, degree;
    std::vector<int16_t> xyToId, goalDist, neigh, pushTo, pushFrom;
    int startPlayer = 0;
    uint64_t startMask = 0;
    uint64_t goalBitMask = 0; // all goal cells bits (for win: (mask & ~goalBitMask)==0)
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

    std::vector<uint32_t> visitGen;
    std::vector<int16_t> bfsQ;
    uint32_t gen = 1;

    int computeReach(int player, uint64_t mask) {
        ++gen;
        if (gen >= 0xfffffff0u) {
            std::fill(visitGen.begin(), visitGen.end(), 0);
            gen = 1;
        }
        int qh = 0, qt = 0, minR = player;
        bfsQ[qt++] = (int16_t)player;
        visitGen[player] = gen;
        const uint32_t g = gen;
        while (qh < qt) {
            int c = bfsQ[qh++];
            if (c < minR) minR = c;
            const int base = c << 2;
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

    inline bool canReach(int c) const { return visitGen[c] == gen; }

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

    // incremental: remove box from, add box to (single step); for tunnel loop outside
    inline int hDelta(int from, int to) const {
        return (int)goalDist[to] - (int)goalDist[from];
    }

    inline bool isWin(uint64_t mask) const {
        return (mask & ~goalBitMask) == 0;
    }

    bool is2x2(uint64_t mask, int movedTo) const {
        int x = cellX[movedTo], y = cellY[movedTo];
        for (int ox = -1; ox <= 0; ox++) {
            for (int oy = -1; oy <= 0; oy++) {
                bool all = true, anyG = false;
                for (int dx = 0; dx <= 1 && all; dx++) {
                    for (int dy = 0; dy <= 1; dy++) {
                        int cx = x + ox + dx, cy = y + oy + dy;
                        if (cx < 0 || cy < 0 || cx >= WW || cy >= H || wall[flat(cx, cy)]) {
                            all = false;
                            break;
                        }
                        int id = xyToId[flat(cx, cy)];
                        if (id < 0 || !(mask & BITS[id])) {
                            all = false;
                            break;
                        }
                        if (isGoal[id]) anyG = true;
                    }
                }
                if (all && !anyG) return true;
            }
        }
        return false;
    }

    // Node: path via parent + tunnel (dir,count) + box start cell
    struct Node {
        uint64_t mask;
        int parent;
        int16_t player;
        int16_t g;
        int16_t h;
        int16_t boxFrom; // first box cell of this push/tunnel
        uint8_t dir;     // 0..3
        uint8_t count;   // tunnel length
    };

    struct Result {
        bool ok = false;
        int ms = 0, nodes = 0, expansions = 0, pushes = 0, visited = 0;
        std::string path, playerPath, dir;
    };

    std::string reconstruct(const std::vector<Node>& nodes, int ci) const {
        std::string path;
        int p = ci;
        std::vector<std::pair<int, int>> segs; // dir, count
        while (p > 0) {
            segs.push_back({nodes[p].dir, nodes[p].count});
            p = nodes[p].parent;
        }
        std::reverse(segs.begin(), segs.end());
        for (auto& s : segs) {
            for (int i = 0; i < s.second; i++) path.push_back(DCH[s.first]);
        }
        return path;
    }

    // 精确重建：每段 (boxFrom cell id, dir, count)
    struct PushSeg {
        int boxFrom, dir, count;
    };
    std::vector<PushSeg> reconstructSegs(const std::vector<Node>& nodes, int ci) const {
        std::vector<PushSeg> segs;
        int p = ci;
        while (p > 0) {
            segs.push_back({nodes[p].boxFrom, nodes[p].dir, nodes[p].count});
            p = nodes[p].parent;
        }
        std::reverse(segs.begin(), segs.end());
        return segs;
    }

    std::string segsToPlayerPath(const std::vector<PushSeg>& segs) {
        // board state
        uint64_t mask = startMask;
        int px = startPlayer;
        std::string full;

        auto walkTo = [&](int fromCell, int toCell, uint64_t m) -> std::string {
            if (fromCell == toCell) return "";
            // BFS on cell ids
            std::vector<int16_t> par(N, -2);
            std::vector<uint8_t> pm(N, 0);
            std::vector<int16_t> q(N);
            int qh = 0, qt = 0;
            q[qt++] = (int16_t)fromCell;
            par[fromCell] = -1;
            while (qh < qt) {
                int c = q[qh++];
                if (c == toCell) break;
                int base = c << 2;
                for (int d = 0; d < 4; d++) {
                    int n = neigh[base + d];
                    if (n < 0 || par[n] != -2) continue;
                    if (m & BITS[n]) continue;
                    par[n] = (int16_t)c;
                    pm[n] = (uint8_t)d;
                    q[qt++] = (int16_t)n;
                }
            }
            if (par[toCell] == -2) return {}; // fail
            std::string w;
            int c = toCell;
            while (par[c] >= 0) {
                w.push_back(DCH[pm[c]]);
                c = par[c];
            }
            std::reverse(w.begin(), w.end());
            return w;
        };

        for (auto& s : segs) {
            int b = s.boxFrom;
            int d = s.dir;
            // player stands at pushFrom[b*4+d] for first push
            int stand = pushFrom[b * 4 + d];
            if (stand < 0) return {};
            std::string w = walkTo(px, stand, mask);
            if (w.empty() && px != stand) return {};
            full += w;
            // apply tunnel pushes
            int curBox = b;
            for (int i = 0; i < s.count; i++) {
                int to = pushTo[curBox * 4 + d];
                if (to < 0) return {};
                full.push_back((char)std::toupper((unsigned char)DCH[d]));
                mask ^= BITS[curBox] ^ BITS[to];
                px = curBox; // player on old box cell
                curBox = to;
            }
        }
        if (!isWin(mask)) return {};
        return full;
    }

    // ---- 4-ary min-heap on (f, idx) ----
    struct Heap {
        std::vector<std::pair<int, int>> a; // f, nodeIdx
        void clear() { a.clear(); }
        bool empty() const { return a.empty(); }
        void push(int f, int idx) {
            a.push_back({f, idx});
            siftUp((int)a.size() - 1);
        }
        std::pair<int, int> pop() {
            auto top = a[0];
            a[0] = a.back();
            a.pop_back();
            if (!a.empty()) siftDown(0);
            return top;
        }
        void siftUp(int i) {
            while (i > 0) {
                int p = (i - 1) >> 2;
                if (a[p].first <= a[i].first) break;
                std::swap(a[p], a[i]);
                i = p;
            }
        }
        void siftDown(int i) {
            int n = (int)a.size();
            for (;;) {
                int best = i;
                for (int k = 1; k <= 4; k++) {
                    int c = (i << 2) + k;
                    if (c < n && a[c].first < a[best].first) best = c;
                }
                if (best == i) break;
                std::swap(a[i], a[best]);
                i = best;
            }
        }
    };

    void ensureBuf() {
        if ((int)visitGen.size() != N) {
            visitGen.assign(N, 0);
            bfsQ.assign(N, 0);
            gen = 1;
        }
    }

    Result solveBF(int timeLimitMs, int Wweight) {
        // Wweight 0 = pure greedy f=h; else f = g + W*h
        Result res;
        res.dir = Wweight == 0 ? "bf" : (Wweight == 1 ? "astar" : "wastar");
        auto T0 = Clock::now();
        ensureBuf();

        int h0 = heuristic(startMask);
        if (h0 >= 999999) return res;

        VisMap visited;
        visited.clear(1 << 22);
        std::vector<Node> nodes;
        nodes.reserve(1 << 22);
        Heap heap;

        int min0 = computeReach(startPlayer, startMask);
        nodes.push_back({startMask, -1, (int16_t)startPlayer, 0, (int16_t)h0, (int16_t)-1, 0, 0});
        int f0 = Wweight == 0 ? h0 : Wweight * h0;
        heap.push(f0, 0);
        visited.tryInsert(startMask, (uint16_t)min0, 0);

        int expansions = 0, nodeCount = 0;

        while (!heap.empty()) {
            if ((expansions & 65535) == 0 && expansions > 0) {
                auto elapsed = std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
                if (timeLimitMs > 0 && elapsed > timeLimitMs) {
                    res.ms = (int)elapsed;
                    res.nodes = nodeCount;
                    res.expansions = expansions;
                    res.visited = (int)visited.count;
                    return res;
                }
                if (timeLimitMs <= 0) {
                    std::cout << "  BF progress exp=" << expansions << " nodes=" << nodeCount
                              << " visited=" << visited.count << " ms=" << elapsed << "\n";
                    std::cout.flush();
                }
            }
            auto [fcur, ci] = heap.pop();
            const Node cur = nodes[ci]; // copy
            // stale: f may be outdated but we only skip if worse g was stored? skip recheck via g
            expansions++;

            if (isWin(cur.mask)) {
                res.ok = true;
                res.path = reconstruct(nodes, ci);
                res.playerPath = segsToPlayerPath(reconstructSegs(nodes, ci));
                res.pushes = cur.g;
                res.ms = (int)std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
                res.nodes = nodeCount;
                res.expansions = expansions;
                res.visited = (int)visited.count;
                return res;
            }

            computeReach(cur.player, cur.mask);
            const uint64_t curMask = cur.mask;
            const int curH = cur.h;
            const int curG = cur.g;

            uint64_t bm = curMask;
            while (bm) {
                int b = __builtin_ctzll(bm);
                bm &= bm - 1;
                int base = b << 2;
                for (int d = 0; d < 4; d++) {
                    int to = pushTo[base + d];
                    if (to < 0) continue;
                    if (curMask & BITS[to]) continue;
                    int from = pushFrom[base + d];
                    if (!canReach(from)) continue;
                    if (dead[to]) continue;

                    uint64_t nm = curMask ^ BITS[b] ^ BITS[to];
                    int fTo = to, fPl = b, pc = 1;
                    int nh = curH + hDelta(b, to);
                    while (degree[fTo] == 2 && !isGoal[fTo]) {
                        int nx = pushTo[(fTo << 2) + d];
                        if (nx < 0 || (nm & BITS[nx]) || dead[nx]) break;
                        nh += hDelta(fTo, nx);
                        nm ^= BITS[fTo] ^ BITS[nx];
                        fPl = fTo;
                        fTo = nx;
                        pc++;
                        if (pc > 12) break;
                    }
                    if (nh < 0) nh = 0; // safety
                    if (nh >= 999999) continue;
                    if (is2x2(nm, fTo)) continue;

                    int minR = computeReach(fPl, nm);
                    computeReach(cur.player, curMask); // restore

                    int ng = curG + pc;
                    if (!visited.tryInsert(nm, (uint16_t)minR, ng)) continue;

                    int f = Wweight == 0 ? nh : (ng + Wweight * nh);
                    int ni = (int)nodes.size();
                    nodes.push_back({nm, ci, (int16_t)fPl, (int16_t)ng, (int16_t)nh, (int16_t)b, (uint8_t)d, (uint8_t)pc});
                    heap.push(f, ni);
                    nodeCount++;
                }
            }
        }
        res.ms = (int)std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
        res.nodes = nodeCount;
        res.expansions = expansions;
        res.visited = (int)visited.count;
        return res;
    }

    // Greedy DFS: order children by nh ascending, depth-first — often finds any solution faster
    Result solveDFS(int timeLimitMs, int maxExpansions = 0) {
        // maxExpansions>0: also stop after this many expansions (anti-OOM for hard levels)
        Result res;
        res.dir = "dfs";
        auto T0 = Clock::now();
        ensureBuf();

        int h0 = heuristic(startMask);
        if (h0 >= 999999) return res;

        VisMap visited;
        visited.clear(1 << 22);
        std::vector<Node> nodes;
        nodes.reserve(1 << 20);
        if (maxExpansions <= 0) maxExpansions = 8000000; // hard cap even if unlimited

        struct Frame {
            int ni;
            int nextChild; // index into children
            std::vector<int> children; // node indices of generated children
        };

        // iterative DFS with pre-sorted children
        int min0 = computeReach(startPlayer, startMask);
        nodes.push_back({startMask, -1, (int16_t)startPlayer, 0, (int16_t)h0, (int16_t)-1, 0, 0});
        visited.tryInsert(startMask, (uint16_t)min0, 0);

        std::vector<Frame> stack;
        stack.reserve(256);

        auto genChildren = [&](int ci) -> std::vector<int> {
            const Node cur = nodes[ci];
            computeReach(cur.player, cur.mask);
            struct Cand {
                uint64_t nm;
                int fPl, nh, pc, d, minR, boxFrom;
            };
            std::vector<Cand> cands;
            cands.reserve(NB * 4);

            uint64_t bm = cur.mask;
            while (bm) {
                int b = __builtin_ctzll(bm);
                bm &= bm - 1;
                int base = b << 2;
                for (int d = 0; d < 4; d++) {
                    int to = pushTo[base + d];
                    if (to < 0 || (cur.mask & BITS[to])) continue;
                    int from = pushFrom[base + d];
                    if (!canReach(from) || dead[to]) continue;

                    uint64_t nm = cur.mask ^ BITS[b] ^ BITS[to];
                    int fTo = to, fPl = b, pc = 1;
                    int nh = cur.h + hDelta(b, to);
                    while (degree[fTo] == 2 && !isGoal[fTo]) {
                        int nx = pushTo[(fTo << 2) + d];
                        if (nx < 0 || (nm & BITS[nx]) || dead[nx]) break;
                        nh += hDelta(fTo, nx);
                        nm ^= BITS[fTo] ^ BITS[nx];
                        fPl = fTo;
                        fTo = nx;
                        pc++;
                        if (pc > 12) break;
                    }
                    if (nh < 0 || nh >= 999999) continue;
                    if (is2x2(nm, fTo)) continue;
                    int minR = computeReach(fPl, nm);
                    computeReach(cur.player, cur.mask);
                    cands.push_back({nm, fPl, nh, pc, d, minR, b});
                }
            }
            std::sort(cands.begin(), cands.end(), [](const Cand& a, const Cand& b) {
                return a.nh < b.nh;
            });

            std::vector<int> childIdx;
            for (auto& c : cands) {
                int ng = cur.g + c.pc;
                if (!visited.tryInsert(c.nm, (uint16_t)c.minR, ng)) continue;
                int ni = (int)nodes.size();
                nodes.push_back({c.nm, ci, (int16_t)c.fPl, (int16_t)ng, (int16_t)c.nh, (int16_t)c.boxFrom, (uint8_t)c.d, (uint8_t)c.pc});
                childIdx.push_back(ni);
            }
            return childIdx;
        };

        stack.push_back({0, 0, genChildren(0)});
        int expansions = 0, nodeCount = 0;

        while (!stack.empty()) {
            if ((expansions & 1023) == 0) {
                if (timeLimitMs > 0) {
                    auto elapsed = std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
                    if (elapsed > timeLimitMs) {
                        res.ms = (int)elapsed;
                        res.nodes = nodeCount;
                        res.expansions = expansions;
                        res.visited = (int)visited.count;
                        return res;
                    }
                }
                if (expansions >= maxExpansions || (int)nodes.size() > 12000000) {
                    res.ms = (int)std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
                    res.nodes = nodeCount;
                    res.expansions = expansions;
                    res.visited = (int)visited.count;
                    return res;
                }
            }
            Frame& fr = stack.back();
            expansions++;
            const Node& cur = nodes[fr.ni];
            if (isWin(cur.mask)) {
                res.ok = true;
                res.path = reconstruct(nodes, fr.ni);
                res.playerPath = segsToPlayerPath(reconstructSegs(nodes, fr.ni));
                res.pushes = cur.g;
                res.ms = (int)std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
                res.nodes = nodeCount;
                res.expansions = expansions;
                res.visited = (int)visited.count;
                return res;
            }
            if (fr.nextChild >= (int)fr.children.size()) {
                stack.pop_back();
                continue;
            }
            int child = fr.children[fr.nextChild++];
            nodeCount++;
            // 限制栈深度，过深改由 BF 处理
            if ((int)stack.size() > 500) continue;
            stack.push_back({child, 0, genChildren(child)});
        }
        res.ms = (int)std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
        res.nodes = nodeCount;
        res.expansions = expansions;
        res.visited = (int)visited.count;
        return res;
    }

    Result solve(int timeLimitMs, const std::string& mode) {
        if (mode == "dfs") return solveDFS(timeLimitMs);
        if (mode == "astar") return solveBF(timeLimitMs, 1);
        if (mode == "wastar") return solveBF(timeLimitMs, 4);
        if (mode == "bf" || mode == "greedy") return solveBF(timeLimitMs, 0);
        // auto unlimited: DFS with expansion cap, then BF unlimited
        if (timeLimitMs <= 0) {
            auto r = solveDFS(0, 5000000);
            if (r.ok) {
                r.dir = "auto/dfs";
                return r;
            }
            std::cout << "  DFS exhausted (exp=" << r.expansions << "), switching to BF...\n";
            std::cout.flush();
            auto r2 = solveBF(0, 0);
            r2.nodes += r.nodes;
            r2.expansions += r.expansions;
            r2.dir = r2.ok ? "auto/bf" : "auto";
            return r2;
        }
        auto T0 = Clock::now();
        int t1 = timeLimitMs * 2 / 5;
        auto r = solveDFS(t1);
        if (r.ok) {
            r.dir = "auto/dfs";
            return r;
        }
        int used = (int)std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
        int left = timeLimitMs - used;
        if (left < 50) {
            r.dir = "auto";
            return r;
        }
        auto r2 = solveBF(left, 0);
        r2.nodes += r.nodes;
        r2.expansions += r.expansions;
        r2.ms = (int)std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
        r2.dir = r2.ok ? "auto/bf" : "auto";
        return r2;
    }
};

// 扫描 levels.json，返回所有 id（按出现顺序）
static std::vector<int> listAllIds(const std::string& json) {
    std::vector<int> ids;
    size_t pos = 0;
    while (true) {
        size_t idKey = json.find("\"id\"", pos);
        if (idKey == std::string::npos) break;
        size_t colon = json.find(':', idKey);
        size_t numStart = json.find_first_of("-0123456789", colon + 1);
        size_t numEnd = numStart;
        if (numStart == std::string::npos) break;
        if (json[numEnd] == '-') numEnd++;
        while (numEnd < json.size() && json[numEnd] >= '0' && json[numEnd] <= '9') numEnd++;
        ids.push_back(std::stoi(json.substr(numStart, numEnd - numStart)));
        pos = numEnd;
    }
    return ids;
}

static void writeAllJsonCopies(const std::string& primaryPath, int levelId, const std::string& playerPath) {
    std::vector<std::string> outs = {
        primaryPath,
        "levels.json",
        "c_app/levels.json",
        "sokoban_linux/levels.json",
    };
    std::vector<std::string> written;
    for (auto& p : outs) {
        auto s = readFile(p);
        if (s.empty()) continue;
        bool dup = false;
        for (auto& w : written)
            if (w == p) dup = true;
        if (dup) continue;
        if (writeSolutionToJson(p, levelId, playerPath)) {
            std::cout << "  Wrote " << p << "\n";
            written.push_back(p);
        }
    }
}

// Convert push path to full player LURD (uppercase push, lowercase walk)
static std::string pushesToPlayerPath(const std::vector<std::string>& puzzle,
                                      const std::string& pushes) {
    // rebuild simple board
    int H = (int)puzzle.size();
    int WW = 0;
    for (auto& r : puzzle) WW = std::max(WW, (int)r.size());
    std::vector<std::string> rows = puzzle;
    for (auto& r : rows)
        if ((int)r.size() < WW) r.append(WW - (int)r.size(), '#');

    auto isWall = [&](int x, int y) {
        if (x < 0 || y < 0 || x >= WW || y >= H) return true;
        return rows[y][x] == '#';
    };
    auto key = [](int x, int y) { return y * 64 + x; };

    std::vector<char> board(WW * H, ' ');
    int px = 0, py = 0;
    std::vector<std::pair<int, int>> boxes;
    std::vector<std::pair<int, int>> goals;
    for (int y = 0; y < H; y++) {
        for (int x = 0; x < WW; x++) {
            char c = rows[y][x];
            if (c == '#') board[y * WW + x] = '#';
            if (c == '.' || c == '*' || c == '+') goals.push_back({x, y});
            if (c == '$' || c == '*') boxes.push_back({x, y});
            if (c == '@' || c == '+') { px = x; py = y; }
        }
    }

    const int DX[4] = {0, 0, -1, 1};
    const int DY[4] = {-1, 1, 0, 0};
    const char DCH[4] = {'u', 'd', 'l', 'r'};
    auto dirIdx = [&](char c) {
        c = (char)std::tolower((unsigned char)c);
        for (int i = 0; i < 4; i++) if (DCH[i] == c) return i;
        return -1;
    };

    auto hasBox = [&](int x, int y) {
        for (auto& b : boxes)
            if (b.first == x && b.second == y) return true;
        return false;
    };

    std::string full;
    for (char pch : pushes) {
        int d = dirIdx(pch);
        if (d < 0) continue;
        // BFS from player to find path to a push cell
        const int MAXC = 64 * 64;
        std::vector<int> parent(MAXC, -2);
        std::vector<char> pmove(MAXC, 0);
        std::vector<int> q;
        int start = key(px, py);
        parent[start] = -1;
        q.push_back(start);
        for (size_t qi = 0; qi < q.size(); qi++) {
            int cur = q[qi];
            int cx = cur % 64, cy = cur / 64;
            for (int dd = 0; dd < 4; dd++) {
                int nx = cx + DX[dd], ny = cy + DY[dd];
                if (isWall(nx, ny) || hasBox(nx, ny)) continue;
                int nk = key(nx, ny);
                if (parent[nk] != -2) continue;
                parent[nk] = cur;
                pmove[nk] = DCH[dd];
                q.push_back(nk);
            }
        }
        // find box pushable in dir d
        int bestWalk = 1e9, bestBi = -1, bestFx = 0, bestFy = 0;
        for (int bi = 0; bi < (int)boxes.size(); bi++) {
            int bx = boxes[bi].first, by = boxes[bi].second;
            int tx = bx + DX[d], ty = by + DY[d];
            int fx = bx - DX[d], fy = by - DY[d];
            if (isWall(tx, ty) || hasBox(tx, ty)) continue;
            if (isWall(fx, fy) || hasBox(fx, fy)) continue;
            int fk = key(fx, fy);
            if (parent[fk] == -2) continue;
            // walk length
            int len = 0, c = fk;
            while (parent[c] >= 0) { len++; c = parent[c]; }
            if (len < bestWalk) {
                bestWalk = len;
                bestBi = bi;
                bestFx = fx;
                bestFy = fy;
            }
        }
        if (bestBi < 0) return {}; // fail
        // reconstruct walk
        std::string walk;
        int c = key(bestFx, bestFy);
        while (parent[c] >= 0) {
            walk.push_back(pmove[c]);
            c = parent[c];
        }
        std::reverse(walk.begin(), walk.end());
        full += walk;
        full.push_back((char)std::toupper((unsigned char)DCH[d]));
        // apply push
        int bx = boxes[bestBi].first, by = boxes[bestBi].second;
        boxes[bestBi] = {bx + DX[d], by + DY[d]};
        px = bx;
        py = by;
    }
    // verify win
    for (auto& b : boxes) {
        bool on = false;
        for (auto& g : goals)
            if (g == b) on = true;
        if (!on) return {};
    }
    return full;
}

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
    int timeLimit = 0; // 0 = unlimited
    std::string mode = "auto";
    bool doWrite = false;
    bool batch = false;

    for (int i = 1; i < argc; i++) {
        std::string a = argv[i];
        if (a == "--write") doWrite = true;
        else if (a == "--batch") batch = true;
        else if (a == "bf" || a == "dfs" || a == "auto" || a == "wastar" || a == "astar" || a == "greedy")
            mode = a;
        else if (a == "0" || (a.size() && (a[0] == '-' || (a[0] >= '0' && a[0] <= '9')))) {
            // number: first is levelId (if not batch), next is timeLimit
            int v = std::atoi(a.c_str());
            if (!batch && levelId == -99999) levelId = v;
            else timeLimit = v;
        }
    }
    if (batch) doWrite = true; // batch always writes

    std::string path = findLevelsJson();
    if (path.empty()) {
        std::cerr << "levels.json not found\n";
        return 1;
    }

    auto processOne = [&](int id, int& solved, int& failed, int& skipped) {
        // re-read json each time so we pick up new solutions / avoid stale
        std::string json = readFile(path);
        LevelData level;
        if (!loadLevelById(json, id, level)) {
            std::cout << "[skip] id=" << id << " not found\n";
            skipped++;
            return;
        }
        if (!level.solution.empty() && level.solution != "null") {
            std::cout << "[skip] id=" << id << " " << level.name << " already has solution\n";
            skipped++;
            return;
        }

        std::cout << "\n========== id=" << level.id << " " << level.name << " ==========\n";
        for (auto& r : level.puzzle) std::cout << "  " << r << "\n";

        Solver solver;
        if (!solver.build(level.puzzle)) {
            std::cout << "BUILD FAIL (N too large or parse)\n";
            failed++;
            return;
        }
        std::cout << "N=" << solver.N << " boxes=" << solver.NB
                  << " limit=" << (timeLimit <= 0 ? "unlimited" : std::to_string(timeLimit) + "ms")
                  << " mode=" << mode << "\n";
        std::cout.flush();

        auto res = solver.solve(timeLimit, mode);
        if (!res.ok) {
            std::cout << "FAILED ms=" << res.ms << " nodes=" << res.nodes
                      << " exp=" << res.expansions << " visited=" << res.visited
                      << " dir=" << res.dir << "\n";
            failed++;
            return;
        }

        std::string playerPath = res.playerPath;
        if (playerPath.empty()) playerPath = pushesToPlayerPath(level.puzzle, res.path);
        if (playerPath.empty()) {
            std::cout << "WARN: no player path, using pushes\n";
            playerPath = res.path;
        }

        std::cout << "SOLVED ms=" << res.ms << " pushes=" << res.pushes
                  << " nodes=" << res.nodes << " exp=" << res.expansions
                  << " dir=" << res.dir << " playerMoves=" << playerPath.size() << "\n";
        std::cout << "player: " << playerPath << "\n";

        if (doWrite) {
            writeAllJsonCopies(path, id, playerPath);
        }
        solved++;
        std::cout.flush();
    };

    if (batch) {
        std::string json = readFile(path);
        auto ids = listAllIds(json);
        // collect unsolved with box counts, sort easy first
        struct Item {
            int id, boxes;
            std::string name;
        };
        std::vector<Item> todo;
        for (int id : ids) {
            LevelData L;
            if (!loadLevelById(json, id, L)) continue;
            if (!L.solution.empty() && L.solution != "null") continue;
            int boxes = 0;
            for (auto& row : L.puzzle)
                for (char c : row)
                    if (c == '$' || c == '*') boxes++;
            todo.push_back({id, boxes, L.name});
        }
        std::sort(todo.begin(), todo.end(), [](const Item& a, const Item& b) {
            if (a.boxes != b.boxes) return a.boxes < b.boxes;
            return a.id < b.id;
        });

        std::cout << "BATCH: " << todo.size() << " unsolved levels, mode=" << mode
                  << " timeLimit=" << (timeLimit <= 0 ? "unlimited" : std::to_string(timeLimit))
                  << "\n";
        int solved = 0, failed = 0, skipped = 0;
        auto batchT0 = Clock::now();
        for (size_t i = 0; i < todo.size(); i++) {
            std::cout << "\n>>> [" << (i + 1) << "/" << todo.size() << "] boxes=" << todo[i].boxes
                      << " id=" << todo[i].id << " " << todo[i].name << "\n";
            processOne(todo[i].id, solved, failed, skipped);
            auto elapsed = std::chrono::duration_cast<ms_t>(Clock::now() - batchT0).count();
            std::cout << "--- progress solved=" << solved << " failed=" << failed
                      << " skipped=" << skipped << " elapsed=" << (elapsed / 1000.0) << "s ---\n";
            std::cout.flush();
        }
        std::cout << "\n========== BATCH DONE ==========\n";
        std::cout << "solved=" << solved << " failed=" << failed << " skipped=" << skipped << "\n";
        std::cout << "Run: node scripts/gen_levels_js.js  to sync HTML\n";
        return failed ? 2 : 0;
    }

    // single level
    if (levelId == -99999) {
        std::cerr << "Usage:\n  sokosolve <id> [timeMs] [mode] [--write]\n"
                     "  sokosolve --batch [timeMs] [mode]   # timeMs=0 unlimited, always --write\n";
        return 1;
    }
    int solved = 0, failed = 0, skipped = 0;
    processOne(levelId, solved, failed, skipped);
    if (doWrite) std::cout << "Run: node scripts/gen_levels_js.js  to sync HTML\n";
    return failed ? 2 : 0;
}
