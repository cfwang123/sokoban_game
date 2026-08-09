#!/usr/bin/env php
<?php
/**
 * phpapp1 — 推箱子终端版（教学）。
 */

require_once __DIR__ . '/game.php';

$level = [
    '#######',
    '#. . .#',
    '# $$$ #',
    '#.$@$.#',
    '# $$$ #',
    '#. . .#',
    '#######',
];

$state = GameState::fromRows($level, 0);
echo "sokoban_php — wasd 移动, z 撤销, r 重置, q 退出\n";

while (true) {
    echo "\n";
    echo $state->renderAscii();
    $flag = $state->won ? ' WIN!' : '';
    echo "moves={$state->moves}{$flag}\n> ";
    $line = fgets(STDIN);
    if ($line === false) {
        break;
    }
    $line = trim($line);
    if ($line === '') {
        continue;
    }
    $ch = strtolower($line[0]);
    switch ($ch) {
        case 'w':
            $state->tryMove(0, -1);
            break;
        case 's':
            $state->tryMove(0, 1);
            break;
        case 'a':
            $state->tryMove(-1, 0);
            break;
        case 'd':
            $state->tryMove(1, 0);
            break;
        case 'z':
            $state->undo();
            break;
        case 'r':
            $state = GameState::fromRows($level, 0);
            break;
        case 'q':
            exit(0);
    }
    if ($state->won) {
        echo "Level clear!\n";
    }
}
