// 推箱子核心逻辑（Odin 教学）
package main

import "core:fmt"
import "core:strings"

Hist :: struct {
	px, py:           int,
	box_from, box_to: string,
	is_push:          bool,
}

Game_State :: struct {
	walls, goals, boxes: map[string]bool,
	px, py:              int,
	moves:               int,
	won:                 bool,
	width, height:       int,
	hist:                [dynamic]Hist,
}

key :: proc(x, y: int) -> string {
	return fmt.tprintf("%d,%d", x, y)
}

from_rows :: proc(rows: []string) -> Game_State {
	s: Game_State
	s.walls = make(map[string]bool)
	s.goals = make(map[string]bool)
	s.boxes = make(map[string]bool)
	max_x, max_y := 0, 0
	for row, y in rows {
		max_y = y
		for i := 0; i < len(row); i += 1 {
			x := i
			if x > max_x {
				max_x = x
			}
			ch := row[i]
			k := key(x, y)
			switch ch {
			case '#':
				s.walls[k] = true
			case '.':
				s.goals[k] = true
			case '$':
				s.boxes[k] = true
			case '*':
				s.boxes[k] = true
				s.goals[k] = true
			case '@':
				s.px = x
				s.py = y
			case '+':
				s.px = x
				s.py = y
				s.goals[k] = true
			}
		}
	}
	s.width = max_x + 1
	s.height = max_y + 1
	return s
}

check_win :: proc(s: ^Game_State) {
	s.won = true
	for b in s.boxes {
		if b not_in s.goals {
			s.won = false
			return
		}
	}
}

try_move :: proc(s: ^Game_State, dx, dy: int) -> bool {
	if s.won {
		return false
	}
	nx, ny := s.px + dx, s.py + dy
	nk := key(nx, ny)
	if nk in s.walls {
		return false
	}
	if nk in s.boxes {
		bx, by := nx + dx, ny + dy
		bk := key(bx, by)
		if bk in s.walls || bk in s.boxes {
			return false
		}
		append(&s.hist, Hist{s.px, s.py, nk, bk, true})
		delete_key(&s.boxes, nk)
		s.boxes[bk] = true
		s.px, s.py = nx, ny
		s.moves += 1
		check_win(s)
		return true
	}
	append(&s.hist, Hist{s.px, s.py, "", "", false})
	s.px, s.py = nx, ny
	return true
}

undo :: proc(s: ^Game_State) -> bool {
	if s.won || len(s.hist) == 0 {
		return false
	}
	for len(s.hist) > 0 {
		e := pop(&s.hist)
		if e.is_push {
			s.px, s.py = e.px, e.py
			delete_key(&s.boxes, e.box_to)
			s.boxes[e.box_from] = true
			if s.moves > 0 {
				s.moves -= 1
			}
			s.won = false
			return true
		}
		s.px, s.py = e.px, e.py
	}
	return true
}

render_ascii :: proc(s: Game_State) -> string {
	b := strings.builder_make()
	for y in 0 ..< s.height {
		for x in 0 ..< s.width {
			k := key(x, y)
			if s.px == x && s.py == y {
				strings.write_byte(&b, '+' if k in s.goals else '@')
			} else if k in s.boxes {
				strings.write_byte(&b, '*' if k in s.goals else '$')
			} else if k in s.walls {
				strings.write_byte(&b, '#')
			} else if k in s.goals {
				strings.write_byte(&b, '.')
			} else {
				strings.write_byte(&b, ' ')
			}
		}
		strings.write_byte(&b, '\n')
	}
	return strings.to_string(b)
}
