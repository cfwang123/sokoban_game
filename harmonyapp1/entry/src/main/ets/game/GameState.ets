/**
 * HarmonyOS ArkTS 推箱子状态（教学）。
 * 在 DevEco Studio 中新建 Stage 工程后拷入本目录。
 */
export class Pos {
  x: number = 0
  y: number = 0
  constructor(x: number = 0, y: number = 0) {
    this.x = x
    this.y = y
  }
  key(): string { return `${this.x},${this.y}` }
}

class Hist {
  px: number = 0
  py: number = 0
  from: string = ''
  to: string = ''
  push: boolean = false
}

export class GameState {
  walls: Set<string> = new Set()
  goals: Set<string> = new Set()
  boxes: Set<string> = new Set()
  player: Pos = new Pos()
  moves: number = 0
  won: boolean = false
  width: number = 0
  height: number = 0
  levelIndex: number = 0
  private hist: Hist[] = []

  static fromRows(rows: string[], index: number): GameState {
    const s = new GameState()
    s.levelIndex = index
    let maxX = 0
    let maxY = 0
    for (let y = 0; y < rows.length; y++) {
      maxY = y
      const row = rows[y]
      for (let x = 0; x < row.length; x++) {
        if (x > maxX) maxX = x
        const k = `${x},${y}`
        const ch = row.charAt(x)
        if (ch === '#') s.walls.add(k)
        else if (ch === '.') s.goals.add(k)
        else if (ch === '$') s.boxes.add(k)
        else if (ch === '*') { s.boxes.add(k); s.goals.add(k) }
        else if (ch === '@') s.player = new Pos(x, y)
        else if (ch === '+') { s.player = new Pos(x, y); s.goals.add(k) }
      }
    }
    s.width = maxX + 1
    s.height = maxY + 1
    return s
  }

  tryMove(dx: number, dy: number): boolean {
    if (this.won) return false
    const nx = this.player.x + dx
    const ny = this.player.y + dy
    const nk = `${nx},${ny}`
    if (this.walls.has(nk)) return false
    if (this.boxes.has(nk)) {
      const bk = `${nx + dx},${ny + dy}`
      if (this.walls.has(bk) || this.boxes.has(bk)) return false
      const h = new Hist()
      h.px = this.player.x; h.py = this.player.y; h.from = nk; h.to = bk; h.push = true
      this.hist.push(h)
      this.boxes.delete(nk)
      this.boxes.add(bk)
      this.player = new Pos(nx, ny)
      this.moves++
      this.checkWin()
      return true
    }
    const h2 = new Hist()
    h2.px = this.player.x; h2.py = this.player.y
    this.hist.push(h2)
    this.player = new Pos(nx, ny)
    return true
  }

  undo(): void {
    if (this.won || this.hist.length === 0) return
    let e: Hist | undefined = undefined
    while (this.hist.length > 0) {
      e = this.hist.pop()
      if (e && e.push) break
      if (e) this.player = new Pos(e.px, e.py)
    }
    if (!e || !e.push) return
    this.player = new Pos(e.px, e.py)
    this.boxes.delete(e.to)
    this.boxes.add(e.from)
    if (this.moves > 0) this.moves--
    this.won = false
  }

  private checkWin(): void {
    for (const b of this.boxes) {
      if (!this.goals.has(b)) { this.won = false; return }
    }
    this.won = true
  }
}

export const DEMO_LEVEL: string[] = [
  '###',
  '#@#',
  '#$#',
  '#.#',
  '###'
]
