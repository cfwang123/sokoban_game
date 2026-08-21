# cmdapp1 — Windows CMD batch Sokoban (teaching)

> [中文版](README.ZH.md)

Pure **`cmd.exe` batch** — no extra runtime required.

## Run

```bat
cd cmdapp1
main.cmd
```

Or double-click `main.cmd` in Explorer.

Controls: WASD move, z undo, r reset, q quit (press Enter after each key).

## Implementation notes

- Map is a length-49 string (7×7), index `y*7+x`
- Internal encoding: `#` wall, `.` goal, `B` box, `*` box on goal, `-` floor (shown as space)
- Avoid unquoted `$`/`*` being treated as wildcards in batch

## Cross-reference

| Directory | Environment |
|-----------|-------------|
| `cmdapp1` (this dir) | Windows CMD / batch |
| [`../powershellapp1`](../powershellapp1) | PowerShell |
| [`../bashapp1`](../bashapp1) | Bash |
