%% prologapp1 — Prolog 推箱子终端版（教学）
%% 运行: swipl -q -s main.pl

:- use_module(game).

level([
    '#######',
    '#. . .#',
    '# $$$ #',
    '#.$@$.#',
    '# $$$ #',
    '#. . .#',
    '#######'
]).

main :-
    level(Rows),
    from_rows(Rows, State),
    writeln('sokoban_prolog — wasd 移动, z 撤销, r 重置, q 退出'),
    loop(State).

loop(State) :-
    nl,
    render_ascii(State, Text),
    write(Text),
    state_moves(State, Moves),
    state_won(State, Won),
    ( Won == true -> Flag = ' WIN!' ; Flag = '' ),
    format('moves=~w~w~n> ', [Moves, Flag]),
    flush_output,
    ( read_line_to_string(user_input, Line) ->
        ( Line == end_of_file -> true
        ; string_chars(Line, Chars),
          skip_spaces(Chars, Rest),
          ( Rest = [C|_] ->
              downcase_atom(C, Ch),
              handle(Ch, State, State2, Quit),
              ( Quit == true -> true
              ; ( state_won(State2, true) -> writeln('Level clear!') ; true ),
                loop(State2)
              )
          ; loop(State)
          )
        )
    ; true
    ).

skip_spaces([' '|T], R) :- !, skip_spaces(T, R).
skip_spaces(R, R).

handle(w, S, S2, false) :- try_move(S, 0, -1, S2), !.
handle(s, S, S2, false) :- try_move(S, 0, 1, S2), !.
handle(a, S, S2, false) :- try_move(S, -1, 0, S2), !.
handle(d, S, S2, false) :- try_move(S, 1, 0, S2), !.
handle(z, S, S2, false) :- undo(S, S2), !.
handle(r, _, S2, false) :- level(Rows), from_rows(Rows, S2), !.
handle(q, S, S, true) :- !.
handle(_, S, S, false).

:- initialization(main, main).
