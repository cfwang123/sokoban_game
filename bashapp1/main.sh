#!/usr/bin/env bash
# bashapp1 — Bash 推箱子终端版（教学）
set -euo pipefail
DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=game.sh
source "$DIR/game.sh"

LEVEL=(
  '#######'
  '#. . .#'
  '# $$$ #'
  '#.$@$.#'
  '# $$$ #'
  '#. . .#'
  '#######'
)

game_from_rows "${LEVEL[@]}"
echo "sokoban_bash — wasd 移动, z 撤销, r 重置, q 退出"

while true; do
  echo
  game_render
  flag=""; (( G_WON )) && flag=" WIN!"
  echo "moves=${G_MOVES}${flag}"
  printf '> '
  if ! IFS= read -r line; then break; fi
  line=${line//[[:space:]]/}
  [[ -z $line ]] && continue
  ch=${line:0:1}
  ch=${ch,,}
  case $ch in
    w) game_try_move 0 -1 || true ;;
    s) game_try_move 0 1 || true ;;
    a) game_try_move -1 0 || true ;;
    d) game_try_move 1 0 || true ;;
    z) game_undo || true ;;
    r) game_from_rows "${LEVEL[@]}" ;;
    q) break ;;
  esac
  (( G_WON )) && echo "Level clear!"
done
