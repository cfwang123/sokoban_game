%% 推箱子核心逻辑（Erlang 教学）
-module(game).
-export([from_rows/1, try_move/3, undo/1, render_ascii/1, moves/1, won/1]).

%% state = {Walls, Goals, Boxes, {PX,PY}, Moves, Won, W, H, Hist}
%% sets as lists of {X,Y}

key(X, Y) -> {X, Y}.

from_rows(Rows) ->
    {Walls, Goals, Boxes, Pos, MaxX, MaxY} = parse(Rows, 0, [], [], [], {0,0}, 0, 0),
    {Walls, Goals, Boxes, Pos, 0, false, MaxX + 1, MaxY + 1, []}.

parse([], _, W, G, B, P, MX, MY) -> {W, G, B, P, MX, MY};
parse([Row|Rest], Y, W, G, B, P, MX, MY) ->
    {W1, G1, B1, P1, MX1} = parse_row(Row, 0, Y, W, G, B, P, MX),
    parse(Rest, Y + 1, W1, G1, B1, P1, MX1, max(MY, Y)).

parse_row([], _, _, W, G, B, P, MX) -> {W, G, B, P, MX};
parse_row([Ch|Rest], X, Y, W, G, B, P, MX) ->
    MX1 = max(MX, X),
    {W1, G1, B1, P1} = apply_ch(Ch, X, Y, W, G, B, P),
    parse_row(Rest, X + 1, Y, W1, G1, B1, P1, MX1).

apply_ch($#, X, Y, W, G, B, P) -> {[key(X,Y)|W], G, B, P};
apply_ch($., X, Y, W, G, B, P) -> {W, [key(X,Y)|G], B, P};
apply_ch($$, X, Y, W, G, B, P) -> {W, G, [key(X,Y)|B], P};
apply_ch($*, X, Y, W, G, B, P) -> {W, [key(X,Y)|G], [key(X,Y)|B], P};
apply_ch($@, X, Y, W, G, B, _) -> {W, G, B, key(X,Y)};
apply_ch($+, X, Y, W, G, B, _) -> {W, [key(X,Y)|G], B, key(X,Y)};
apply_ch(_, _, _, W, G, B, P) -> {W, G, B, P}.

member_pos(K, L) -> lists:member(K, L).

check_win(Boxes, Goals) ->
    lists:all(fun(B) -> member_pos(B, Goals) end, Boxes).

moves({_, _, _, _, M, _, _, _, _}) -> M.
won({_, _, _, _, _, Won, _, _, _}) -> Won.

try_move(State, DX, DY) ->
    {Walls, Goals, Boxes, {PX, PY}, Moves, Won, W, H, Hist} = State,
    case Won of
        true -> State;
        false ->
            NX = PX + DX, NY = PY + DY,
            NK = key(NX, NY),
            case member_pos(NK, Walls) of
                true -> State;
                false ->
                    case member_pos(NK, Boxes) of
                        true ->
                            BX = NX + DX, BY = NY + DY, BK = key(BX, BY),
                            case member_pos(BK, Walls) orelse member_pos(BK, Boxes) of
                                true -> State;
                                false ->
                                    Boxes2 = [BK | lists:delete(NK, Boxes)],
                                    Won2 = check_win(Boxes2, Goals),
                                    {Walls, Goals, Boxes2, {NX, NY}, Moves + 1, Won2, W, H,
                                     [{{PX,PY}, NK, BK}|Hist]}
                            end;
                        false ->
                            {Walls, Goals, Boxes, {NX, NY}, Moves, false, W, H,
                             [{{PX,PY}, none, none}|Hist]}
                    end
            end
    end.

undo(State) ->
    {Walls, Goals, Boxes, _, Moves, Won, W, H, Hist} = State,
    case Won orelse Hist =:= [] of
        true -> State;
        false -> undo_loop(Hist, Boxes, Moves, Walls, Goals, W, H)
    end.

undo_loop([], Boxes, Moves, Walls, Goals, W, H) ->
    {Walls, Goals, Boxes, {0,0}, Moves, false, W, H, []};
undo_loop([{{PX,PY}, none, none}|Rest], Boxes, Moves, Walls, Goals, W, H) ->
    case Rest of
        [] -> {Walls, Goals, Boxes, {PX,PY}, Moves, false, W, H, []};
        _ -> undo_loop(Rest, Boxes, Moves, Walls, Goals, W, H)
    end;
undo_loop([{{PX,PY}, BF, BT}|Rest], Boxes, Moves, Walls, Goals, W, H) when BF =/= none ->
    Boxes2 = [BF | lists:delete(BT, Boxes)],
    {Walls, Goals, Boxes2, {PX,PY}, max(0, Moves - 1), false, W, H, Rest}.

render_ascii({Walls, Goals, Boxes, {PX, PY}, _, _, Width, Height, _}) ->
    lists:flatten([render_row(Y, Width, Walls, Goals, Boxes, PX, PY) || Y <- lists:seq(0, Height - 1)]).

render_row(Y, Width, Walls, Goals, Boxes, PX, PY) ->
    [cell(X, Y, Walls, Goals, Boxes, PX, PY) || X <- lists:seq(0, Width - 1)] ++ "\n".

cell(X, Y, Walls, Goals, Boxes, PX, PY) ->
    K = key(X, Y),
    if
        X =:= PX, Y =:= PY ->
            case member_pos(K, Goals) of true -> $+; false -> $@ end;
        true ->
            case member_pos(K, Boxes) of
                true -> case member_pos(K, Goals) of true -> $*; false -> $$ end;
                false ->
                    case member_pos(K, Walls) of
                        true -> $#;
                        false ->
                            case member_pos(K, Goals) of true -> $.; false -> $\s end
                    end
            end
    end.
