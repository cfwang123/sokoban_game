# befungeapp1 — Befunge-93 playable Sokoban

> [中文版](README.ZH.md)

**Game logic is 100% Befunge-93** (`sokoban.bf`).  
`befunge93.py` / `main.py` are only the interpreter and launcher — **no** separate Python game.

## Level

```text
#####
#.$@#
#####
```

One box, one goal; push left to clear.

## Run

```bash
cd befungeapp1
python -X utf8 main.py
```

| Key | Action |
|-----|--------|
| `a` / `d` | left / right (can push) |
| `q` or EOF | quit |

Sample input (clear then quit):

```text
a
q
```

## Files

| File | Description |
|------|-------------|
| `sokoban.bf` | **pure Befunge-93 game source** |
| `befunge93.py` | Befunge-93 interpreter (auto-extends playfield width) |
| `main.py` | load and run `sokoban.bf` |
| `gen_sokoban.py` | maintenance: regenerate `sokoban.bf` |
| `README.md` | this document (English) |
| `README.ZH.md` | Chinese document |

Regenerate:

```bash
python -X utf8 gen_sokoban.py
```

## Implementation notes

- Map lives in Funge-Space (`g` / `p`).
- Main loop is a **single-line** program that wraps on **playfield width**; first run initializes coordinates via a flag.
- On `q`, write `@` at `(0,0)`; next wrap halts.
- Interpreter playfield width ≥ program line length (classic 80 columns is too narrow; still Befunge-93 semantics).

## Policy

Gameplay in the target language; host is interpreter only. See [docs/UNSUPPORTED_LANGS.md](../docs/UNSUPPORTED_LANGS.md).
