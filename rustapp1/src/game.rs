use std::collections::{HashSet, VecDeque};

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Pos {
    pub x: i32,
    pub y: i32,
}

impl Pos {
    pub fn key(self) -> String {
        format!("{},{}", self.x, self.y)
    }
    pub fn offset(self, dx: i32, dy: i32) -> Pos {
        Pos {
            x: self.x + dx,
            y: self.y + dy,
        }
    }
}

#[derive(Clone)]
struct Hist {
    player: Pos,
    box_from: Option<String>,
    box_to: Option<String>,
}

pub struct GameState {
    pub walls: HashSet<String>,
    pub goals: HashSet<String>,
    pub boxes: HashSet<String>,
    pub player: Pos,
    pub moves: i32,
    pub won: bool,
    pub width: i32,
    pub height: i32,
    pub level_index: usize,
    hist: Vec<Hist>,
}

impl GameState {
    pub fn from_rows(rows: &[&str], index: usize) -> Self {
        let mut walls = HashSet::new();
        let mut goals = HashSet::new();
        let mut boxes = HashSet::new();
        let mut player = Pos { x: 0, y: 0 };
        let mut max_x = 0i32;
        let mut max_y = 0i32;
        for (y, row) in rows.iter().enumerate() {
            max_y = y as i32;
            for (x, ch) in row.chars().enumerate() {
                max_x = max_x.max(x as i32);
                let k = format!("{},{}", x, y);
                match ch {
                    '#' => {
                        walls.insert(k);
                    }
                    '.' => {
                        goals.insert(k);
                    }
                    '$' => {
                        boxes.insert(k);
                    }
                    '*' => {
                        boxes.insert(k.clone());
                        goals.insert(k);
                    }
                    '@' => player = Pos {
                        x: x as i32,
                        y: y as i32,
                    },
                    '+' => {
                        player = Pos {
                            x: x as i32,
                            y: y as i32,
                        };
                        goals.insert(k);
                    }
                    _ => {}
                }
            }
        }
        Self {
            walls,
            goals,
            boxes,
            player,
            moves: 0,
            won: false,
            width: max_x + 1,
            height: max_y + 1,
            level_index: index,
            hist: Vec::new(),
        }
    }

    pub fn try_move(&mut self, dx: i32, dy: i32) -> bool {
        if self.won {
            return false;
        }
        let next = self.player.offset(dx, dy);
        let nk = next.key();
        if self.walls.contains(&nk) {
            return false;
        }
        if self.boxes.contains(&nk) {
            let bn = next.offset(dx, dy);
            let bk = bn.key();
            if self.walls.contains(&bk) || self.boxes.contains(&bk) {
                return false;
            }
            self.hist.push(Hist {
                player: self.player,
                box_from: Some(nk.clone()),
                box_to: Some(bk.clone()),
            });
            self.boxes.remove(&nk);
            self.boxes.insert(bk);
            self.player = next;
            self.moves += 1;
            self.check_win();
            return true;
        }
        self.hist.push(Hist {
            player: self.player,
            box_from: None,
            box_to: None,
        });
        self.player = next;
        true
    }

    pub fn undo(&mut self) -> bool {
        if self.won || self.hist.is_empty() {
            return false;
        }
        let mut e = None;
        while let Some(h) = self.hist.pop() {
            if h.box_from.is_some() {
                e = Some(h);
                break;
            }
            self.player = h.player;
            e = Some(h);
        }
        let Some(e) = e else { return true };
        if e.box_from.is_none() {
            return true;
        }
        self.player = e.player;
        if let (Some(f), Some(t)) = (e.box_from, e.box_to) {
            self.boxes.remove(&t);
            self.boxes.insert(f);
        }
        if self.moves > 0 {
            self.moves -= 1;
        }
        self.won = false;
        true
    }

    fn check_win(&mut self) {
        self.won = self.boxes.iter().all(|b| self.goals.contains(b));
    }

    pub fn render_ascii(&self) -> String {
        let mut out = String::new();
        for y in 0..self.height {
            for x in 0..self.width {
                let k = format!("{},{}", x, y);
                let ch = if self.player.x == x && self.player.y == y {
                    if self.goals.contains(&k) { '+' } else { '@' }
                } else if self.boxes.contains(&k) {
                    if self.goals.contains(&k) { '*' } else { '$' }
                } else if self.walls.contains(&k) {
                    '#'
                } else if self.goals.contains(&k) {
                    '.'
                } else {
                    ' '
                };
                out.push(ch);
            }
            out.push('\n');
        }
        out
    }
}

/// BFS 寻路
pub fn find_path(state: &GameState, tx: i32, ty: i32) -> Option<Vec<(i32, i32)>> {
    if state.player.x == tx && state.player.y == ty {
        return Some(vec![]);
    }
    let mut blocked: HashSet<String> = state.walls.iter().cloned().collect();
    blocked.extend(state.boxes.iter().cloned());
    let start = state.player.key();
    let target = format!("{},{}", tx, ty);
    let mut q = VecDeque::new();
    q.push_back(state.player);
    let mut visited = HashSet::new();
    visited.insert(start.clone());
    let mut parent: std::collections::HashMap<String, (String, i32, i32)> =
        std::collections::HashMap::new();
    let dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)];
    while let Some(cur) = q.pop_front() {
        let ck = cur.key();
        for (dx, dy) in dirs {
            let n = cur.offset(dx, dy);
            let nk = n.key();
            if blocked.contains(&nk) || visited.contains(&nk) {
                continue;
            }
            visited.insert(nk.clone());
            parent.insert(nk.clone(), (ck.clone(), dx, dy));
            if nk == target {
                let mut path = Vec::new();
                let mut p = nk;
                while p != start {
                    let (from, dx, dy) = parent.get(&p)?.clone();
                    path.push((dx, dy));
                    p = from;
                }
                path.reverse();
                return Some(path);
            }
            q.push_back(n);
        }
    }
    None
}
