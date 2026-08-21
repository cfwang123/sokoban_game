// cpp26app1 — 推箱子核心：C++03~C++26 语法展柜（可玩教学）
#pragma once

// —— C++03/98 STL ——
#include <algorithm>
#include <exception>
#include <map>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// —— C++11 ——
#include <chrono>
#include <cstdint>
#include <functional>
#include <memory>
#include <tuple>
#include <type_traits>
#include <unordered_set>

// —— C++14 ——
// (exchange / make_unique 等在头中已间接可用)

// —— C++17 ——
#include <cstddef>
#include <optional>
#include <string_view>
#include <variant>

// —— C++20 ——
#include <bit>
#include <concepts>
#include <ranges>
#include <span>
#include <source_location>

// —— C++23 ——
#include <expected>
#include <flat_set>
#include <format>
#include <generator>

// —— C++26 相关（语言特性；库头按可用性） ——
#include <version>

namespace sokoban::cxx26 {

// C++11: alias template / nullptr / constexpr / enum class
using i64 = std::int64_t;
using Clock = std::chrono::steady_clock;

[[nodiscard]] constexpr i64 pack(int x, int y) noexcept {
    return (static_cast<i64>(x) << 32) | static_cast<std::uint32_t>(y);
}
[[nodiscard]] constexpr int unpack_x(i64 k) noexcept { return static_cast<int>(k >> 32); }
[[nodiscard]] constexpr int unpack_y(i64 k) noexcept {
    return static_cast<int>(static_cast<std::uint32_t>(k));
}

// C++11 enum class + C++20 using enum
enum class Dir : int { Up, Down, Left, Right };
enum class MoveErr : std::uint8_t { AlreadyWon, HitWall, BlockedBox };

[[nodiscard]] constexpr std::pair<int, int> delta(Dir d) noexcept {
    using enum Dir;  // C++20
    switch (d) {
    case Up: return {0, -1};
    case Down: return {0, 1};
    case Left: return {-1, 0};
    case Right: return {1, 0};
    }
    return {0, 0};
}

// C++20 concepts
template <typename R>
concept LevelRows = std::ranges::input_range<R>
    && std::convertible_to<std::ranges::range_reference_t<R>, std::string_view>;

// C++14 variable template + C++11 type_traits
template <typename T>
inline constexpr bool is_byte_like_v =
    std::is_same_v<T, char> || std::is_same_v<T, unsigned char> || std::is_same_v<T, std::byte>;

// C++26 pack indexing helper
template <typename... Ts>
[[nodiscard]] constexpr std::size_t sizeof_pack_head() noexcept {
    static_assert(sizeof...(Ts) > 0);
    return sizeof(Ts...[0]);
}

// C++11: =default / =delete ；C++26: =delete("reason")
struct NonCopyable {
    NonCopyable() = default;
    NonCopyable(const NonCopyable&) = delete("GameState snapshots should be moved, not copied lightly");
    NonCopyable& operator=(const NonCopyable&) = delete("GameState snapshots should be moved, not copied lightly");
    NonCopyable(NonCopyable&&) noexcept = default;
    NonCopyable& operator=(NonCopyable&&) noexcept = default;
};

// C++17: structured-friendly aggregate + optional
struct Hist {
    int px{};
    int py{};
    std::optional<i64> box_from{};
    std::optional<i64> box_to{};
    bool is_push = false;  // C++11 NSDMI
};

// C++23: static operator()
struct KeyHash {
    static std::size_t operator()(i64 k) noexcept {
        return std::hash<i64>{}(k);
    }
};

// C++20 three-way for Coord-like key wrapper
struct Key {
    i64 v{};
    constexpr Key() = default;
    constexpr explicit Key(i64 x) : v(x) {}
    constexpr Key(int x, int y) : v(pack(x, y)) {}
    constexpr operator i64() const noexcept { return v; }
    // C++20 <=>
    friend constexpr auto operator<=>(const Key&, const Key&) = default;
};

// C++23 multidimensional subscript — 只作语法展柜（小演示网格）
struct DemoGrid {
    int cells[2][2]{};
    int& operator[](std::size_t r, std::size_t c) { return cells[r][c]; }
    const int& operator[](std::size_t r, std::size_t c) const { return cells[r][c]; }
};

// C++11 inheriting / delegating constructors 轻量 CRTP 痕迹
template <typename D>
struct Fluent {
    D& self() { return *static_cast<D*>(this); }
    const D& self() const { return *static_cast<const D*>(this); }
};

struct GameState : Fluent<GameState>, NonCopyable {
    // C++23 flat_set；亦保留 unordered 作对照痕迹
    std::flat_set<i64> walls;
    std::flat_set<i64> goals;
    std::flat_set<i64> boxes;
    int px = 0, py = 0;
    int moves = 0;
    bool won = false;
    int width = 0, height = 0;
    std::vector<Hist> hist;
    Clock::time_point started = Clock::now();  // C++11 chrono

    // C++11: static factory；C++20 concepts on rows
    [[nodiscard]] static GameState from_rows(LevelRows auto&& rows, int /*index*/ = 0) {
        GameState s;
        int max_x = 0, max_y = 0;
        int y = 0;
        for (std::string_view row : rows) {  // C++11 range-for + C++17 string_view
            max_y = y;
            for (int x = 0; x < static_cast<int>(row.size()); ++x) {
                max_x = std::max(max_x, x);  // C++11 std::max
                const i64 k = pack(x, y);
                // C++17 if-init 风格拆解；此处用 switch（C++03 起）
                switch (row[static_cast<std::size_t>(x)]) {
                case '#': s.walls.insert(k); break;
                case '.': s.goals.insert(k); break;
                case '$': s.boxes.insert(k); break;
                case '*':
                    s.boxes.insert(k);
                    s.goals.insert(k);
                    break;
                case '@':
                    s.px = x;
                    s.py = y;
                    break;
                case '+':
                    s.px = x;
                    s.py = y;
                    s.goals.insert(k);
                    break;
                default: break;
                }
            }
            ++y;
        }
        s.width = max_x + 1;
        s.height = max_y + 1;
        s.started = Clock::now();
        return s;
    }

    // 从 #embed 进来的原始字节解析（C++17 string_view + C++20 ranges）
    [[nodiscard]] static GameState from_embedded(std::string_view blob) {
        namespace rv = std::ranges;
        namespace vw = std::views;
        auto lines = blob | vw::split('\n') | vw::transform([](auto&& sub) {
            std::string_view sv{&*sub.begin(), static_cast<std::size_t>(rv::distance(sub))};
            if (!sv.empty() && sv.back() == '\r') {
                sv.remove_suffix(1);
            }
            return sv;
        }) | vw::filter([](std::string_view sv) { return !sv.empty(); });
        return from_rows(lines);
    }

    void check_win(this GameState& self) {  // C++23 deducing this
        self.won = std::ranges::all_of(self.boxes, [&](i64 b) { return self.goals.contains(b); });
    }

    [[nodiscard]] auto try_move(this GameState& self, int dx, int dy)
        -> std::expected<void, MoveErr> {  // C++23 expected
        if (self.won) {
            return std::unexpected(MoveErr::AlreadyWon);
        }
        const int nx = self.px + dx;
        const int ny = self.py + dy;
        const i64 nk = pack(nx, ny);
        if (self.walls.contains(nk)) {
            return std::unexpected(MoveErr::HitWall);
        }
        if (self.boxes.contains(nk)) {
            const i64 bk = pack(nx + dx, ny + dy);
            if (self.walls.contains(bk) || self.boxes.contains(bk)) {
                return std::unexpected(MoveErr::BlockedBox);
            }
            // C++20 designated initializers
            self.hist.push_back(Hist{
                .px = self.px,
                .py = self.py,
                .box_from = nk,
                .box_to = bk,
                .is_push = true,
            });
            self.boxes.erase(nk);
            self.boxes.insert(bk);
            self.px = nx;
            self.py = ny;
            ++self.moves;
            self.check_win();
            return {};
        }
        self.hist.push_back(Hist{.px = self.px, .py = self.py});
        self.px = nx;
        self.py = ny;
        return {};
    }

    [[nodiscard]] auto try_move(this GameState& self, Dir d) -> std::expected<void, MoveErr> {
        const auto [dx, dy] = delta(d);  // C++17 structured binding
        return self.try_move(dx, dy);
    }

    bool undo(this GameState& self) {
        if (self.won || self.hist.empty()) {
            return false;
        }
        while (!self.hist.empty()) {
            // C++11 move
            Hist e = std::move(self.hist.back());
            self.hist.pop_back();
            if (e.is_push) {
                self.px = e.px;
                self.py = e.py;
                self.boxes.erase(*e.box_to);
                self.boxes.insert(*e.box_from);
                if (self.moves > 0) {
                    --self.moves;
                }
                self.won = false;
                return true;
            }
            self.px = e.px;
            self.py = e.py;
        }
        return true;
    }

    // C++23 std::generator（协程）
    [[nodiscard]] std::generator<std::string> render_lines(this GameState const& self) {
        for (int y = 0; y < self.height; ++y) {
            std::string line;
            line.reserve(static_cast<std::size_t>(self.width));
            for (int x = 0; x < self.width; ++x) {
                const i64 k = pack(x, y);
                if (self.px == x && self.py == y) {
                    line += self.goals.contains(k) ? '+' : '@';
                } else if (self.boxes.contains(k)) {
                    line += self.goals.contains(k) ? '*' : '$';
                } else if (self.walls.contains(k)) {
                    line += '#';
                } else if (self.goals.contains(k)) {
                    line += '.';
                } else {
                    line += ' ';
                }
            }
            co_yield line;
        }
    }

    [[nodiscard]] std::string render_ascii(this GameState const& self) {
        std::string out;
        for (std::string line : self.render_lines()) {
            out += line;
            out += '\n';
        }
        return out;
    }

    [[nodiscard]] std::string status_line(this GameState const& self) {
        using namespace std::chrono_literals;  // C++14 UDL
        const auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            Clock::now() - self.started);
        // C++20/23 format
        return std::format("moves={}{}  t={}ms", self.moves, self.won ? " WIN!" : "", ms.count());
    }
};

// C++17 fold expression 展柜
template <typename... Flags>
[[nodiscard]] constexpr bool any_true(Flags... fs) noexcept {
    return (false || ... || static_cast<bool>(fs));
}

// C++11 variadic + C++26 pack index：取方向表第 N 项
template <std::size_t N>
[[nodiscard]] constexpr Dir dir_at() {
    // pack of Dir values indexed by N
    return []<typename... Ds>(Ds... ds) {
        return ds...[N];
    }(Dir::Up, Dir::Down, Dir::Left, Dir::Right);
}

// C++17 variant 命令；C++26 member visit
using Command = std::variant<std::monostate, Dir, char>;

}  // namespace sokoban::cxx26
