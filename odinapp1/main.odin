// odinapp1 — Odin 推箱子终端版（教学）
// 编译: odin build . -out:sokoban
package main

import "core:fmt"
import "core:os"
import "core:strings"
import "core:unicode"
import "core:unicode/utf8"

LEVEL :: [7]string{
	"#######",
	"#. . .#",
	"# $$$ #",
	"#.$@$.#",
	"# $$$ #",
	"#. . .#",
	"#######",
}

main :: proc() {
	state := from_rows(LEVEL[:])
	fmt.println("sokoban_odin — wasd 移动, z 撤销, r 重置, q 退出")
	for {
		fmt.println()
		fmt.print(render_ascii(state))
		flag := " WIN!" if state.won else ""
		fmt.printf("moves=%d%s\n> ", state.moves, flag)
		buf: [256]byte
		n, _ := os.read(os.stdin, buf[:])
		if n <= 0 do break
		line := strings.trim_space(string(buf[:n]))
		if len(line) == 0 do continue
		r, _ := utf8.decode_rune_in_string(line)
		ch := unicode.to_lower(r)
		switch ch {
		case 'w': try_move(&state, 0, -1)
		case 's': try_move(&state, 0, 1)
		case 'a': try_move(&state, -1, 0)
		case 'd': try_move(&state, 1, 0)
		case 'z': undo(&state)
		case 'r': state = from_rows(LEVEL[:])
		case 'q': return
		}
		if state.won do fmt.println("Level clear!")
	}
}
