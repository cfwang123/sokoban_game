%% erlangapp1 — Erlang 推箱子终端版（教学）
%% 编译: erlc game.erl main.erl
%% 运行: erl -noshell -s main start -s init stop
-module(main).
-export([start/0]).

level() ->
    ["#######",
     "#. . .#",
     "# $$$ #",
     "#.$@$.#",
     "# $$$ #",
     "#. . .#",
     "#######"].

start() ->
    State = game:from_rows(level()),
    io:format("sokoban_erlang — wasd 移动, z 撤销, r 重置, q 退出~n"),
    loop(State).

loop(State) ->
    io:format("~n~s", [game:render_ascii(State)]),
    Flag = case game:won(State) of true -> " WIN!"; false -> "" end,
    io:format("moves=~p~s~n> ", [game:moves(State), Flag]),
    case io:get_line("") of
        eof -> ok;
        {error, _} -> ok;
        Line ->
            case string:trim(Line) of
                [] -> loop(State);
                [C|_] ->
                    Ch = string:to_lower([C]),
                    case Ch of
                        "q" -> ok;
                        _ ->
                            State2 = handle(Ch, State),
                            case game:won(State2) of
                                true -> io:format("Level clear!~n");
                                false -> ok
                            end,
                            loop(State2)
                    end
            end
    end.

handle("w", S) -> game:try_move(S, 0, -1);
handle("s", S) -> game:try_move(S, 0, 1);
handle("a", S) -> game:try_move(S, -1, 0);
handle("d", S) -> game:try_move(S, 1, 0);
handle("z", S) -> game:undo(S);
handle("r", _) -> game:from_rows(level());
handle(_, S) -> S.
