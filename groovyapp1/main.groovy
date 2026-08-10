#!/usr/bin/env groovy
// groovyapp1 — Groovy 推箱子终端版（教学）
// 运行: groovy main.groovy

evaluate(new File('Game.groovy').text)

def LEVEL = [
    '#######',
    '#. . .#',
    '# $$$ #',
    '#.$@$.#',
    '# $$$ #',
    '#. . .#',
    '#######',
]

def state = GameState.fromRows(LEVEL, 0)
println 'sokoban_groovy — wasd 移动, z 撤销, r 重置, q 退出'
def reader = System.in.newReader()

while (true) {
    println()
    print state.renderAscii()
    def flag = state.won ? ' WIN!' : ''
    print "moves=${state.moves}${flag}\n> "
    def line = reader.readLine()
    if (line == null) break
    line = line.trim()
    if (!line) continue
    def ch = line[0].toLowerCase()
    switch (ch) {
        case 'w': state.tryMove(0, -1); break
        case 's': state.tryMove(0, 1); break
        case 'a': state.tryMove(-1, 0); break
        case 'd': state.tryMove(1, 0); break
        case 'z': state.undo(); break
        case 'r': state = GameState.fromRows(LEVEL, 0); break
        case 'q': System.exit(0)
    }
    if (state.won) println 'Level clear!'
}
