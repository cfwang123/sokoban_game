# 推箱子核心逻辑（Elixir 教学）

defmodule Sokoban.Game do
  defstruct walls: MapSet.new(), goals: MapSet.new(), boxes: MapSet.new(),
            px: 0, py: 0, moves: 0, won: false, width: 0, height: 0, hist: []

  def key(x, y), do: "#{x},#{y}"

  def from_rows(rows, _index \\ 0) do
    {walls, goals, boxes, px, py, max_x, max_y} =
      rows
      |> Enum.with_index()
      |> Enum.reduce({MapSet.new(), MapSet.new(), MapSet.new(), 0, 0, 0, 0}, fn {row, y}, acc ->
        row
        |> String.graphemes()
        |> Enum.with_index()
        |> Enum.reduce(acc, fn {ch, x}, {w, g, b, px, py, mx, my} ->
          mx = max(mx, x)
          my = max(my, y)
          k = key(x, y)
          case ch do
            "#" -> {MapSet.put(w, k), g, b, px, py, mx, my}
            "." -> {w, MapSet.put(g, k), b, px, py, mx, my}
            "$" -> {w, g, MapSet.put(b, k), px, py, mx, my}
            "*" -> {w, MapSet.put(g, k), MapSet.put(b, k), px, py, mx, my}
            "@" -> {w, g, b, x, y, mx, my}
            "+" -> {w, MapSet.put(g, k), b, x, y, mx, my}
            _ -> {w, g, b, px, py, mx, my}
          end
        end)
      end)

    %__MODULE__{
      walls: walls, goals: goals, boxes: boxes,
      px: px, py: py, width: max_x + 1, height: max_y + 1
    }
  end

  defp check_win(boxes, goals), do: Enum.all?(boxes, &MapSet.member?(goals, &1))

  def try_move(%{won: true} = s, _, _), do: s

  def try_move(s, dx, dy) do
    nx = s.px + dx
    ny = s.py + dy
    nk = key(nx, ny)

    cond do
      MapSet.member?(s.walls, nk) ->
        s

      MapSet.member?(s.boxes, nk) ->
        bx = nx + dx
        by = ny + dy
        bk = key(bx, by)

        if MapSet.member?(s.walls, bk) or MapSet.member?(s.boxes, bk) do
          s
        else
          boxes = s.boxes |> MapSet.delete(nk) |> MapSet.put(bk)

          %{
            s
            | boxes: boxes,
              px: nx,
              py: ny,
              moves: s.moves + 1,
              won: check_win(boxes, s.goals),
              hist: [%{px: s.px, py: s.py, bf: nk, bt: bk} | s.hist]
          }
        end

      true ->
        %{s | px: nx, py: ny, hist: [%{px: s.px, py: s.py, bf: nil, bt: nil} | s.hist]}
    end
  end

  def undo(%{won: true} = s), do: s
  def undo(%{hist: []} = s), do: s

  def undo(s), do: do_undo(s.hist, s)

  defp do_undo([], s), do: %{s | hist: [], won: false}

  defp do_undo([%{bf: nil, px: px, py: py} | rest], s),
    do: do_undo(rest, %{s | px: px, py: py, hist: rest})

  defp do_undo([%{bf: bf, bt: bt, px: px, py: py} | rest], s) when not is_nil(bf) do
    boxes = s.boxes |> MapSet.delete(bt) |> MapSet.put(bf)

    %{
      s
      | boxes: boxes,
        px: px,
        py: py,
        moves: max(0, s.moves - 1),
        won: false,
        hist: rest
    }
  end

  def render_ascii(s) do
    for y <- 0..(s.height - 1), into: "" do
      row =
        for x <- 0..(s.width - 1), into: "" do
          k = key(x, y)

          cond do
            s.px == x and s.py == y -> if(MapSet.member?(s.goals, k), do: "+", else: "@")
            MapSet.member?(s.boxes, k) -> if(MapSet.member?(s.goals, k), do: "*", else: "$")
            MapSet.member?(s.walls, k) -> "#"
            MapSet.member?(s.goals, k) -> "."
            true -> " "
          end
        end

      row <> "\n"
    end
  end
end
