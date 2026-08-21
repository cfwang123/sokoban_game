// cpp26app1 — C++03~C++26 语法展柜推箱子（可玩）
// 编译: g++ -std=c++26 -O2 main.cpp -o sokoban -lstdc++exp
#include "game.hpp"

#include <cctype>
#include <iostream>
#include <print>       // C++23
#include <span>        // C++20
#include <string>
#include <string_view>
#include <tuple>
#include <utility>
#include <vector>

namespace {

using sokoban::cxx26::Command;
using sokoban::cxx26::Dir;
using sokoban::cxx26::GameState;
using sokoban::cxx26::MoveErr;
using sokoban::cxx26::any_true;
using sokoban::cxx26::dir_at;
using sokoban::cxx26::sizeof_pack_head;

// C++26 #embed — 把关卡文件嵌进二进制
constexpr char kLevelBlob[] = {
#embed "level.min.txt"
    , '\0'};

// C++11 user-defined literal（教学用，把字符标成“命令字面量”）
constexpr char operator""_cmd(char c) noexcept { return c; }

// C++11 lambda / C++14 generic lambda / C++20 templated lambda 痕迹
constexpr auto lower = [](unsigned char u) constexpr -> char {
    return static_cast<char>(u >= 'A' && u <= 'Z' ? u - 'A' + 'a' : u);
};

[[nodiscard]] Command parse_command(char ch) {
    // C++17 if-init + C++20 designated-ish via returns
    switch (ch) {
    case 'w': return Dir::Up;
    case 's': return Dir::Down;
    case 'a': return Dir::Left;
    case 'd': return Dir::Right;
    case 'z'_cmd:
    case 'r'_cmd:
    case 'q'_cmd: return ch;
    default: return std::monostate{};
    }
}

[[nodiscard]] const char* move_err_msg(MoveErr e) {
    switch (e) {
    case MoveErr::AlreadyWon: return "already won";
    case MoveErr::HitWall: return "hit wall";
    case MoveErr::BlockedBox: return "blocked box";
    }
    return "unknown";
}

}  // namespace

int main() {
    // C++17 inline-ish static assert message; C++26 enhanced static_assert messages OK as string
    static_assert(sizeof_pack_head<int, char, double>() == sizeof(int),
                  "pack indexing head should be int");
    static_assert(dir_at<0>() == Dir::Up);
    static_assert(any_true(false, false, true));

    using sokoban::cxx26::i64;

    // C++26 placeholder _ （可重复的无名占位）
    auto demo_tuple = std::tuple{1, 2, 3};
    auto [_, keep, _] = demo_tuple;
    (void)keep;

    // C++26 结构化绑定旁属性
    auto demo2 = std::tuple{4, 5, 6};
    auto [a [[maybe_unused]], mid, c [[maybe_unused]]] = demo2;
    (void)mid;

    // C++26 结构化绑定作条件
    if (auto [ok, val] = std::pair{true, 42}; ok) {
        (void)val;
    }

    // C++23 auto(x) decay-copy 痕迹
    std::string_view title = "sokoban_cpp26";
    auto title_owned = auto(std::string{title});

    auto state = GameState::from_embedded(std::string_view{kLevelBlob});

    // C++20 source_location
    const auto loc = std::source_location::current();
    std::println("{} (C++{}) — wasd/z/r/q  |  built from {}:{}",
                 title_owned,
                 __cplusplus,
                 loc.file_name(),
                 loc.line());
    std::println("embed_bytes={}  pack_head_sizeof={}",
                 std::span{kLevelBlob}.size() - 1zu,  // C++23 zu suffix
                 sizeof_pack_head<i64, int>());

    while (true) {
        std::println("\n{}", state.render_ascii());
        std::println("{}", state.status_line());
        std::print("> ");

        std::string line;
        if (!std::getline(std::cin, line)) {
            break;
        }
        if (line.empty()) {
            continue;
        }

        const char ch = lower(static_cast<unsigned char>(line.front()));
        Command cmd = parse_command(ch);

        // C++26: variant 成员 visit；C++17 visit 的现代写法
        const bool quit = cmd.visit([&](auto&& c) -> bool {
            using T = std::decay_t<decltype(c)>;
            if constexpr (std::is_same_v<T, Dir>) {  // C++17 if constexpr
                if (auto r = state.try_move(c); !r) {
                    // C++26 structured binding as condition
                    if (auto err = r.error(); any_true(err == MoveErr::HitWall,
                                                       err == MoveErr::BlockedBox,
                                                       err == MoveErr::AlreadyWon)) {
                        (void)err;  // 静默失败即可；消息能力已展示
                    }
                }
                return false;
            } else if constexpr (std::is_same_v<T, char>) {
                if (c == 'z') {
                    (void)state.undo();
                } else if (c == 'r') {
                    state = GameState::from_embedded(std::string_view{kLevelBlob});
                } else if (c == 'q') {
                    return true;
                }
                return false;
            } else {
                (void)c;
                return false;
            }
        });

        if (quit) {
            break;
        }
        if (state.won) {
            std::println("Level clear!");
        }
    }

    // 避免未使用告警：展柜符号引用
    (void)move_err_msg(MoveErr::HitWall);
    (void)sokoban::cxx26::DemoGrid{};
    return 0;
}
