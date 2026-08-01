mod game;

use game::GameState;
use std::io::{self, Write};

const LEVEL: &[&str] = &[
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
];

fn main() {
    let mut state = GameState::from_rows(LEVEL, 0);
    println!("sokoban_rust — WASD move, z undo, r reset, q quit");
    loop {
        print!("\n{}", state.render_ascii());
        println!("moves={} {}", state.moves, if state.won { "WIN!" } else { "" });
        print!("> ");
        io::stdout().flush().ok();
        let mut line = String::new();
        if io::stdin().read_line(&mut line).is_err() {
            break;
        }
        match line.trim().chars().next().unwrap_or(' ') {
            'w' | 'W' => {
                state.try_move(0, -1);
            }
            's' | 'S' => {
                state.try_move(0, 1);
            }
            'a' | 'A' => {
                state.try_move(-1, 0);
            }
            'd' | 'D' => {
                state.try_move(1, 0);
            }
            'z' | 'Z' => {
                state.undo();
            }
            'r' | 'R' => state = GameState::from_rows(LEVEL, 0),
            'q' | 'Q' => break,
            _ => {}
        }
        if state.won {
            println!("Level clear!");
        }
    }
}
