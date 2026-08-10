%% 推箱子核心逻辑（Prolog 教学，SWI-Prolog）

:- module(game, [
    from_rows/2,
    try_move/4,
    undo/2,
    render_ascii/2,
    state_moves/2,
    state_won/2
]).

%% state(Walls, Goals, Boxes, PX-PY, Moves, Won, Width, Height, Hist)
%% Walls/Goals/Boxes: list of X-Y

cell_key(X, Y, X-Y).

from_rows(Rows, state(Walls, Goals, Boxes, PX-PY, 0, false, W, H, [])) :-
    parse_rows(Rows, 0, [], [], [], 0-0, 0, 0, Walls, Goals, Boxes, PX-PY, MaxX, MaxY),
    W is MaxX + 1,
    H is MaxY + 1.

parse_rows([], _, Walls, Goals, Boxes, Pos, MaxX, MaxY, Walls, Goals, Boxes, Pos, MaxX, MaxY).
parse_rows([Row|Rest], Y, Walls0, Goals0, Boxes0, Pos0, MaxX0, MaxY0,
           Walls, Goals, Boxes, Pos, MaxX, MaxY) :-
    atom_chars(Row, Chars),
    parse_row(Chars, 0, Y, Walls0, Goals0, Boxes0, Pos0, MaxX0,
              Walls1, Goals1, Boxes1, Pos1, MaxX1),
    MaxY1 is max(MaxY0, Y),
    Y1 is Y + 1,
    parse_rows(Rest, Y1, Walls1, Goals1, Boxes1, Pos1, MaxX1, MaxY1,
               Walls, Goals, Boxes, Pos, MaxX, MaxY).

parse_row([], _, _, W, G, B, P, MX, W, G, B, P, MX).
parse_row([Ch|Rest], X, Y, Walls0, Goals0, Boxes0, Pos0, MaxX0,
          Walls, Goals, Boxes, Pos, MaxX) :-
    MaxX1 is max(MaxX0, X),
    apply_cell(Ch, X, Y, Walls0, Goals0, Boxes0, Pos0,
               Walls1, Goals1, Boxes1, Pos1),
    X1 is X + 1,
    parse_row(Rest, X1, Y, Walls1, Goals1, Boxes1, Pos1, MaxX1,
              Walls, Goals, Boxes, Pos, MaxX).

apply_cell('#', X, Y, W, G, B, P, [X-Y|W], G, B, P).
apply_cell('.', X, Y, W, G, B, P, W, [X-Y|G], B, P).
apply_cell('$', X, Y, W, G, B, P, W, G, [X-Y|B], P).
apply_cell('*', X, Y, W, G, B, P, W, [X-Y|G], [X-Y|B], P).
apply_cell('@', X, Y, W, G, B, _, W, G, B, X-Y).
apply_cell('+', X, Y, W, G, B, _, W, [X-Y|G], B, X-Y).
apply_cell(_, _, _, W, G, B, P, W, G, B, P).

member_pos(X-Y, List) :- member(X-Y, List).

check_win(Boxes, Goals) :-
    forall(member(Box, Boxes), member(Box, Goals)).

state_moves(state(_,_,_,_,M,_,_,_,_), M).
state_won(state(_,_,_,_,_,Won,_,_,_), Won).

try_move(state(_,_,_,_,_,true,_,_,_), _, _, _) :- !, fail.
try_move(state(Walls, Goals, Boxes, PX-PY, Moves, _, W, H, Hist), DX, DY,
         state(Walls, Goals, Boxes2, NX-NY, Moves2, Won2, W, H, Hist2)) :-
    NX is PX + DX,
    NY is PY + DY,
    \+ member_pos(NX-NY, Walls),
    ( member_pos(NX-NY, Boxes) ->
        BX is NX + DX,
        BY is NY + DY,
        \+ member_pos(BX-BY, Walls),
        \+ member_pos(BX-BY, Boxes),
        select(NX-NY, Boxes, Boxes1),
        Boxes2 = [BX-BY|Boxes1],
        Moves2 is Moves + 1,
        Hist2 = [hist(PX-PY, NX-NY, BX-BY)|Hist],
        ( check_win(Boxes2, Goals) -> Won2 = true ; Won2 = false )
    ;
        Boxes2 = Boxes,
        Moves2 = Moves,
        Won2 = false,
        Hist2 = [hist(PX-PY, none, none)|Hist]
    ).

undo(state(_,_,_,_,_,true,_,_,_), _) :- !, fail.
undo(state(_,_,_,_,_,_, _,_,[]), _) :- !, fail.
undo(state(Walls, Goals, Boxes, _, Moves, _, W, H, Hist),
     state(Walls, Goals, Boxes2, PX-PY, Moves2, false, W, H, Rest)) :-
    undo_loop(Hist, Boxes, Moves, Boxes2, PX-PY, Moves2, Rest).

%% 与其它语言版一致：回退到上一次推箱（中间走路一并撤销）
undo_loop([hist(P, none, none)|Rest], Boxes, Moves, Boxes2, Pos, Moves2, HistOut) :-
    !,
    ( Rest = [] ->
        Boxes2 = Boxes, Pos = P, Moves2 = Moves, HistOut = []
    ; undo_loop(Rest, Boxes, Moves, Boxes2, Pos, Moves2, HistOut)
    ).
undo_loop([hist(P, BF, BT)|Rest], Boxes, Moves, Boxes2, P, Moves2, Rest) :-
    BF \= none,
    select(BT, Boxes, Boxes1),
    Boxes2 = [BF|Boxes1],
    Moves2 is max(0, Moves - 1).

render_ascii(state(Walls, Goals, Boxes, PX-PY, _, _, Width, Height, _), Text) :-
    render_rows(0, Height, Width, Walls, Goals, Boxes, PX-PY, Lines),
    atomic_list_concat(Lines, '\n', Body),
    atom_concat(Body, '\n', Text).

render_rows(Y, Height, _, _, _, _, _, []) :- Y >= Height, !.
render_rows(Y, Height, Width, Walls, Goals, Boxes, Player, [Line|Rest]) :-
    render_row(0, Width, Y, Walls, Goals, Boxes, Player, Chars),
    atomic_list_concat(Chars, '', Line),
    Y1 is Y + 1,
    render_rows(Y1, Height, Width, Walls, Goals, Boxes, Player, Rest).

render_row(X, Width, _, _, _, _, _, []) :- X >= Width, !.
render_row(X, Width, Y, Walls, Goals, Boxes, PX-PY, [Ch|Rest]) :-
    ( X =:= PX, Y =:= PY ->
        ( member_pos(X-Y, Goals) -> Ch = '+' ; Ch = '@' )
    ; member_pos(X-Y, Boxes) ->
        ( member_pos(X-Y, Goals) -> Ch = '*' ; Ch = '$' )
    ; member_pos(X-Y, Walls) ->
        Ch = '#'
    ; member_pos(X-Y, Goals) ->
        Ch = '.'
    ;
        Ch = ' '
    ),
    X1 is X + 1,
    render_row(X1, Width, Y, Walls, Goals, Boxes, PX-PY, Rest).
