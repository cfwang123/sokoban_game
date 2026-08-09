#!/usr/bin/env node
/**
 * nodejsapp1 — 推箱子终端版（教学）。
 */

'use strict';

const readline = require('readline');
const game = require('./game');

const LEVEL = [
  '#######',
  '#. . .#',
  '# $$$ #',
  '#.$@$.#',
  '# $$$ #',
  '#. . .#',
  '#######',
];

let state = game.fromRows(LEVEL, 0);

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

console.log('sokoban_node — wasd 移动, z 撤销, r 重置, q 退出');

function prompt() {
  const flag = state.won ? ' WIN!' : '';
  process.stdout.write('\n' + game.renderAscii(state));
  process.stdout.write('moves=' + state.moves + flag + '\n> ');
}

function handle(line) {
  line = (line || '').trim();
  if (!line) {
    prompt();
    return;
  }
  const ch = line[0].toLowerCase();
  if (ch === 'w') game.tryMove(state, 0, -1);
  else if (ch === 's') game.tryMove(state, 0, 1);
  else if (ch === 'a') game.tryMove(state, -1, 0);
  else if (ch === 'd') game.tryMove(state, 1, 0);
  else if (ch === 'z') game.undo(state);
  else if (ch === 'r') state = game.fromRows(LEVEL, 0);
  else if (ch === 'q') {
    rl.close();
    return;
  }
  if (state.won) console.log('Level clear!');
  prompt();
}

rl.on('line', handle);
rl.on('close', () => process.exit(0));
prompt();
