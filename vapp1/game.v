// 推箱子核心逻辑（V 教学）
module main

struct Hist {
	px       int
	py       int
	box_from string
	box_to   string
	is_push  bool
}

struct GameState {
mut:
	walls  map[string]bool
	goals  map[string]bool
	boxes  map[string]bool
	px     int
	py     int
	moves  int
	won    bool
	width  int
	height int
	hist   []Hist
}

fn key(x int, y int) string {
	return '${x},${y}'
}

fn from_rows(rows []string) GameState {
	mut s := GameState{}
	mut max_x := 0
	mut max_y := 0
	for y, row in rows {
		max_y = y
		for x, ch in row {
			if x > max_x {
				max_x = x
			}
			k := key(x, y)
			match ch {
				`#` { s.walls[k] = true }
				`.` { s.goals[k] = true }
				`$` { s.boxes[k] = true }
				`*` {
					s.boxes[k] = true
					s.goals[k] = true
				}
				`@` {
					s.px = x
					s.py = y
				}
				`+` {
					s.px = x
					s.py = y
					s.goals[k] = true
				}
				else {}
			}
		}
	}
	s.width = max_x + 1
	s.height = max_y + 1
	return s
}

fn (mut s GameState) check_win() {
	s.won = true
	for b, _ in s.boxes {
		if b !in s.goals {
			s.won = false
			return
		}
	}
}

fn (mut s GameState) try_move(dx int, dy int) bool {
	if s.won {
		return false
	}
	nx := s.px + dx
	ny := s.py + dy
	nk := key(nx, ny)
	if nk in s.walls {
		return false
	}
	if nk in s.boxes {
		bx := nx + dx
		by := ny + dy
		bk := key(bx, by)
		if bk in s.walls || bk in s.boxes {
			return false
		}
		s.hist << Hist{s.px, s.py, nk, bk, true}
		s.boxes.delete(nk)
		s.boxes[bk] = true
		s.px = nx
		s.py = ny
		s.moves++
		s.check_win()
		return true
	}
	s.hist << Hist{s.px, s.py, '', '', false}
	s.px = nx
	s.py = ny
	return true
}

fn (mut s GameState) undo() bool {
	if s.won || s.hist.len == 0 {
		return false
	}
	for s.hist.len > 0 {
		e := s.hist.pop()
		if e.is_push {
			s.px = e.px
			s.py = e.py
			s.boxes.delete(e.box_to)
			s.boxes[e.box_from] = true
			if s.moves > 0 {
				s.moves--
			}
			s.won = false
			return true
		}
		s.px = e.px
		s.py = e.py
	}
	return true
}

fn (s GameState) render_ascii() string {
	mut out := ''
	for y in 0 .. s.height {
		for x in 0 .. s.width {
			k := key(x, y)
			if s.px == x && s.py == y {
				out += if k in s.goals { '+' } else { '@' }
			} else if k in s.boxes {
				out += if k in s.goals { '*' } else { '$' }
			} else if k in s.walls {
				out += '#'
			} else if k in s.goals {
				out += '.'
			} else {
				out += ' '
			}
		}
		out += '\n'
	}
	return out
}
