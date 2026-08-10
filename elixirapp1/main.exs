# elixirapp1 — Elixir 推箱子终端版（教学）
# 运行: elixir main.exs

Code.require_file("game.exs", __DIR__)

level = [
  "#######",
  "#. . .#",
  "# $$$ #",
  "#.$@$.#",
  "# $$$ #",
  "#. . .#",
  "#######"
]

state = Sokoban.Game.from_rows(level)
IO.puts("sokoban_elixir — wasd 移动, z 撤销, r 重置, q 退出")

defmodule MainLoop do
  def loop(state, level) do
    IO.puts("")
    IO.write(Sokoban.Game.render_ascii(state))
    flag = if state.won, do: " WIN!", else: ""
    IO.write("moves=#{state.moves}#{flag}\n> ")

    case IO.gets("") do
      :eof -> :ok
      nil -> :ok
      line ->
        line = String.trim(line)

        if line == "" do
          loop(state, level)
        else
          ch = line |> String.first() |> String.downcase()

          state2 =
            case ch do
              "w" -> Sokoban.Game.try_move(state, 0, -1)
              "s" -> Sokoban.Game.try_move(state, 0, 1)
              "a" -> Sokoban.Game.try_move(state, -1, 0)
              "d" -> Sokoban.Game.try_move(state, 1, 0)
              "z" -> Sokoban.Game.undo(state)
              "r" -> Sokoban.Game.from_rows(level)
              "q" -> :quit
              _ -> state
            end

          case state2 do
            :quit ->
              :ok

            s ->
              if s.won, do: IO.puts("Level clear!")
              loop(s, level)
          end
        end
    end
  end
end

MainLoop.loop(state, level)
