# jsfuckapp1 — pure JSFuck playable Sokoban

> [中文版](readme.zh.md)

[JSFuck](https://jsfuck.com/): valid JavaScript using only **`[]()!+`**.  
The **whole game** is encoded as pure JSFuck; `main.py` / `play.html` only launch.

## Check (playable)

```bash
cd jsfuckapp1
node generate.js --check   # re-encode + one-push smoke test
python -X utf8 main.py --test
python -X utf8 main.py     # or: node sokoban.jsfuck.js
```

Controls: WASD move, `z` undo, `r` reset, `q` quit.

Browser: open `play.html` (loads `sokoban.browser.jsfuck.js`).

## Files

| File | Description |
|------|-------------|
| **`sokoban.jsfuck.js`** | pure JSFuck terminal game (Node) |
| **`sokoban.browser.jsfuck.js`** | pure JSFuck browser game |
| `game_src.js` | readable Node source (maintenance) |
| `game_src_browser.js` | readable browser source (maintenance) |
| `jsfuck_lib.js` | encoder |
| `generate.js` | generate pure JSFuck from readable sources |
| `main.py` | launcher / `--test` / `--rebuild` |
| `readme.md` | this document (English) |
| `readme.zh.md` | Chinese document |

## Generate

```bash
node generate.js --check
# or
python -X utf8 main.py --rebuild
```

## Notes

- Readable sources must not use `require` (JSFuck `eval` has no `require`); Node uses `process.stdin`.
- Standard 7×7 mini level (includes `# $$$ #`).
- Purity: output is only `[]()!+` (plus whitespace, which may be ignored on load).
