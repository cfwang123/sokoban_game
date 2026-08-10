/**
 * angularapp1 — Angular 独立组件教学源码
 * 不强制在本仓库 `ng serve`；逻辑与 play.html 一致。
 *
 * 本地可选：
 *   ng new sokoban --standalone
 *   将本文件与 game-core.ts 拷入 src/app/
 */
import { Component, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  GameState,
  cellAt,
  newGame,
  tryMove,
  undo,
} from './game-core';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="app">
      <h1>Sokoban · Angular</h1>
      <p class="hint">WASD / 方向键 · Z 撤销 · R 重置</p>
      <div class="board">
        <div class="row" *ngFor="let y of rows">
          <span
            class="cell"
            *ngFor="let x of cols"
            [ngClass]="cellClass(x, y)"
            >{{ charAt(x, y) }}</span
          >
        </div>
      </div>
      <p class="status">
        moves={{ state.moves }}{{ state.won ? ' WIN!' : '' }}
      </p>
      <div class="btns">
        <button type="button" (click)="move(0, -1)">W</button>
        <button type="button" (click)="move(-1, 0)">A</button>
        <button type="button" (click)="move(0, 1)">S</button>
        <button type="button" (click)="move(1, 0)">D</button>
        <button type="button" (click)="doUndo()">Z</button>
        <button type="button" (click)="reset()">R</button>
      </div>
    </div>
  `,
  styles: [
    `
      .app {
        text-align: center;
        color: #ecf0f1;
        font-family: system-ui, sans-serif;
      }
      .board {
        display: inline-block;
        background: #16213e;
        padding: 12px;
        border-radius: 8px;
        font-family: Consolas, monospace;
        font-size: 22px;
      }
      .row {
        display: flex;
      }
      .cell {
        width: 1.2em;
        height: 1.2em;
        display: inline-flex;
        align-items: center;
        justify-content: center;
      }
      .c-wall {
        color: #7f8c8d;
      }
      .c-goal {
        color: #e94560;
      }
      .c-box {
        color: #f39c12;
      }
      .c-boxg {
        color: #2ecc71;
      }
      .c-player {
        color: #3498db;
        font-weight: bold;
      }
      .btns button {
        margin: 0.2rem;
        padding: 0.4rem 0.6rem;
        background: #c3002f;
        color: #fff;
        border: none;
        border-radius: 6px;
        cursor: pointer;
      }
    `,
  ],
})
export class AppComponent {
  state: GameState = newGame();

  get rows(): number[] {
    return Array.from({ length: this.state.height }, (_, i) => i);
  }
  get cols(): number[] {
    return Array.from({ length: this.state.width }, (_, i) => i);
  }

  charAt(x: number, y: number): string {
    const c = cellAt(this.state, x, y);
    return c === ' ' ? '\u00a0' : c;
  }

  cellClass(x: number, y: number): string {
    const ch = cellAt(this.state, x, y);
    if (ch === '#') return 'c-wall';
    if (ch === '.') return 'c-goal';
    if (ch === '$') return 'c-box';
    if (ch === '*') return 'c-boxg';
    if (ch === '@' || ch === '+') return 'c-player';
    return '';
  }

  move(dx: number, dy: number): void {
    tryMove(this.state, dx, dy);
  }
  doUndo(): void {
    undo(this.state);
  }
  reset(): void {
    this.state = newGame();
  }

  @HostListener('window:keydown', ['$event'])
  onKey(e: KeyboardEvent): void {
    const k = e.key.toLowerCase();
    if (k === 'w' || e.key === 'ArrowUp') this.move(0, -1);
    else if (k === 's' || e.key === 'ArrowDown') this.move(0, 1);
    else if (k === 'a' || e.key === 'ArrowLeft') this.move(-1, 0);
    else if (k === 'd' || e.key === 'ArrowRight') this.move(1, 0);
    else if (k === 'z') this.doUndo();
    else if (k === 'r') this.reset();
  }
}
