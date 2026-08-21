# powershellapp1 — PowerShell Sokoban (teaching)

> [中文版](README.ZH.md)

Pure **PowerShell** scripts (Windows PowerShell 5.1+ or PowerShell 7 `pwsh`).

## Run

```powershell
cd powershellapp1
# PowerShell 7
pwsh -NoProfile -File main.ps1
# Windows PowerShell (if execution policy blocks)
powershell -NoProfile -ExecutionPolicy Bypass -File main.ps1
```

Controls: WASD move, z undo, r reset, q quit.

## Files

| File | Description |
|------|-------------|
| `Game.ps1` | core logic |
| `main.ps1` | main loop |
| `README.md` | this document (English) |
| `README.ZH.md` | Chinese document |

## Cross-reference

| Directory | Environment |
|-----------|-------------|
| [`../cmdapp1`](../cmdapp1) | Windows CMD / batch |
| `powershellapp1` (this dir) | PowerShell |
| [`../bashapp1`](../bashapp1) | Bash |
