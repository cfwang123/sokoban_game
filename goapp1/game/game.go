package game

import (
	"fmt"
	"strings"
)

type Pos struct{ X, Y int }

func (p Pos) Key() string { return fmt.Sprintf("%d,%d", p.X, p.Y) }
func (p Pos) Off(dx, dy int) Pos { return Pos{p.X + dx, p.Y + dy} }

type hist struct {
	player       Pos
	boxFrom, boxTo string
	push         bool
}

type State struct {
	Walls, Goals, Boxes map[string]bool
	Player              Pos
	Moves               int
	Won                 bool
	W, H, LevelIndex    int
	hist                []hist
}

func FromRows(rows []string, index int) *State {
	s := &State{
		Walls: map[string]bool{}, Goals: map[string]bool{}, Boxes: map[string]bool{},
		LevelIndex: index,
	}
	for y, row := range rows {
		if y > s.H {
			s.H = y
		}
		for x, ch := range row {
			if x > s.W {
				s.W = x
			}
			k := fmt.Sprintf("%d,%d", x, y)
			switch ch {
			case '#':
				s.Walls[k] = true
			case '.':
				s.Goals[k] = true
			case '$':
				s.Boxes[k] = true
			case '*':
				s.Boxes[k] = true
				s.Goals[k] = true
			case '@':
				s.Player = Pos{x, y}
			case '+':
				s.Player = Pos{x, y}
				s.Goals[k] = true
			}
		}
	}
	s.W++
	s.H++
	return s
}

func (s *State) TryMove(dx, dy int) bool {
	if s.Won {
		return false
	}
	n := s.Player.Off(dx, dy)
	nk := n.Key()
	if s.Walls[nk] {
		return false
	}
	if s.Boxes[nk] {
		b := n.Off(dx, dy)
		bk := b.Key()
		if s.Walls[bk] || s.Boxes[bk] {
			return false
		}
		s.hist = append(s.hist, hist{s.Player, nk, bk, true})
		delete(s.Boxes, nk)
		s.Boxes[bk] = true
		s.Player = n
		s.Moves++
		s.checkWin()
		return true
	}
	s.hist = append(s.hist, hist{player: s.Player})
	s.Player = n
	return true
}

func (s *State) Undo() {
	if s.Won || len(s.hist) == 0 {
		return
	}
	var e hist
	for len(s.hist) > 0 {
		e = s.hist[len(s.hist)-1]
		s.hist = s.hist[:len(s.hist)-1]
		if e.push {
			break
		}
		s.Player = e.player
	}
	if !e.push {
		return
	}
	s.Player = e.player
	delete(s.Boxes, e.boxTo)
	s.Boxes[e.boxFrom] = true
	if s.Moves > 0 {
		s.Moves--
	}
	s.Won = false
}

func (s *State) checkWin() {
	for b := range s.Boxes {
		if !s.Goals[b] {
			s.Won = false
			return
		}
	}
	s.Won = true
}

func (s *State) ASCII() string {
	var b strings.Builder
	for y := 0; y < s.H; y++ {
		for x := 0; x < s.W; x++ {
			k := fmt.Sprintf("%d,%d", x, y)
			ch := byte(' ')
			switch {
			case s.Player.X == x && s.Player.Y == y:
				if s.Goals[k] {
					ch = '+'
				} else {
					ch = '@'
				}
			case s.Boxes[k]:
				if s.Goals[k] {
					ch = '*'
				} else {
					ch = '$'
				}
			case s.Walls[k]:
				ch = '#'
			case s.Goals[k]:
				ch = '.'
			}
			b.WriteByte(ch)
		}
		b.WriteByte('\n')
	}
	return b.String()
}
