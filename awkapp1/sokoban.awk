# awkapp1 — AWK 推箱子终端版（教学）
# 运行: awk -f sokoban.awk
# 需要 gawk（多维数组 / 关联数组）

BEGIN {
    level[0] = "#######"
    level[1] = "#. . .#"
    level[2] = "# $$$ #"
    level[3] = "#.$@$.#"
    level[4] = "# $$$ #"
    level[5] = "#. . .#"
    level[6] = "#######"
    nlevel = 7
    init()
    print "sokoban_awk — wasd 移动, z 撤销, r 重置, q 退出"
    while (1) {
        print ""
        render()
        flag = (won ? " WIN!" : "")
        printf "moves=%d%s\n> ", moves, flag
        if ((getline line < "/dev/stdin") <= 0) break
        gsub(/^[ \t]+|[ \t]+$/, "", line)
        if (line == "") continue
        ch = tolower(substr(line, 1, 1))
        if (ch == "w") try_move(0, -1)
        else if (ch == "s") try_move(0, 1)
        else if (ch == "a") try_move(-1, 0)
        else if (ch == "d") try_move(1, 0)
        else if (ch == "z") undo()
        else if (ch == "r") init()
        else if (ch == "q") break
        if (won) print "Level clear!"
    }
}

function key(x, y) { return x SUBSEP y }

function init(   y, x, row, ch, k) {
    delete walls; delete goals; delete boxes; delete hist_px; delete hist_py
    delete hist_bfx; delete hist_bfy; delete hist_btx; delete hist_bty; delete hist_push
    moves = 0; won = 0; hist_n = 0; width = 0; height = nlevel
    px = 0; py = 0
    for (y = 0; y < nlevel; y++) {
        row = level[y]
        if (length(row) > width) width = length(row)
        for (x = 0; x < length(row); x++) {
            ch = substr(row, x + 1, 1)
            k = key(x, y)
            if (ch == "#") walls[k] = 1
            else if (ch == ".") goals[k] = 1
            else if (ch == "$") boxes[k] = 1
            else if (ch == "*") { boxes[k] = 1; goals[k] = 1 }
            else if (ch == "@") { px = x; py = y }
            else if (ch == "+") { px = x; py = y; goals[k] = 1 }
        }
    }
}

function check_win(   b) {
    for (b in boxes) if (!(b in goals)) { won = 0; return }
    won = 1
}

function try_move(dx, dy,   nx, ny, nk, bx, by, bk) {
    if (won) return 0
    nx = px + dx; ny = py + dy
    nk = key(nx, ny)
    if (nk in walls) return 0
    if (nk in boxes) {
        bx = nx + dx; by = ny + dy
        bk = key(bx, by)
        if ((bk in walls) || (bk in boxes)) return 0
        hist_n++
        hist_px[hist_n] = px; hist_py[hist_n] = py
        hist_bfx[hist_n] = nx; hist_bfy[hist_n] = ny
        hist_btx[hist_n] = bx; hist_bty[hist_n] = by
        hist_push[hist_n] = 1
        delete boxes[nk]
        boxes[bk] = 1
        px = nx; py = ny
        moves++
        check_win()
        return 1
    }
    hist_n++
    hist_px[hist_n] = px; hist_py[hist_n] = py
    hist_push[hist_n] = 0
    px = nx; py = ny
    return 1
}

function undo(   e) {
    if (won || hist_n == 0) return 0
    while (hist_n > 0) {
        e = hist_n
        hist_n--
        if (hist_push[e]) {
            px = hist_px[e]; py = hist_py[e]
            delete boxes[key(hist_btx[e], hist_bty[e])]
            boxes[key(hist_bfx[e], hist_bfy[e])] = 1
            if (moves > 0) moves--
            won = 0
            return 1
        }
        px = hist_px[e]; py = hist_py[e]
    }
    return 1
}

function render(   y, x, k, ch) {
    for (y = 0; y < height; y++) {
        for (x = 0; x < width; x++) {
            k = key(x, y)
            if (x == px && y == py) ch = ((k in goals) ? "+" : "@")
            else if (k in boxes) ch = ((k in goals) ? "*" : "$")
            else if (k in walls) ch = "#"
            else if (k in goals) ch = "."
            else ch = " "
            printf "%s", ch
        }
        print ""
    }
}
