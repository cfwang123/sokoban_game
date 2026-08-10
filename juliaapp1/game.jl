# 推箱子核心逻辑（Julia 教学）

const Cell = String

mutable struct Hist
    player::Tuple{Int,Int}
    box_from::Union{Nothing,Cell}
    box_to::Union{Nothing,Cell}
end

mutable struct GameState
    walls::Set{Cell}
    goals::Set{Cell}
    boxes::Set{Cell}
    player::Tuple{Int,Int}
    moves::Int
    won::Bool
    width::Int
    height::Int
    hist::Vector{Hist}
end

cell_key(x::Int, y::Int) = string(x, ",", y)

function from_rows(rows::Vector{String}, index::Int=0)::GameState
    walls = Set{Cell}()
    goals = Set{Cell}()
    boxes = Set{Cell}()
    px, py = 0, 0
    max_x, max_y = 0, 0
    for (y, row) in enumerate(rows)
        max_y = y - 1
        for (x0, ch) in enumerate(row)
            x = x0 - 1
            max_x = max(max_x, x)
            k = cell_key(x, y - 1)
            if ch == '#'
                push!(walls, k)
            elseif ch == '.'
                push!(goals, k)
            elseif ch == '$'
                push!(boxes, k)
            elseif ch == '*'
                push!(boxes, k); push!(goals, k)
            elseif ch == '@'
                px, py = x, y - 1
            elseif ch == '+'
                px, py = x, y - 1
                push!(goals, k)
            end
        end
    end
    GameState(walls, goals, boxes, (px, py), 0, false, max_x + 1, max_y + 1, Hist[])
end

function check_win!(s::GameState)
    s.won = all(b -> b in s.goals, s.boxes)
end

function try_move!(s::GameState, dx::Int, dy::Int)::Bool
    s.won && return false
    px, py = s.player
    nx, ny = px + dx, py + dy
    nk = cell_key(nx, ny)
    nk in s.walls && return false
    if nk in s.boxes
        bx, by = nx + dx, ny + dy
        bk = cell_key(bx, by)
        (bk in s.walls || bk in s.boxes) && return false
        push!(s.hist, Hist(s.player, nk, bk))
        delete!(s.boxes, nk)
        push!(s.boxes, bk)
        s.player = (nx, ny)
        s.moves += 1
        check_win!(s)
        return true
    end
    push!(s.hist, Hist(s.player, nothing, nothing))
    s.player = (nx, ny)
    true
end

function undo!(s::GameState)::Bool
    (s.won || isempty(s.hist)) && return false
    while !isempty(s.hist)
        e = pop!(s.hist)
        if e.box_from !== nothing
            s.player = e.player
            delete!(s.boxes, e.box_to)
            push!(s.boxes, e.box_from)
            s.moves > 0 && (s.moves -= 1)
            s.won = false
            return true
        end
        s.player = e.player
    end
    true
end

function render_ascii(s::GameState)::String
    io = IOBuffer()
    for y in 0:s.height-1
        for x in 0:s.width-1
            k = cell_key(x, y)
            if s.player == (x, y)
                print(io, k in s.goals ? '+' : '@')
            elseif k in s.boxes
                print(io, k in s.goals ? '*' : '$')
            elseif k in s.walls
                print(io, '#')
            elseif k in s.goals
                print(io, '.')
            else
                print(io, ' ')
            end
        end
        print(io, '\n')
    end
    String(take!(io))
end
