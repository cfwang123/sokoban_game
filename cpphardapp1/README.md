# cpphardapp1 — Intentionally unreadable C++ Sokoban

> [中文版](README.ZH.md)

Same mini Sokoban as other CLI ports, implemented with a **dense pile of hard-to-read C++** (macros, token-paste names, CRTP, member-function pointers, `std::variant` + overload sets, comma-operator chains, nested ternaries, `bitset` direction encoding, …).

This is a teaching **anti-example / syntax showcase**, not a style guide. Prefer `cppapp1/` (readable C++17) or `cpp26app1/` (C++03–C++26 museum).

## Build / run

```bash
cd cpphardapp1
g++ -std=c++17 -O2 main.cpp -o sokoban
./sokoban
```

Controls: WASD move, `z` undo, `r` reset, `q` quit.

## Files

| File | Role |
|------|------|
| `game.hpp` | Obfuscated core (`_::Game`, macros, templates) |
| `main.cpp` | Obfuscated input loop (`variant` / `Ov` / pipe) |
