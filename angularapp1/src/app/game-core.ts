/** Angular 教学：纯 TS 玩法核心（无 Angular 依赖） */

export const LEVEL = [
  '#######',
  '#. . .#',
  '# $$$ #',
  '#.$@$.#',
  '# $$$ #',
  '#. . .#',
  '#######',
];

export interface GameState {
  walls: Record<string, boolean>;
  goals: Record<string, boolean>;
  boxes: Record<string, boolean>;
  px: number;
  py: number;
  moves: number;
  won: boolean;
  width: number;
  height: number;
  hist: { px: number; py: number; bf: string | null; bt: string | null }[];
}

function key(x: number, y: number): string {
  return `${x},${y}`;
}

export function fromRows(rows: string[]): GameState {
  const walls: Record<string, boolean> = {};
  const goals: Record<string, boolean> = {};
  const boxes: Record<string, boolean> = {};
  let px = 0,
    py = 0,
    maxX = 0,
    maxY = 0;
  rows.forEach((row, y) => {
    maxY = y;
    [...row].forEach((ch, x) => {
      if (x > maxX) maxX = x;
      const k = key(x, y);
      if (ch === '#') walls[k] = true;
      else if (ch === '.') goals[k] = true;
      else if (ch === '$') boxes[k] = true;
      else if (ch === '*') {
        boxes[k] = true;
        goals[k] = true;
      } else if (ch === '@') {
        px = x;
        py = y;
      } else if (ch === '+') {
        px = x;
        py = y;
        goals[k] = true;
      }
    });
  });
  return {
    walls,
    goals,
    boxes,
    px,
    py,
    moves: 0,
    won: false,
    width: maxX + 1,
    height: maxY + 1,
    hist: [],
  };
}

export function tryMove(s: GameState, dx: number, dy: number): boolean {
  if (s.won) return false;
  const nx = s.px + dx,
    ny = s.py + dy;
  const nk = key(nx, ny);
  if (s.walls[nk]) return false;
  if (s.boxes[nk]) {
    const bx = nx + dx,
      by = ny + dy;
    const bk = key(bx, by);
    if (s.walls[bk] || s.boxes[bk]) return false;
    s.hist.push({ px: s.px, py: s.py, bf: nk, bt: bk });
    delete s.boxes[nk];
    s.boxes[bk] = true;
    s.px = nx;
    s.py = ny;
    s.moves++;
    s.won = Object.keys(s.boxes).every((b) => s.goals[b]);
    return true;
  }
  s.hist.push({ px: s.px, py: s.py, bf: null, bt: null });
  s.px = nx;
  s.py = ny;
  return true;
}

export function undo(s: GameState): boolean {
  if (s.won || !s.hist.length) return false;
  while (s.hist.length) {
    const e = s.hist.pop()!;
    if (e.bf != null) {
      s.px = e.px;
      s.py = e.py;
      delete s.boxes[e.bt!];
      s.boxes[e.bf] = true;
      if (s.moves > 0) s.moves--;
      s.won = false;
      return true;
    }
    s.px = e.px;
    s.py = e.py;
  }
  return true;
}

export function cellAt(s: GameState, x: number, y: number): string {
  const k = key(x, y);
  if (s.px === x && s.py === y) return s.goals[k] ? '+' : '@';
  if (s.boxes[k]) return s.goals[k] ? '*' : '$';
  if (s.walls[k]) return '#';
  if (s.goals[k]) return '.';
  return ' ';
}

export function newGame(): GameState {
  return fromRows(LEVEL);
}
