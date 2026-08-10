// vapp1 — V 推箱子终端版（教学）
// 运行: v run .
module main

import os

const level = [
	'#######',
	'#. . .#',
	'# $$$ #',
	'#.$@$.#',
	'# $$$ #',
	'#. . .#',
	'#######',
]

fn main() {
	mut state := from_rows(level)
	println('sokoban_v — wasd 移动, z 撤销, r 重置, q 退出')
	for {
		println('')
		print(state.render_ascii())
		flag := if state.won { ' WIN!' } else { '' }
		print('moves=${state.moves}${flag}\n> ')
		line := os.input('')
		t := line.trim_space()
		if t.len == 0 {
			continue
		}
		ch := t[0].ascii_str().to_lower()
		match ch {
			'w' { state.try_move(0, -1) }
			's' { state.try_move(0, 1) }
			'a' { state.try_move(-1, 0) }
			'd' { state.try_move(1, 0) }
			'z' { state.undo() }
			'r' { state = from_rows(level) }
			'q' { break }
			else {}
		}
		if state.won {
			println('Level clear!')
		}
	}
}
