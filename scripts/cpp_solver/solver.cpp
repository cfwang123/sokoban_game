/**
 * Sokoban C++ 高速求解器 v3
 * - 256-bit 箱掩码（最多 256 地板格）
 * - Greedy BF / DFS / auto
 * - 批量 --batch：按箱子数从少到多，时间不限，解完即写
 *
 * 编译: g++ -O3 -std=c++17 -march=native -o sokosolve.exe solver.cpp
 * 用法:
 *   sokosolve <id> [timeMs] [mode] [--write]   # timeMs=0 不限时
 *   sokosolve --batch [timeMs] [mode]
 */
#include <algorithm>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

using Clock = std::chrono::steady_clock;
using ms_t = std::chrono::milliseconds;

// ===================== 256-bit mask =====================
struct BitMask {
    static constexpr int WORDS = 4; // 256 bits
    uint64_t w[WORDS]{};

    void clear() { w[0] = w[1] = w[2] = w[3] = 0; }
    bool empty() const { return !(w[0] | w[1] | w[2] | w[3]); }
    void set(int i) { w[i >> 6] |= 1ull << (i & 63); }
    void reset(int i) { w[i >> 6] &= ~(1ull << (i & 63)); }
    bool test(int i) const { return (w[i >> 6] >> (i & 63)) & 1ull; }
    void flip(int i) { w[i >> 6] ^= 1ull << (i & 63); }

    BitMask operator^(const BitMask& o) const {
        BitMask r;
        for (int i = 0; i < WORDS; i++) r.w[i] = w[i] ^ o.w[i];
        return r;
    }
    BitMask operator&(const BitMask& o) const {
        BitMask r;
        for (int i = 0; i < WORDS; i++) r.w[i] = w[i] & o.w[i];
        return r;
    }
    BitMask operator~() const {
        BitMask r;
        for (int i = 0; i < WORDS; i++) r.w[i] = ~w[i];
        return r;
    }
    bool operator==(const BitMask& o) const {
        return w[0] == o.w[0] && w[1] == o.w[1] && w[2] == o.w[2] && w[3] == o.w[3];
    }
    bool operator!=(const BitMask& o) const { return !(*this == o); }

    // iterate set bits: for (int b; (b = next()) >= 0; )
    struct Iter {
        const BitMask* m;
        int wi, bit;
        int next() {
            while (wi < WORDS) {
                uint64_t x = m->w[wi] >> bit;
                if (x) {
                    int tz = __builtin_ctzll(x);
                    int idx = (wi << 6) + bit + tz;
                    bit += tz + 1;
                    if (bit >= 64) { wi++; bit = 0; }
                    return idx;
                }
                wi++;
                bit = 0;
            }
            return -1;
        }
    };
    Iter iter() const { return Iter{this, 0, 0}; }

    size_t hash() const {
        uint64_t h = w[0];
        h ^= w[1] * 0x9e3779b97f4a7c15ull;
        h ^= w[2] * 0xbf58476d1ce4e5b9ull;
        h ^= w[3] * 0x94d049bb133111ebull;
        h ^= h >> 33;
        return (size_t)h;
    }
};

// ===================== JSON helpers =====================
struct LevelData {
    int id = -999;
    std::string name;
    std::vector<std::string> puzzle;
    std::string solution;
};

static std::string readFile(const std::string& path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) return {};
    return std::string((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
}

static bool loadLevelById(const std::string& json, int wantId, LevelData& out) {
    size_t pos = 0;
    while (true) {
        size_t idKey = json.find("\"id\"", pos);
        if (idKey == std::string::npos) return false;
        size_t colon = json.find(':', idKey);
        size_t numStart = json.find_first_of("-0123456789", colon + 1);
        if (numStart == std::string::npos) return false;
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
        out.solution.clear();
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

        size_t sk = json.find("\"solution\"", objStart);
        if (sk == std::string::npos || sk >= objEnd) {
            json.insert(objEnd - 1, ",\n    \"solution\": \"" + solution + "\"");
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
            } else return false;
        }
        std::ofstream out(path, std::ios::binary);
        out << json;
        return true;
    }
}

static std::vector<int> listAllIds(const std::string& json) {
    std::vector<int> ids;
    size_t pos = 0;
    while (true) {
        size_t idKey = json.find("\"id\"", pos);
        if (idKey == std::string::npos) break;
        size_t colon = json.find(':', idKey);
        size_t numStart = json.find_first_of("-0123456789", colon + 1);
        if (numStart == std::string::npos) break;
        size_t numEnd = numStart;
        if (json[numEnd] == '-') numEnd++;
        while (numEnd < json.size() && json[numEnd] >= '0' && json[numEnd] <= '9') numEnd++;
        ids.push_back(std::stoi(json.substr(numStart, numEnd - numStart)));
        pos = numEnd;
    }
    return ids;
}

static std::string findLevelsJson() {
    for (const char* p : {"levels.json", "../levels.json", "../../levels.json",
                          "D:/VS_Projects/AIPrototype/game/sokoban/levels.json"}) {
        if (!readFile(p).empty()) return p;
    }
    return {};
}

static void writeAllJsonCopies(const std::string& primary, int id, const std::string& sol) {
    for (const std::string& p : {primary, std::string("levels.json"),
                                 std::string("c_app/levels.json"),
                                 std::string("sokoban_linux/levels.json")}) {
        if (readFile(p).empty()) continue;
        if (writeSolutionToJson(p, id, sol))
            std::cout << "  Wrote " << p << "\n";
    }
}

// ===================== Visited hash (open addressing) =====================
struct VisKey {
    BitMask mask;
    uint16_t minR;
};

struct VisEntry {
    BitMask mask;
    uint16_t minR;
    int g;
    uint8_t used;
};

struct VisMap {
    std::vector<VisEntry> tab;
    size_t maskBits = 0;
    size_t count = 0;

    void clear(size_t capPow2 = 1 << 20) {
        tab.assign(capPow2, VisEntry{});
        maskBits = capPow2 - 1;
        count = 0;
    }

    static size_t hash(const BitMask& m, uint16_t r) {
        return m.hash() ^ (size_t(r) * 0x9e3779b9u);
    }

    std::mutex mu;

    bool tryInsert(const BitMask& m, uint16_t r, int g) {
        std::lock_guard<std::mutex> lk(mu);
        return tryInsertUnlocked(m, r, g);
    }

    bool tryInsertUnlocked(const BitMask& m, uint16_t r, int g) {
        if (count * 10 > tab.size() * 7) rehashUnlocked();
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
            if (e.minR == r && e.mask == m) {
                if (g < e.g) { e.g = g; return true; }
                return false;
            }
            i = (i + 1) & maskBits;
        }
    }

    void rehashUnlocked() {
        auto old = std::move(tab);
        size_t nsz = old.size() * 2;
        tab.assign(nsz, VisEntry{});
        maskBits = nsz - 1;
        count = 0;
        for (auto& e : old)
            if (e.used) tryInsertUnlocked(e.mask, e.minR, e.g);
    }
};

// ===================== Solver =====================
struct Solver {
    int H = 0, WW = 0, N = 0, NB = 0;
    std::vector<int> cellX, cellY;
    std::vector<uint8_t> wall, isGoal, dead, degree;
    std::vector<int16_t> xyToId, goalDist, neigh, pushTo, pushFrom;
    int startPlayer = 0;
    BitMask startMask, goalBitMask;

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
        cellX.clear();
        cellY.clear();
        std::vector<int> startBoxes, goals;
        int sx = 0, sy = 0;
        for (int y = 0; y < H; y++) {
            for (int x = 0; x < WW; x++) {
                char c = rows[y][x];
                if (c == '#') {
                    wall[flat(x, y)] = 1;
                    continue;
                }
                int id = (int)cellX.size();
                cellX.push_back(x);
                cellY.push_back(y);
                xyToId[flat(x, y)] = (int16_t)id;
                if (c == '.' || c == '*' || c == '+') goals.push_back(id);
                if (c == '$' || c == '*') startBoxes.push_back(id);
                if (c == '@' || c == '+') {
                    sx = x;
                    sy = y;
                }
            }
        }
        N = (int)cellX.size();
        NB = (int)startBoxes.size();
        if (N > 256) {
            std::cerr << "N=" << N << " > 256\n";
            return false;
        }
        isGoal.assign(N, 0);
        goalBitMask.clear();
        for (int g : goals) {
            isGoal[g] = 1;
            goalBitMask.set(g);
        }
        startPlayer = xyToId[flat(sx, sy)];
        startMask.clear();
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
            if (goalDist[i] >= 32000) {
                dead[i] = 1;
                continue;
            }
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
            for (int d = 0; d < 4; d++)
                if (neigh[i * 4 + d] >= 0) deg++;
            degree[i] = (uint8_t)deg;
        }
        return true;
    }

    // 线程局部可达 BFS 缓冲（多线程安全）
    struct ReachBuf {
        std::vector<uint32_t> visitGen;
        std::vector<int16_t> bfsQ;
        uint32_t gen = 1;
        void ensure(int n) {
            if ((int)visitGen.size() != n) {
                visitGen.assign(n, 0);
                bfsQ.assign(n, 0);
                gen = 1;
            }
        }
    };

    int computeReach(int player, const BitMask& mask, ReachBuf& buf) const {
        buf.ensure(N);
        ++buf.gen;
        if (buf.gen >= 0xfffffff0u) {
            std::fill(buf.visitGen.begin(), buf.visitGen.end(), 0);
            buf.gen = 1;
        }
        int qh = 0, qt = 0, minR = player;
        buf.bfsQ[qt++] = (int16_t)player;
        buf.visitGen[player] = buf.gen;
        const uint32_t g = buf.gen;
        while (qh < qt) {
            int c = buf.bfsQ[qh++];
            if (c < minR) minR = c;
            int base = c << 2;
            for (int d = 0; d < 4; d++) {
                int n = neigh[base + d];
                if (n < 0 || buf.visitGen[n] == g) continue;
                if (mask.test(n)) continue;
                buf.visitGen[n] = g;
                buf.bfsQ[qt++] = (int16_t)n;
            }
        }
        return minR;
    }

    inline bool canReach(int c, const ReachBuf& buf) const {
        return buf.visitGen[c] == buf.gen;
    }

    // 兼容单线程旧调用
    mutable ReachBuf defaultReach;
    int computeReach(int player, const BitMask& mask) const {
        return computeReach(player, mask, defaultReach);
    }
    inline bool canReach(int c) const { return canReach(c, defaultReach); }

    int heuristic(const BitMask& mask) const {
        int h = 0;
        auto it = mask.iter();
        for (int i; (i = it.next()) >= 0;) {
            int d = goalDist[i];
            if (d >= 32000) return 999999;
            h += d;
        }
        return h;
    }

    inline int hDelta(int from, int to) const {
        return (int)goalDist[to] - (int)goalDist[from];
    }

    // win: every box is on a goal
    inline bool isWin(const BitMask& mask) const {
        auto it = mask.iter();
        for (int i; (i = it.next()) >= 0;) {
            if (!isGoal[i]) return false;
        }
        return true;
    }

    bool is2x2(const BitMask& mask, int movedTo) const {
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
                        if (id < 0 || !mask.test(id)) {
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

    struct Node {
        BitMask mask;
        int parent;
        int16_t player, g, h, boxFrom;
        uint8_t dir, count;
    };

    struct Result {
        bool ok = false;
        int ms = 0, nodes = 0, expansions = 0, pushes = 0, visited = 0;
        std::string path, playerPath, dir;
    };

    std::string reconstruct(const std::vector<Node>& nodes, int ci) const {
        std::string path;
        std::vector<std::pair<int, int>> segs;
        int p = ci;
        while (p > 0) {
            segs.push_back({nodes[p].dir, nodes[p].count});
            p = nodes[p].parent;
        }
        std::reverse(segs.begin(), segs.end());
        for (auto& s : segs)
            for (int i = 0; i < s.second; i++) path.push_back(DCH[s.first]);
        return path;
    }

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
        BitMask mask = startMask;
        int px = startPlayer;
        std::string full;

        auto walkTo = [&](int fromCell, int toCell, const BitMask& m) -> std::string {
            if (fromCell == toCell) return "";
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
                    if (m.test(n)) continue;
                    par[n] = (int16_t)c;
                    pm[n] = (uint8_t)d;
                    q[qt++] = (int16_t)n;
                }
            }
            if (par[toCell] == -2) return {};
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
            int stand = pushFrom[b * 4 + d];
            if (stand < 0) return {};
            std::string w = walkTo(px, stand, mask);
            if (w.empty() && px != stand) return {};
            full += w;
            int curBox = b;
            for (int i = 0; i < s.count; i++) {
                int to = pushTo[curBox * 4 + d];
                if (to < 0) return {};
                full.push_back((char)std::toupper((unsigned char)DCH[d]));
                mask.flip(curBox);
                mask.flip(to);
                px = curBox;
                curBox = to;
            }
        }
        if (!isWin(mask)) return {};
        return full;
    }

    struct Heap {
        std::vector<std::pair<int, int>> a;
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

    // 单线程 BF（dirOrder 用于打乱扩展顺序，便于多线程竞速）
    Result solveBF_ST(int timeLimitMs, int Wweight, const int dirOrder[4],
                      std::atomic<bool>* externalStop, int threadId) {
        Result res;
        res.dir = Wweight == 0 ? "bf" : (Wweight == 1 ? "astar" : "wastar");
        auto T0 = Clock::now();
        ReachBuf buf;
        buf.ensure(N);

        int h0 = heuristic(startMask);
        if (h0 >= 999999) return res;

        VisMap visited;
        visited.clear(1 << 18); // 竞速多实例，单实例哈希表缩小以省内存
        std::vector<Node> nodes;
        nodes.reserve(1 << 18);
        Heap heap;

        int min0 = computeReach(startPlayer, startMask, buf);
        nodes.push_back({startMask, -1, (int16_t)startPlayer, 0, (int16_t)h0, (int16_t)-1, 0, 0});
        int f0 = Wweight == 0 ? h0 : Wweight * h0;
        // 线程间轻微打散 f，减少重复搜索路径
        f0 += threadId;
        heap.push(f0, 0);
        visited.tryInsertUnlocked(startMask, (uint16_t)min0, 0);

        int expansions = 0, nodeCount = 0;
        int dirs[4] = {dirOrder[0], dirOrder[1], dirOrder[2], dirOrder[3]};

        while (!heap.empty()) {
            if (externalStop && externalStop->load(std::memory_order_relaxed)) break;
            if ((expansions & 65535) == 0 && expansions > 0) {
                auto elapsed = std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
                if (timeLimitMs > 0 && elapsed > timeLimitMs) break;
                if (timeLimitMs <= 0 && threadId == 0) {
                    std::cout << "  BF progress exp=" << expansions << " nodes=" << nodeCount
                              << " visited=" << visited.count << " ms=" << elapsed << "\n";
                    std::cout.flush();
                }
            }
            auto [fcur, ci] = heap.pop();
            const Node cur = nodes[ci];
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

            computeReach(cur.player, cur.mask, buf);
            const BitMask curMask = cur.mask;
            const int curH = cur.h, curG = cur.g;

            auto it = curMask.iter();
            for (int b; (b = it.next()) >= 0;) {
                int base = b << 2;
                for (int di = 0; di < 4; di++) {
                    int d = dirs[di];
                    int to = pushTo[base + d];
                    if (to < 0 || curMask.test(to)) continue;
                    int from = pushFrom[base + d];
                    if (!canReach(from, buf) || dead[to]) continue;

                    BitMask nm = curMask;
                    nm.flip(b);
                    nm.flip(to);
                    int fTo = to, fPl = b, pc = 1;
                    int nh = curH + hDelta(b, to);
                    while (degree[fTo] == 2 && !isGoal[fTo]) {
                        int nx = pushTo[(fTo << 2) + d];
                        if (nx < 0 || nm.test(nx) || dead[nx]) break;
                        nh += hDelta(fTo, nx);
                        nm.flip(fTo);
                        nm.flip(nx);
                        fPl = fTo;
                        fTo = nx;
                        pc++;
                        if (pc > 12) break;
                    }
                    if (nh < 0) nh = 0;
                    if (nh >= 999999) continue;
                    if (is2x2(nm, fTo)) continue;

                    int minR = computeReach(fPl, nm, buf);
                    computeReach(cur.player, curMask, buf);

                    int ng = curG + pc;
                    if (!visited.tryInsertUnlocked(nm, (uint16_t)minR, ng)) continue;

                    int f = Wweight == 0 ? nh : (ng + Wweight * nh);
                    // 轻微分叉：不同线程优先不同 f 偏移
                    f += (threadId * 3 + d) & 7;
                    int ni = (int)nodes.size();
                    nodes.push_back({nm, ci, (int16_t)fPl, (int16_t)ng, (int16_t)nh, (int16_t)b, (uint8_t)d,
                                     (uint8_t)pc});
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

    // 多线程：N 路独立 BF 竞速（无共享锁，吃满多核）
    Result solveBF(int timeLimitMs, int Wweight, int nthreads = 0) {
        if (nthreads <= 0) {
            nthreads = (int)std::thread::hardware_concurrency();
            if (nthreads <= 0) nthreads = 8;
        }
        // 竞速：尽量吃满多核（留 1 核给系统），内存用较小哈希表控制
        int hc = nthreads;
        nthreads = std::max(2, hc > 2 ? hc - 1 : hc);
        if (nthreads > 16) nthreads = 16;
        if (nthreads == 1) {
            int ord[4] = {0, 1, 2, 3};
            return solveBF_ST(timeLimitMs, Wweight, ord, nullptr, 0);
        }

        std::cout << "  BF race threads=" << nthreads << " (of " << hc << " cpus) weight=" << Wweight << "\n";
        std::cout.flush();

        std::atomic<bool> stop{false};
        std::vector<Result> results(nthreads);
        std::vector<std::thread> threads;
        threads.reserve(nthreads);

        // 不同线程不同方向顺序 + 略微不同权重
        static const int perms[][4] = {
            {0, 1, 2, 3}, {0, 1, 3, 2}, {0, 2, 1, 3}, {0, 2, 3, 1},
            {0, 3, 1, 2}, {0, 3, 2, 1}, {1, 0, 2, 3}, {1, 0, 3, 2},
            {1, 2, 0, 3}, {1, 2, 3, 0}, {1, 3, 0, 2}, {1, 3, 2, 0},
            {2, 0, 1, 3}, {2, 0, 3, 1}, {2, 1, 0, 3}, {2, 1, 3, 0},
            {2, 3, 0, 1}, {2, 3, 1, 0}, {3, 0, 1, 2}, {3, 0, 2, 1},
            {3, 1, 0, 2}, {3, 1, 2, 0}, {3, 2, 0, 1}, {3, 2, 1, 0},
        };
        const int nperm = 24;

        auto T0 = Clock::now();
        for (int t = 0; t < nthreads; t++) {
            threads.emplace_back([&, t]() {
                int ord[4];
                for (int i = 0; i < 4; i++) ord[i] = perms[t % nperm][i];
                // 部分线程用 wastar 变体，扩大覆盖
                int w = Wweight;
                if (Wweight == 0 && (t % 4) == 1) w = 2;
                if (Wweight == 0 && (t % 4) == 2) w = 3;
                if (Wweight == 0 && (t % 4) == 3) w = 5;
                results[t] = solveBF_ST(timeLimitMs, w, ord, &stop, t);
                if (results[t].ok) stop.store(true, std::memory_order_relaxed);
            });
        }
        for (auto& th : threads) th.join();

        Result best;
        best.ms = (int)std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
        for (int t = 0; t < nthreads; t++) {
            best.nodes += results[t].nodes;
            best.expansions += results[t].expansions;
            if (results[t].ok) {
                if (!best.ok || results[t].pushes < best.pushes) {
                    best.ok = true;
                    best.path = std::move(results[t].path);
                    best.playerPath = std::move(results[t].playerPath);
                    best.pushes = results[t].pushes;
                    best.dir = results[t].dir + "-race" + std::to_string(t);
                    best.visited = results[t].visited;
                }
            }
        }
        if (!best.ok) best.visited = results[0].visited;
        return best;
    }

    Result solveDFS(int timeLimitMs, int maxExpansions = 5000000) {
        Result res;
        res.dir = "dfs";
        auto T0 = Clock::now();
        defaultReach.ensure(N);
        if (maxExpansions <= 0) maxExpansions = 5000000;

        int h0 = heuristic(startMask);
        if (h0 >= 999999) return res;

        VisMap visited;
        visited.clear(1 << 20);
        std::vector<Node> nodes;
        nodes.reserve(1 << 20);

        struct Frame {
            int ni;
            int nextChild;
            std::vector<int> children;
        };

        auto genChildren = [&](int ci) -> std::vector<int> {
            const Node cur = nodes[ci];
            computeReach(cur.player, cur.mask);
            struct Cand {
                BitMask nm;
                int fPl, nh, pc, d, minR, boxFrom;
            };
            std::vector<Cand> cands;
            cands.reserve(NB * 4);

            auto it = cur.mask.iter();
            for (int b; (b = it.next()) >= 0;) {
                int base = b << 2;
                for (int d = 0; d < 4; d++) {
                    int to = pushTo[base + d];
                    if (to < 0 || cur.mask.test(to)) continue;
                    int from = pushFrom[base + d];
                    if (!canReach(from) || dead[to]) continue;

                    BitMask nm = cur.mask;
                    nm.flip(b);
                    nm.flip(to);
                    int fTo = to, fPl = b, pc = 1;
                    int nh = cur.h + hDelta(b, to);
                    while (degree[fTo] == 2 && !isGoal[fTo]) {
                        int nx = pushTo[(fTo << 2) + d];
                        if (nx < 0 || nm.test(nx) || dead[nx]) break;
                        nh += hDelta(fTo, nx);
                        nm.flip(fTo);
                        nm.flip(nx);
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
            std::sort(cands.begin(), cands.end(),
                      [](const Cand& a, const Cand& b) { return a.nh < b.nh; });

            std::vector<int> childIdx;
            for (auto& c : cands) {
                int ng = cur.g + c.pc;
                if (!visited.tryInsert(c.nm, (uint16_t)c.minR, ng)) continue;
                int ni = (int)nodes.size();
                nodes.push_back({c.nm, ci, (int16_t)c.fPl, (int16_t)ng, (int16_t)c.nh, (int16_t)c.boxFrom,
                                 (uint8_t)c.d, (uint8_t)c.pc});
                childIdx.push_back(ni);
            }
            return childIdx;
        };

        int min0 = computeReach(startPlayer, startMask);
        nodes.push_back({startMask, -1, (int16_t)startPlayer, 0, (int16_t)h0, (int16_t)-1, 0, 0});
        visited.tryInsert(startMask, (uint16_t)min0, 0);

        std::vector<Frame> stack;
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
                if (expansions >= maxExpansions || (int)nodes.size() > 8000000) {
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
            if ((int)stack.size() > 400) continue;
            stack.push_back({child, 0, genChildren(child)});
        }
        res.ms = (int)std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
        res.nodes = nodeCount;
        res.expansions = expansions;
        res.visited = (int)visited.count;
        return res;
    }

    Result solve(int timeLimitMs, const std::string& mode) {
        int thr = (int)std::thread::hardware_concurrency();
        if (thr <= 0) thr = 8;

        if (mode == "dfs") return solveDFS(timeLimitMs);
        if (mode == "astar") return solveBF(timeLimitMs, 1, thr);
        if (mode == "wastar") return solveBF(timeLimitMs, 4, thr);
        if (mode == "bf" || mode == "greedy") return solveBF(timeLimitMs, 0, thr);

        // auto: 多线程 BF 直接跑（吃满多核）；可选先短 DFS
        if (timeLimitMs <= 0) {
            // 短 DFS 抢快解（单线程），失败再全核 BF
            auto r = solveDFS(0, 2000000);
            if (r.ok) {
                r.dir = "auto/dfs";
                return r;
            }
            std::cout << "  DFS exhausted (exp=" << r.expansions << "), multi-thread BF thr="
                      << thr << "...\n";
            std::cout.flush();
            auto r2 = solveBF(0, 0, thr);
            r2.nodes += r.nodes;
            r2.expansions += r.expansions;
            r2.dir = r2.ok ? "auto/bf-mt" : "auto";
            return r2;
        }
        auto T0 = Clock::now();
        int t1 = timeLimitMs * 2 / 5;
        auto r = solveDFS(t1, 2000000);
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
        auto r2 = solveBF(left, 0, thr);
        r2.nodes += r.nodes;
        r2.expansions += r.expansions;
        r2.ms = (int)std::chrono::duration_cast<ms_t>(Clock::now() - T0).count();
        r2.dir = r2.ok ? "auto/bf-mt" : "auto";
        return r2;
    }
};

// ===================== main =====================
int main(int argc, char** argv) {
    int levelId = -99999;
    int timeLimit = 0;
    std::string mode = "auto";
    bool doWrite = false;
    bool batch = false;

    for (int i = 1; i < argc; i++) {
        std::string a = argv[i];
        if (a == "--write") doWrite = true;
        else if (a == "--batch") batch = true;
        else if (a == "bf" || a == "dfs" || a == "auto" || a == "wastar" || a == "astar" || a == "greedy")
            mode = a;
        else if (!a.empty() && (a[0] == '-' || (a[0] >= '0' && a[0] <= '9'))) {
            int v = std::atoi(a.c_str());
            if (!batch && levelId == -99999) levelId = v;
            else timeLimit = v;
        }
    }
    if (batch) doWrite = true;

    std::string path = findLevelsJson();
    if (path.empty()) {
        std::cerr << "levels.json not found\n";
        return 1;
    }

    auto processOne = [&](int id, int& solved, int& failed, int& skipped) {
        std::string json = readFile(path);
        LevelData level;
        if (!loadLevelById(json, id, level)) {
            std::cout << "[skip] id=" << id << " not found\n";
            skipped++;
            return;
        }
        if (!level.solution.empty() && level.solution != "null") {
            std::cout << "[skip] id=" << id << " " << level.name << " already solved\n";
            skipped++;
            return;
        }

        std::cout << "\n========== id=" << level.id << " " << level.name << " ==========\n";
        for (auto& r : level.puzzle) std::cout << "  " << r << "\n";

        Solver solver;
        if (!solver.build(level.puzzle)) {
            std::cout << "BUILD FAIL N=" << solver.N << "\n";
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
        if (playerPath.empty()) {
            std::cout << "WARN: no player path, using pushes\n";
            playerPath = res.path;
        }
        std::cout << "SOLVED ms=" << res.ms << " pushes=" << res.pushes
                  << " nodes=" << res.nodes << " exp=" << res.expansions
                  << " dir=" << res.dir << " playerMoves=" << playerPath.size() << "\n";
        std::cout << "player: " << playerPath << "\n";
        if (doWrite) writeAllJsonCopies(path, id, playerPath);
        solved++;
        std::cout.flush();
    };

    if (batch) {
        std::string json = readFile(path);
        auto ids = listAllIds(json);
        struct Item {
            int id, boxes, floors;
            std::string name;
        };
        std::vector<Item> todo;
        for (int id : ids) {
            LevelData L;
            if (!loadLevelById(json, id, L)) continue;
            if (!L.solution.empty() && L.solution != "null") continue;
            int boxes = 0, floors = 0;
            int maxW = 0;
            for (auto& row : L.puzzle) maxW = std::max(maxW, (int)row.size());
            for (auto& row : L.puzzle) {
                std::string r = row;
                if ((int)r.size() < maxW) r.append(maxW - (int)r.size(), '#');
                for (char c : r) {
                    if (c != '#') floors++;
                    if (c == '$' || c == '*') boxes++;
                }
            }
            todo.push_back({id, boxes, floors, L.name});
        }
        std::sort(todo.begin(), todo.end(), [](const Item& a, const Item& b) {
            if (a.boxes != b.boxes) return a.boxes < b.boxes;
            if (a.floors != b.floors) return a.floors < b.floors;
            return a.id < b.id;
        });

        std::cout << "BATCH: " << todo.size() << " unsolved, mode=" << mode
                  << " time=" << (timeLimit <= 0 ? "unlimited" : std::to_string(timeLimit)) << "\n";
        int solved = 0, failed = 0, skipped = 0;
        auto batchT0 = Clock::now();
        for (size_t i = 0; i < todo.size(); i++) {
            std::cout << "\n>>> [" << (i + 1) << "/" << todo.size() << "] boxes=" << todo[i].boxes
                      << " floors=" << todo[i].floors << " id=" << todo[i].id << " " << todo[i].name
                      << "\n";
            processOne(todo[i].id, solved, failed, skipped);
            auto elapsed = std::chrono::duration_cast<ms_t>(Clock::now() - batchT0).count();
            std::cout << "--- progress solved=" << solved << " failed=" << failed
                      << " skipped=" << skipped << " elapsed=" << (elapsed / 1000.0) << "s ---\n";
            std::cout.flush();
        }
        std::cout << "\n========== BATCH DONE ==========\n";
        std::cout << "solved=" << solved << " failed=" << failed << " skipped=" << skipped << "\n";
        std::cout << "Run: node scripts/gen_levels_js.js\n";
        return failed ? 2 : 0;
    }

    if (levelId == -99999) {
        std::cerr << "Usage: sokosolve <id> [timeMs] [mode] [--write]\n"
                     "       sokosolve --batch [timeMs] [mode]\n";
        return 1;
    }
    int solved = 0, failed = 0, skipped = 0;
    processOne(levelId, solved, failed, skipped);
    if (doWrite) std::cout << "Run: node scripts/gen_levels_js.js\n";
    return failed ? 2 : 0;
}
