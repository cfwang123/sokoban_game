# parenthesishellapp1 — Parenthesis Hell Sokoban

> [中文版](readme.zh.md)

[Parenthesis Hell](https://esolangs.org/wiki/Parenthesis_Hell): a Lisp-like esolang where **code and data are only nested parentheses** `()`.  
This folder provides a **Python interpreter** plus a playable mini level.

## Run

```bash
cd parenthesishellapp1
python -X utf8 main.py
python -X utf8 main.py --test
```

Controls: WASD move, `z` undo, `r` reset, `q` quit.

## Files

| File | Description |
|------|-------------|
| `ph.py` | **Parenthesis Hell interpreter** (parse / eval / ASCII codec) |
| `hello.ph` | pure `()` Hello world (wiki example) |
| `sokoban.ph` | pure `()` program (default identity: return input) |
| `main.py` | interactive host; board state as PH `Cons`/`Nil` trees |
| `generate.py` | rewrite default `sokoban.ph` |
| `readme.md` | this document (English) |
| `readme.zh.md` | Chinese document |

## Language notes

| Form | Meaning |
|------|---------|
| `()` | as expr: current input; as function name: quote |
| `(())` | letrec |
| `((()))` | car |
| `(()())` | cdr |
| `((())())` | cons |
| `(()()())` | if |
| `(((())))` | eval |

A program is a **single expression** over the input value. No streaming `getchar`; the host owns the interactive loop.

ASCII strings are bit-encoded into paren trees (same idea as [qpliu/esolang](https://github.com/qpliu/esolang)). Verify `hello.ph`:

```bash
python -X utf8 -c "from ph import run_source; from pathlib import Path; print(repr(run_source(Path('hello.ph').read_text(encoding='utf-8'))))"
```

## Boundary vs pure PH whole-game

Parenthesis Hell fits pure transforms, not a self-contained interactive loop. This port:

- **State** = valid PH value (`Cons`/`Nil`, printable via `value_to_source`);
- After **each step**, state is fed into `sokoban.ph` (default identity `()` / cat);
- **Push rules** run on the host over PH structure (interpreter = language, host = session);
- Pure PH samples: `hello.ph`, quote/cat checks (`--test`).

A hand-written pure-PH `try_move` would be huge; the interpreter/value model are in place for further generation.
