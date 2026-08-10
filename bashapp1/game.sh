# 推箱子核心逻辑（Bash 教学）
# shellcheck shell=bash

game_key() { echo "$1,$2"; }

game_from_rows() {
  # sets globals: G_WALLS G_GOALS G_BOXES G_PX G_PY G_MOVES G_WON G_W G_H G_HIST
  declare -gA G_WALLS G_GOALS G_BOXES
  G_WALLS=(); G_GOALS=(); G_BOXES=()
  G_PX=0; G_PY=0; G_MOVES=0; G_WON=0
  G_W=0; G_H=0
  G_HIST=()
  local y=0 row x ch k maxx=0
  for row in "$@"; do
    for ((x=0; x<${#row}; x++)); do
      (( x > maxx )) && maxx=$x
      ch=${row:x:1}
      k=$(game_key "$x" "$y")
      case "$ch" in
        \#) G_WALLS[$k]=1 ;;
        .) G_GOALS[$k]=1 ;;
        \$) G_BOXES[$k]=1 ;;
        \*) G_BOXES[$k]=1; G_GOALS[$k]=1 ;;
        @) G_PX=$x; G_PY=$y ;;
        +) G_PX=$x; G_PY=$y; G_GOALS[$k]=1 ;;
      esac
    done
    ((y++))
  done
  G_W=$((maxx + 1))
  G_H=$y
}

game_check_win() {
  local b
  for b in "${!G_BOXES[@]}"; do
    [[ -z ${G_GOALS[$b]+x} ]] && { G_WON=0; return; }
  done
  G_WON=1
}

game_try_move() {
  local dx=$1 dy=$2
  (( G_WON )) && return 1
  local nx=$((G_PX + dx)) ny=$((G_PY + dy))
  local nk bx by bk
  nk=$(game_key "$nx" "$ny")
  [[ -n ${G_WALLS[$nk]+x} ]] && return 1
  if [[ -n ${G_BOXES[$nk]+x} ]]; then
    bx=$((nx + dx)); by=$((ny + dy))
    bk=$(game_key "$bx" "$by")
    [[ -n ${G_WALLS[$bk]+x} || -n ${G_BOXES[$bk]+x} ]] && return 1
    G_HIST+=("$G_PX $G_PY $nk $bk")
    unset "G_BOXES[$nk]"
    G_BOXES[$bk]=1
    G_PX=$nx; G_PY=$ny
    ((G_MOVES++))
    game_check_win
    return 0
  fi
  G_HIST+=("$G_PX $G_PY - -")
  G_PX=$nx; G_PY=$ny
  return 0
}

game_undo() {
  (( G_WON || ${#G_HIST[@]} == 0 )) && return 1
  local entry hx hy bf bt
  while (( ${#G_HIST[@]} > 0 )); do
    entry=${G_HIST[-1]}
    unset 'G_HIST[-1]'
    read -r hx hy bf bt <<<"$entry"
    if [[ $bf != - ]]; then
      G_PX=$hx; G_PY=$hy
      unset "G_BOXES[$bt]"
      G_BOXES[$bf]=1
      (( G_MOVES > 0 )) && ((G_MOVES--))
      G_WON=0
      return 0
    fi
    G_PX=$hx; G_PY=$hy
  done
  return 0
}

game_render() {
  local y x k
  for ((y=0; y<G_H; y++)); do
    for ((x=0; x<G_W; x++)); do
      k=$(game_key "$x" "$y")
      if (( x == G_PX && y == G_PY )); then
        [[ -n ${G_GOALS[$k]+x} ]] && printf '+' || printf '@'
      elif [[ -n ${G_BOXES[$k]+x} ]]; then
        [[ -n ${G_GOALS[$k]+x} ]] && printf '*' || printf '$'
      elif [[ -n ${G_WALLS[$k]+x} ]]; then
        printf '#'
      elif [[ -n ${G_GOALS[$k]+x} ]]; then
        printf '.'
      else
        printf ' '
      fi
    done
    printf '\n'
  done
}
