import { DEMO_LEVEL, GameState } from '../game/GameState'

/**
 * 主页面教学示意：用 Grid 显示格子字符。
 * 真机：DevEco Studio 创建 API 12+ 工程，配置 EntryAbility 指向本页。
 */
@Entry
@Component
struct Index {
  @State state: GameState = GameState.fromRows(DEMO_LEVEL, 0)
  @State grid: string[] = []

  aboutToAppear(): void {
    this.refreshGrid()
  }

  refreshGrid(): void {
    const g: string[] = []
    for (let y = 0; y < this.state.height; y++) {
      let row = ''
      for (let x = 0; x < this.state.width; x++) {
        const k = `${x},${y}`
        if (this.state.player.x === x && this.state.player.y === y) {
          row += this.state.goals.has(k) ? '+' : '@'
        } else if (this.state.boxes.has(k)) {
          row += this.state.goals.has(k) ? '*' : '$'
        } else if (this.state.walls.has(k)) row += '#'
        else if (this.state.goals.has(k)) row += '.'
        else row += ' '
      }
      g.push(row)
    }
    this.grid = g
  }

  move(dx: number, dy: number): void {
    this.state.tryMove(dx, dy)
    this.refreshGrid()
  }

  build() {
    Column({ space: 8 }) {
      Text(`推箱子 Harmony  步数:${this.state.moves}${this.state.won ? ' 过关' : ''}`)
        .fontSize(18)
        .fontColor('#E94560')
      ForEach(this.grid, (row: string) => {
        Text(row)
          .fontFamily('monospace')
          .fontSize(22)
          .fontColor('#EEEEEE')
      })
      Row({ space: 8 }) {
        Button('↑').onClick(() => this.move(0, -1))
        Button('↓').onClick(() => this.move(0, 1))
        Button('←').onClick(() => this.move(-1, 0))
        Button('→').onClick(() => this.move(1, 0))
      }
      Row({ space: 8 }) {
        Button('撤销').onClick(() => {
          this.state.undo()
          this.refreshGrid()
        })
        Button('重置').onClick(() => {
          this.state = GameState.fromRows(DEMO_LEVEL, 0)
          this.refreshGrid()
        })
      }
    }
    .width('100%')
    .height('100%')
    .padding(16)
    .backgroundColor('#1A1A2E')
  }
}
