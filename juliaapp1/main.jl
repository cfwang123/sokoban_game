#!/usr/bin/env julia
# juliaapp1 — Julia 推箱子终端版（教学）

include(joinpath(@__DIR__, "game.jl"))

const LEVEL = [
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
]

function main()
    state = from_rows(LEVEL, 0)
    println("sokoban_julia — wasd 移动, z 撤销, r 重置, q 退出")
    while true
        println()
        print(render_ascii(state))
        flag = state.won ? " WIN!" : ""
        print("moves=$(state.moves)$flag\n> ")
        line = try
            readline()
        catch
            break
        end
        isempty(line) && continue
        ch = lowercase(line[1])
        if ch == 'w'
            try_move!(state, 0, -1)
        elseif ch == 's'
            try_move!(state, 0, 1)
        elseif ch == 'a'
            try_move!(state, -1, 0)
        elseif ch == 'd'
            try_move!(state, 1, 0)
        elseif ch == 'z'
            undo!(state)
        elseif ch == 'r'
            state = from_rows(LEVEL, 0)
        elseif ch == 'q'
            break
        end
        state.won && println("Level clear!")
    end
end

main()
