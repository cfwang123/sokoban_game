# cpp26app1 — Sokoban as a C++03…C++26 syntax museum (playable)

> [中文版](README.ZH.md)

Same mini Sokoban CLI as `cppapp1/`, rewritten to **exercise representative syntax & library features from C++03 through C++26** (compiled as **`-std=c++26`**). Contrast with readable C++17 `cppapp1/` and the obfuscated `cpphardapp1/`.

## Build / run

Needs GCC 15+ / a toolchain with solid C++26 support. On **MinGW**, link `libstdc++exp` for `<print>`:

```bash
cd cpp26app1
g++ -std=c++26 -O2 main.cpp -o sokoban -lstdc++exp
./sokoban
```

Controls: WASD move, `z` undo, `r` reset, `q` quit.

## Files

| File | Role |
|------|------|
| `game.hpp` | Core logic + language/library showcase |
| `main.cpp` | Terminal loop, `#embed`, `print`, command `variant` |
| `level.min.txt` | Mini level **embedded** via C++26 `#embed` |

## Feature map (by standard)

| Era | Used here (non-exhaustive) |
|-----|----------------------------|
| **C++03/98** | templates, namespaces, STL (`vector`/`algorithm`/`string`), `switch`, references |
| **C++11** | `auto`, `nullptr`, `constexpr`, range-for, lambdas, `enum class`, alias templates, `=default`/`=delete`, NSDMI, move, `chrono`, `tuple`, UDL (`_cmd`), inheriting-style CRTP helper, `override`-ready design |
| **C++14** | generic/relaxed constexpr lambdas, chrono UDLs (`ms`), variable templates |
| **C++17** | `string_view`, `optional`, `variant`, structured bindings, `if constexpr`, fold expressions, nested namespace, `[[nodiscard]]`, CTAD (`tuple{…}`), `std::size_t` utilities |
| **C++20** | concepts (`LevelRows`), ranges/views, `span`, `<=>`, `using enum`, designated init, `format`, `source_location`, `bit` header available, coroutines (via `generator`) |
| **C++23** | `print`/`println`, `expected`, `flat_set`, `generator`, deducing `this`, multidimensional `operator[]`, `static operator()`, `auto(x)`, `zu` suffix, `ranges` algorithms |
| **C++26** | `#embed`, pack indexing `Ts...[N]` / `xs...[N]`, placeholder `_`, `= delete("reason")`, attributes on structured bindings, structured binding as `if` condition, `variant::visit` member |

Not every paper in each standard is used (modules / reflection / contracts need wider toolchain support); the set above is what this demo **actually compiles and runs** under GCC 15 `-std=c++26`.
