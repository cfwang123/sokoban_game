# erlangapp1 — Erlang Sokoban (teaching)

> [中文版](README.ZH.md)

[Erlang/OTP](https://www.erlang.org/)（`erlc` / `erl`）.

## Run

```bash
cd erlangapp1
erlc game.erl main.erl
erl -noshell -s main start -s init stop
```

Controls: WASD move, z undo, r reset, q quit.
