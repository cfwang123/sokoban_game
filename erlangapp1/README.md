# erlangapp1 — Erlang 推箱子（教学）

需要 [Erlang/OTP](https://www.erlang.org/)（`erlc` / `erl`）。

```bash
cd erlangapp1
erlc game.erl main.erl
erl -noshell -s main start -s init stop
```

键位：WASD 移动，z 撤销，r 重置，q 退出。
