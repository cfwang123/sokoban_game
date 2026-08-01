package main

import (
	"bufio"
	"fmt"
	"os"
	"sokoban_go/game"
	"strings"
)

var level = []string{
	"#######",
	"#. . .#",
	"# $$$ #",
	"#.$@$.#",
	"# $$$ #",
	"#. . .#",
	"#######",
}

func main() {
	st := game.FromRows(level, 0)
	in := bufio.NewReader(os.Stdin)
	fmt.Println("sokoban_go — wasd move, z undo, r reset, q quit")
	// 图形版可换 ebiten.RunGame；教学默认终端
	for {
		fmt.Print("\n", st.ASCII())
		fmt.Printf("moves=%d %s\n> ", st.Moves, map[bool]string{true: "WIN", false: ""}[st.Won])
		line, _ := in.ReadString('\n')
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		switch line[0] {
		case 'w', 'W':
			st.TryMove(0, -1)
		case 's', 'S':
			st.TryMove(0, 1)
		case 'a', 'A':
			st.TryMove(-1, 0)
		case 'd', 'D':
			st.TryMove(1, 0)
		case 'z', 'Z':
			st.Undo()
		case 'r', 'R':
			st = game.FromRows(level, 0)
		case 'q', 'Q':
			return
		}
	}
}
