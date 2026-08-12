#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate remaining multi-language Sokoban teaching CLIs (batch B)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print("wrote", rel)


def changelog(lang: str) -> str:
    return f"""# Changelog

## 1.0.0 — 2026-08-10

- 初版 {lang} 核心逻辑 + 终端 main
"""


def readme(title: str, need: str, run: str) -> str:
    return f"""# {title}

{need}

```bash
{run}
```

键位：WASD 移动，z 撤销，r 重置，q 退出。
"""


def gen_ocaml() -> None:
    write(
        "ocamlapp1/game.ml",
        r"""(* 推箱子核心逻辑（OCaml 教学） *)

module S = Set.Make(String)

type hist = {
  px : int; py : int;
  box_from : string option;
  box_to : string option;
}

type state = {
  walls : S.t; goals : S.t; boxes : S.t;
  px : int; py : int;
  moves : int; won : bool;
  width : int; height : int;
  hist : hist list;
}

let key x y = Printf.sprintf "%d,%d" x y

let from_rows rows =
  let walls = ref S.empty and goals = ref S.empty and boxes = ref S.empty in
  let px = ref 0 and py = ref 0 and max_x = ref 0 and max_y = ref 0 in
  List.iteri (fun y row ->
    max_y := y;
    String.iteri (fun x ch ->
      if x > !max_x then max_x := x;
      let k = key x y in
      match ch with
      | '#' -> walls := S.add k !walls
      | '.' -> goals := S.add k !goals
      | '$' -> boxes := S.add k !boxes
      | '*' -> boxes := S.add k !boxes; goals := S.add k !goals
      | '@' -> px := x; py := y
      | '+' -> px := x; py := y; goals := S.add k !goals
      | _ -> ()
    ) row
  ) rows;
  {
    walls = !walls; goals = !goals; boxes = !boxes;
    px = !px; py = !py; moves = 0; won = false;
    width = !max_x + 1; height = !max_y + 1; hist = [];
  }

let check_win boxes goals =
  S.for_all (fun b -> S.mem b goals) boxes

let try_move s dx dy =
  if s.won then s else
  let nx = s.px + dx and ny = s.py + dy in
  let nk = key nx ny in
  if S.mem nk s.walls then s
  else if S.mem nk s.boxes then
    let bx = nx + dx and by = ny + dy in
    let bk = key bx by in
    if S.mem bk s.walls || S.mem bk s.boxes then s
    else
      let boxes = S.add bk (S.remove nk s.boxes) in
      { s with
        boxes; px = nx; py = ny; moves = s.moves + 1;
        won = check_win boxes s.goals;
        hist = { px = s.px; py = s.py; box_from = Some nk; box_to = Some bk } :: s.hist }
  else
    { s with px = nx; py = ny;
      hist = { px = s.px; py = s.py; box_from = None; box_to = None } :: s.hist }

let rec undo s =
  if s.won || s.hist = [] then s
  else
    match s.hist with
    | [] -> s
    | h :: rest ->
      match h.box_from with
      | None ->
          undo { s with px = h.px; py = h.py; hist = rest }
      | Some bf ->
          let bt = Option.value h.box_to ~default:bf in
          let boxes = S.add bf (S.remove bt s.boxes) in
          { s with
            boxes; px = h.px; py = h.py;
            moves = max 0 (s.moves - 1); won = false; hist = rest }

let render_ascii s =
  let buf = Buffer.create 128 in
  for y = 0 to s.height - 1 do
    for x = 0 to s.width - 1 do
      let k = key x y in
      let ch =
        if s.px = x && s.py = y then
          if S.mem k s.goals then '+' else '@'
        else if S.mem k s.boxes then
          if S.mem k s.goals then '*' else '$'
        else if S.mem k s.walls then '#'
        else if S.mem k s.goals then '.'
        else ' '
      in
      Buffer.add_char buf ch
    done;
    Buffer.add_char buf '\n'
  done;
  Buffer.contents buf
""",
    )
    write(
        "ocamlapp1/main.ml",
        r"""(* ocamlapp1 — OCaml 推箱子终端版（教学）
   编译: ocamlc -o sokoban game.ml main.ml
   或: ocamlopt -o sokoban game.ml main.ml *)

let level = [
  "#######";
  "#. . .#";
  "# $$$ #";
  "#.$@$.#";
  "# $$$ #";
  "#. . .#";
  "#######";
]

let () =
  let state = ref (Game.from_rows level) in
  print_endline "sokoban_ocaml — wasd 移动, z 撤销, r 重置, q 退出";
  let rec loop () =
    print_newline ();
    print_string (Game.render_ascii !state);
    let flag = if !state.Game.won then " WIN!" else "" in
    Printf.printf "moves=%d%s\n> %!" !state.Game.moves flag;
    match try Some (input_line stdin) with End_of_file -> None with
    | None -> ()
    | Some line ->
      let line = String.trim line in
      if line = "" then loop ()
      else
        let ch = Char.lowercase_ascii line.[0] in
        begin match ch with
        | 'w' -> state := Game.try_move !state 0 (-1)
        | 's' -> state := Game.try_move !state 0 1
        | 'a' -> state := Game.try_move !state (-1) 0
        | 'd' -> state := Game.try_move !state 1 0
        | 'z' -> state := Game.undo !state
        | 'r' -> state := Game.from_rows level
        | 'q' -> raise Exit
        | _ -> ()
        end;
        if !state.Game.won then print_endline "Level clear!";
        loop ()
  in
  try loop () with Exit -> ()
""",
    )
    write(
        "ocamlapp1/readme.md",
        readme(
            "ocamlapp1 — OCaml 推箱子（教学）",
            "需要 [OCaml](https://ocaml.org/)（`ocamlc` / `ocamlopt`）。",
            "cd ocamlapp1\nocamlc -o sokoban game.ml main.ml\n./sokoban",
        ),
    )
    write("ocamlapp1/CHANGELOG.md", changelog("OCaml"))


def gen_clojure() -> None:
    write(
        "clojureapp1/game.clj",
        r""";; 推箱子核心逻辑（Clojure 教学）
(ns game)

(defn cell-key [x y] (str x "," y))

(defn from-rows
  ([rows] (from-rows rows 0))
  ([rows _index]
   (let [parsed
         (reduce
          (fn [acc [y row]]
            (reduce
             (fn [a [x ch]]
               (let [k (cell-key x y)]
                 (case ch
                   \# (update a :walls conj k)
                   \. (update a :goals conj k)
                   \$ (update a :boxes conj k)
                   \* (-> a (update :boxes conj k) (update :goals conj k))
                   \@ (assoc a :px x :py y)
                   \+ (-> a (assoc :px x :py y) (update :goals conj k))
                   a)))
             (assoc acc :max-y y :max-x (max (:max-x acc 0) (dec (count row))))
             (map-indexed vector row)))
          {:walls #{} :goals #{} :boxes #{} :px 0 :py 0 :max-x 0 :max-y 0}
          (map-indexed vector rows))]
     {:walls (:walls parsed)
      :goals (:goals parsed)
      :boxes (:boxes parsed)
      :px (:px parsed)
      :py (:py parsed)
      :moves 0
      :won false
      :width (inc (:max-x parsed))
      :height (inc (:max-y parsed))
      :hist []})))

(defn check-win [boxes goals]
  (every? #(contains? goals %) boxes))

(defn try-move [s dx dy]
  (if (:won s)
    s
    (let [px (:px s) py (:py s)
          nx (+ px dx) ny (+ py dy)
          nk (cell-key nx ny)]
      (cond
        (contains? (:walls s) nk) s
        (contains? (:boxes s) nk)
        (let [bx (+ nx dx) by (+ ny dy) bk (cell-key bx by)]
          (if (or (contains? (:walls s) bk) (contains? (:boxes s) bk))
            s
            (let [boxes (-> (:boxes s) (disj nk) (conj bk))]
              (assoc s
                     :boxes boxes
                     :px nx :py ny
                     :moves (inc (:moves s))
                     :won (check-win boxes (:goals s))
                     :hist (conj (:hist s) {:px px :py py :box-from nk :box-to bk})))))
        :else
        (assoc s :px nx :py ny
               :hist (conj (:hist s) {:px px :py py :box-from nil :box-to nil}))))))

(defn undo [s]
  (if (or (:won s) (empty? (:hist s)))
    s
    (loop [hist (:hist s)
           px (:px s) py (:py s)
           boxes (:boxes s)
           moves (:moves s)]
      (if (empty? hist)
        (assoc s :px px :py py :boxes boxes :moves moves :won false :hist [])
        (let [e (peek hist)
              rest (pop hist)]
          (if (:box-from e)
            (assoc s
                   :px (:px e) :py (:py e)
                   :boxes (-> boxes (disj (:box-to e)) (conj (:box-from e)))
                   :moves (max 0 (dec moves))
                   :won false
                   :hist rest)
            (recur rest (:px e) (:py e) boxes moves)))))))

(defn render-ascii [s]
  (let [sb (StringBuilder.)]
    (doseq [y (range (:height s))
            x (range (:width s))]
      (let [k (cell-key x y)
            ch (cond
                 (and (= x (:px s)) (= y (:py s)))
                 (if (contains? (:goals s) k) \+ \@)
                 (contains? (:boxes s) k)
                 (if (contains? (:goals s) k) \* \$)
                 (contains? (:walls s) k) \#
                 (contains? (:goals s) k) \.
                 :else \space)]
        (.append sb ch)
        (when (= x (dec (:width s))) (.append sb \newline))))
    (str sb)))
""",
    )
    write(
        "clojureapp1/main.clj",
        r""";; clojureapp1 — Clojure 推箱子终端版（教学）
;; 运行: clojure -M main.clj
;; 或: clj -M main.clj

(load-file (str (.getParent (java.io.File. *file*)) "/game.clj"))
(require '[game :as g])

(def level
  ["#######"
   "#. . .#"
   "# $$$ #"
   "#.$@$.#"
   "# $$$ #"
   "#. . .#"
   "#######"])

(defn -main []
  (println "sokoban_clojure — wasd 移动, z 撤销, r 重置, q 退出")
  (loop [state (g/from-rows level 0)]
    (println)
    (print (g/render-ascii state))
    (print (str "moves=" (:moves state) (when (:won state) " WIN!") "\n> "))
    (flush)
    (let [line (read-line)]
      (if (nil? line)
        nil
        (let [line (clojure.string/trim line)]
          (if (empty? line)
            (recur state)
            (let [ch (Character/toLowerCase (first line))
                  state2 (case ch
                           \w (g/try-move state 0 -1)
                           \s (g/try-move state 0 1)
                           \a (g/try-move state -1 0)
                           \d (g/try-move state 1 0)
                           \z (g/undo state)
                           \r (g/from-rows level 0)
                           \q :quit
                           state)]
              (if (= state2 :quit)
                nil
                (do
                  (when (:won state2) (println "Level clear!"))
                  (recur state2))))))))))

(-main)
""",
    )
    write(
        "clojureapp1/readme.md",
        readme(
            "clojureapp1 — Clojure 推箱子（教学）",
            "需要 [Clojure CLI](https://clojure.org/)（`clj` / `clojure`）。",
            "cd clojureapp1\nclj -M main.clj",
        ),
    )
    write("clojureapp1/CHANGELOG.md", changelog("Clojure"))


def gen_fsharp() -> None:
    write(
        "fsharpapp1/Game.fs",
        r"""// 推箱子核心逻辑（F# 教学）
module Game

open System.Collections.Generic

type Hist = { Px: int; Py: int; BoxFrom: string option; BoxTo: string option }

type GameState = {
    Walls: HashSet<string>
    Goals: HashSet<string>
    Boxes: HashSet<string>
    mutable Px: int
    mutable Py: int
    mutable Moves: int
    mutable Won: bool
    Width: int
    Height: int
    Hist: ResizeArray<Hist>
}

let key x y = sprintf "%d,%d" x y

let fromRows (rows: string list) =
    let walls = HashSet<string>()
    let goals = HashSet<string>()
    let boxes = HashSet<string>()
    let mutable px, py, maxX, maxY = 0, 0, 0, 0
    rows |> List.iteri (fun y row ->
        maxY <- y
        row |> Seq.iteri (fun x ch ->
            if x > maxX then maxX <- x
            let k = key x y
            match ch with
            | '#' -> walls.Add k |> ignore
            | '.' -> goals.Add k |> ignore
            | '$' -> boxes.Add k |> ignore
            | '*' -> boxes.Add k |> ignore; goals.Add k |> ignore
            | '@' -> px <- x; py <- y
            | '+' -> px <- x; py <- y; goals.Add k |> ignore
            | _ -> ()
        )
    )
    {
        Walls = walls; Goals = goals; Boxes = boxes
        Px = px; Py = py; Moves = 0; Won = false
        Width = maxX + 1; Height = maxY + 1
        Hist = ResizeArray()
    }

let checkWin (s: GameState) =
    s.Won <- s.Boxes |> Seq.forall s.Goals.Contains

let tryMove (s: GameState) dx dy =
    if s.Won then false
    else
        let nx, ny = s.Px + dx, s.Py + dy
        let nk = key nx ny
        if s.Walls.Contains nk then false
        elif s.Boxes.Contains nk then
            let bx, by = nx + dx, ny + dy
            let bk = key bx by
            if s.Walls.Contains bk || s.Boxes.Contains bk then false
            else
                s.Hist.Add { Px = s.Px; Py = s.Py; BoxFrom = Some nk; BoxTo = Some bk }
                s.Boxes.Remove nk |> ignore
                s.Boxes.Add bk |> ignore
                s.Px <- nx; s.Py <- ny
                s.Moves <- s.Moves + 1
                checkWin s
                true
        else
            s.Hist.Add { Px = s.Px; Py = s.Py; BoxFrom = None; BoxTo = None }
            s.Px <- nx; s.Py <- ny
            true

let undo (s: GameState) =
    if s.Won || s.Hist.Count = 0 then false
    else
        let mutable done' = false
        while s.Hist.Count > 0 && not done' do
            let e = s.Hist.[s.Hist.Count - 1]
            s.Hist.RemoveAt(s.Hist.Count - 1)
            match e.BoxFrom with
            | Some bf ->
                s.Px <- e.Px; s.Py <- e.Py
                s.Boxes.Remove e.BoxTo.Value |> ignore
                s.Boxes.Add bf |> ignore
                if s.Moves > 0 then s.Moves <- s.Moves - 1
                s.Won <- false
                done' <- true
            | None ->
                s.Px <- e.Px; s.Py <- e.Py
        true

let renderAscii (s: GameState) =
    let sb = System.Text.StringBuilder()
    for y in 0 .. s.Height - 1 do
        for x in 0 .. s.Width - 1 do
            let k = key x y
            if s.Px = x && s.Py = y then
                sb.Append(if s.Goals.Contains k then '+' else '@') |> ignore
            elif s.Boxes.Contains k then
                sb.Append(if s.Goals.Contains k then '*' else '$') |> ignore
            elif s.Walls.Contains k then sb.Append '#' |> ignore
            elif s.Goals.Contains k then sb.Append '.' |> ignore
            else sb.Append ' ' |> ignore
        sb.AppendLine() |> ignore
    sb.ToString()
""",
    )
    write(
        "fsharpapp1/Program.fs",
        r"""// fsharpapp1 — F# 推箱子终端版（教学）
// 运行: dotnet fsi Program.fs
// 或: dotnet run（若使用项目文件）

#if INTERACTIVE
#load "Game.fs"
#endif

open System
open Game

let level = [
    "#######"
    "#. . .#"
    "# $$$ #"
    "#.$@$.#"
    "# $$$ #"
    "#. . .#"
    "#######"
]

[<EntryPoint>]
let main _ =
    let mutable state = fromRows level
    printfn "sokoban_fsharp — wasd 移动, z 撤销, r 重置, q 退出"
    let mutable cont = true
    while cont do
        printfn ""
        printf "%s" (renderAscii state)
        let flag = if state.Won then " WIN!" else ""
        printf "moves=%d%s\n> " state.Moves flag
        let line = Console.ReadLine()
        if isNull line then cont <- false
        else
            let t = line.Trim()
            if t.Length > 0 then
                match Char.ToLowerInvariant t.[0] with
                | 'w' -> tryMove state 0 -1 |> ignore
                | 's' -> tryMove state 0 1 |> ignore
                | 'a' -> tryMove state -1 0 |> ignore
                | 'd' -> tryMove state 1 0 |> ignore
                | 'z' -> undo state |> ignore
                | 'r' -> state <- fromRows level
                | 'q' -> cont <- false
                | _ -> ()
                if state.Won then printfn "Level clear!"
    0
""",
    )
    write(
        "fsharpapp1/fsharpapp1.fsproj",
        r"""<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include="Game.fs" />
    <Compile Include="Program.fs" />
  </ItemGroup>
</Project>
""",
    )
    write(
        "fsharpapp1/readme.md",
        readme(
            "fsharpapp1 — F# 推箱子（教学）",
            "需要 .NET SDK（`dotnet`）。",
            "cd fsharpapp1\ndotnet run",
        ),
    )
    write("fsharpapp1/CHANGELOG.md", changelog("F#"))


def gen_scala() -> None:
    write(
        "scalaapp1/Game.scala",
        r"""// 推箱子核心逻辑（Scala 教学）
import scala.collection.mutable

case class Hist(px: Int, py: Int, boxFrom: Option[String] = None, boxTo: Option[String] = None)

class GameState {
  val walls = mutable.Set.empty[String]
  val goals = mutable.Set.empty[String]
  val boxes = mutable.Set.empty[String]
  var px = 0
  var py = 0
  var moves = 0
  var won = false
  var width = 0
  var height = 0
  val hist = mutable.ArrayBuffer.empty[Hist]

  def checkWin(): Unit =
    won = boxes.forall(goals.contains)

  def tryMove(dx: Int, dy: Int): Boolean = {
    if (won) return false
    val nx = px + dx
    val ny = py + dy
    val nk = GameState.key(nx, ny)
    if (walls.contains(nk)) return false
    if (boxes.contains(nk)) {
      val bx = nx + dx
      val by = ny + dy
      val bk = GameState.key(bx, by)
      if (walls.contains(bk) || boxes.contains(bk)) return false
      hist += Hist(px, py, Some(nk), Some(bk))
      boxes -= nk
      boxes += bk
      px = nx; py = ny
      moves += 1
      checkWin()
      true
    } else {
      hist += Hist(px, py)
      px = nx; py = ny
      true
    }
  }

  def undo(): Boolean = {
    if (won || hist.isEmpty) return false
    var entry: Hist = null
    while (hist.nonEmpty) {
      entry = hist.remove(hist.length - 1)
      if (entry.boxFrom.isDefined) {
        px = entry.px; py = entry.py
        boxes -= entry.boxTo.get
        boxes += entry.boxFrom.get
        if (moves > 0) moves -= 1
        won = false
        return true
      }
      px = entry.px; py = entry.py
    }
    true
  }

  def renderAscii(): String = {
    val sb = new StringBuilder
    for (y <- 0 until height; x <- 0 until width) {
      val k = GameState.key(x, y)
      if (px == x && py == y) sb += (if (goals.contains(k)) '+' else '@')
      else if (boxes.contains(k)) sb += (if (goals.contains(k)) '*' else '$')
      else if (walls.contains(k)) sb += '#'
      else if (goals.contains(k)) sb += '.'
      else sb += ' '
      if (x == width - 1) sb += '\n'
    }
    sb.toString
  }
}

object GameState {
  def key(x: Int, y: Int): String = s"$x,$y"

  def fromRows(rows: Seq[String], index: Int = 0): GameState = {
    val s = new GameState
    var maxX = 0
    var maxY = 0
    for ((row, y) <- rows.zipWithIndex) {
      maxY = y
      for ((ch, x) <- row.zipWithIndex) {
        if (x > maxX) maxX = x
        val k = key(x, y)
        ch match {
          case '#' => s.walls += k
          case '.' => s.goals += k
          case '$' => s.boxes += k
          case '*' => s.boxes += k; s.goals += k
          case '@' => s.px = x; s.py = y
          case '+' => s.px = x; s.py = y; s.goals += k
          case _ =>
        }
      }
    }
    s.width = maxX + 1
    s.height = maxY + 1
    s
  }
}
""",
    )
    write(
        "scalaapp1/Main.scala",
        r"""// scalaapp1 — Scala 推箱子终端版（教学）
// 运行: scala Main.scala
// 或: scalac Game.scala Main.scala && scala Main

object Main {
  val Level = Seq(
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######"
  )

  def main(args: Array[String]): Unit = {
    var state = GameState.fromRows(Level)
    println("sokoban_scala — wasd 移动, z 撤销, r 重置, q 退出")
    var cont = true
    while (cont) {
      println()
      print(state.renderAscii())
      val flag = if (state.won) " WIN!" else ""
      print(s"moves=${state.moves}$flag\n> ")
      val line = scala.io.StdIn.readLine()
      if (line == null) cont = false
      else {
        val t = line.trim
        if (t.nonEmpty) {
          t.head.toLower match {
            case 'w' => state.tryMove(0, -1)
            case 's' => state.tryMove(0, 1)
            case 'a' => state.tryMove(-1, 0)
            case 'd' => state.tryMove(1, 0)
            case 'z' => state.undo()
            case 'r' => state = GameState.fromRows(Level)
            case 'q' => cont = false
            case _ =>
          }
          if (state.won) println("Level clear!")
        }
      }
    }
  }
}
""",
    )
    write(
        "scalaapp1/readme.md",
        readme(
            "scalaapp1 — Scala 推箱子（教学）",
            "需要 [Scala](https://www.scala-lang.org/) 3 或 2（`scala` / `scalac`）。",
            "cd scalaapp1\nscalac Game.scala Main.scala && scala Main",
        ),
    )
    write("scalaapp1/CHANGELOG.md", changelog("Scala"))


def gen_elixir() -> None:
    write(
        "elixirapp1/game.exs",
        r"""# 推箱子核心逻辑（Elixir 教学）

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
""",
    )
    write(
        "elixirapp1/main.exs",
        r"""# elixirapp1 — Elixir 推箱子终端版（教学）
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
""",
    )
    write(
        "elixirapp1/readme.md",
        readme(
            "elixirapp1 — Elixir 推箱子（教学）",
            "需要 [Elixir](https://elixir-lang.org/)（`elixir`）。",
            "cd elixirapp1\nelixir main.exs",
        ),
    )
    write("elixirapp1/CHANGELOG.md", changelog("Elixir"))


def gen_erlang() -> None:
    write(
        "erlangapp1/game.erl",
        r"""%% 推箱子核心逻辑（Erlang 教学）
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
""",
    )
    write(
        "erlangapp1/main.erl",
        r"""%% erlangapp1 — Erlang 推箱子终端版（教学）
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
""",
    )
    write(
        "erlangapp1/readme.md",
        readme(
            "erlangapp1 — Erlang 推箱子（教学）",
            "需要 [Erlang/OTP](https://www.erlang.org/)（`erlc` / `erl`）。",
            "cd erlangapp1\nerlc game.erl main.erl\nerl -noshell -s main start -s init stop",
        ),
    )
    write("erlangapp1/CHANGELOG.md", changelog("Erlang"))


def gen_crystal() -> None:
    write(
        "crystalapp1/game.cr",
        r"""# 推箱子核心逻辑（Crystal 教学）

class Hist
  property px : Int32, py : Int32
  property box_from : String?
  property box_to : String?

  def initialize(@px, @py, @box_from = nil, @box_to = nil)
  end
end

class GameState
  property walls : Set(String)
  property goals : Set(String)
  property boxes : Set(String)
  property px : Int32
  property py : Int32
  property moves : Int32
  property won : Bool
  property width : Int32
  property height : Int32
  property hist : Array(Hist)

  def initialize
    @walls = Set(String).new
    @goals = Set(String).new
    @boxes = Set(String).new
    @px = 0
    @py = 0
    @moves = 0
    @won = false
    @width = 0
    @height = 0
    @hist = [] of Hist
  end

  def self.key(x : Int32, y : Int32) : String
    "#{x},#{y}"
  end

  def self.from_rows(rows : Array(String), index = 0) : GameState
    s = GameState.new
    max_x = 0
    max_y = 0
    rows.each_with_index do |row, y|
      max_y = y
      row.each_char.with_index do |ch, x|
        max_x = x if x > max_x
        k = key(x, y)
        case ch
        when '#' then s.walls << k
        when '.' then s.goals << k
        when '$' then s.boxes << k
        when '*'
          s.boxes << k
          s.goals << k
        when '@'
          s.px = x
          s.py = y
        when '+'
          s.px = x
          s.py = y
          s.goals << k
        end
      end
    end
    s.width = max_x + 1
    s.height = max_y + 1
    s
  end

  def check_win
    @won = @boxes.all? { |b| @goals.includes?(b) }
  end

  def try_move(dx : Int32, dy : Int32) : Bool
    return false if @won
    nx = @px + dx
    ny = @py + dy
    nk = self.class.key(nx, ny)
    return false if @walls.includes?(nk)
    if @boxes.includes?(nk)
      bx = nx + dx
      by = ny + dy
      bk = self.class.key(bx, by)
      return false if @walls.includes?(bk) || @boxes.includes?(bk)
      @hist << Hist.new(@px, @py, nk, bk)
      @boxes.delete(nk)
      @boxes << bk
      @px = nx
      @py = ny
      @moves += 1
      check_win
      return true
    end
    @hist << Hist.new(@px, @py)
    @px = nx
    @py = ny
    true
  end

  def undo : Bool
    return false if @won || @hist.empty?
    while !@hist.empty?
      e = @hist.pop
      if bf = e.box_from
        @px = e.px
        @py = e.py
        @boxes.delete(e.box_to.not_nil!)
        @boxes << bf
        @moves -= 1 if @moves > 0
        @won = false
        return true
      end
      @px = e.px
      @py = e.py
    end
    true
  end

  def render_ascii : String
    String.build do |io|
      @height.times do |y|
        @width.times do |x|
          k = self.class.key(x, y)
          if @px == x && @py == y
            io << (@goals.includes?(k) ? '+' : '@')
          elsif @boxes.includes?(k)
            io << (@goals.includes?(k) ? '*' : '$')
          elsif @walls.includes?(k)
            io << '#'
          elsif @goals.includes?(k)
            io << '.'
          else
            io << ' '
          end
        end
        io << '\n'
      end
    end
  end
end
""",
    )
    write(
        "crystalapp1/main.cr",
        r"""# crystalapp1 — Crystal 推箱子终端版（教学）
# 编译: crystal build main.cr -o sokoban

require "./game"

LEVEL = [
  "#######",
  "#. . .#",
  "# $$$ #",
  "#.$@$.#",
  "# $$$ #",
  "#. . .#",
  "#######",
]

state = GameState.from_rows(LEVEL, 0)
puts "sokoban_crystal — wasd 移动, z 撤销, r 重置, q 退出"

loop do
  puts
  print state.render_ascii
  flag = state.won ? " WIN!" : ""
  print "moves=#{state.moves}#{flag}\n> "
  line = gets
  break if line.nil?
  line = line.strip
  next if line.empty?
  ch = line[0].downcase
  case ch
  when 'w' then state.try_move(0, -1)
  when 's' then state.try_move(0, 1)
  when 'a' then state.try_move(-1, 0)
  when 'd' then state.try_move(1, 0)
  when 'z' then state.undo
  when 'r' then state = GameState.from_rows(LEVEL, 0)
  when 'q' then break
  end
  puts "Level clear!" if state.won
end
""",
    )
    write(
        "crystalapp1/readme.md",
        readme(
            "crystalapp1 — Crystal 推箱子（教学）",
            "需要 [Crystal](https://crystal-lang.org/)（`crystal`）。",
            "cd crystalapp1\ncrystal run main.cr",
        ),
    )
    write("crystalapp1/CHANGELOG.md", changelog("Crystal"))


def gen_dlang() -> None:
    write(
        "dlangapp1/game.d",
        r"""// 推箱子核心逻辑（D 教学）
module game;

import std.algorithm;
import std.array;
import std.conv;
import std.string;

struct Hist {
    int px, py;
    string boxFrom, boxTo;
    bool isPush;
}

struct GameState {
    bool[string] walls, goals, boxes;
    int px, py;
    int moves;
    bool won;
    int width, height;
    Hist[] hist;
}

string key(int x, int y) { return text(x, ",", y); }

GameState fromRows(string[] rows, int index = 0) {
    GameState s;
    int maxX = 0, maxY = 0;
    foreach (y, row; rows) {
        maxY = cast(int)y;
        foreach (x, ch; row) {
            if (cast(int)x > maxX) maxX = cast(int)x;
            auto k = key(cast(int)x, cast(int)y);
            switch (ch) {
            case '#': s.walls[k] = true; break;
            case '.': s.goals[k] = true; break;
            case '$': s.boxes[k] = true; break;
            case '*': s.boxes[k] = true; s.goals[k] = true; break;
            case '@': s.px = cast(int)x; s.py = cast(int)y; break;
            case '+': s.px = cast(int)x; s.py = cast(int)y; s.goals[k] = true; break;
            default: break;
            }
        }
    }
    s.width = maxX + 1;
    s.height = maxY + 1;
    return s;
}

void checkWin(ref GameState s) {
    foreach (b, _; s.boxes) {
        if (b !in s.goals) { s.won = false; return; }
    }
    s.won = true;
}

bool tryMove(ref GameState s, int dx, int dy) {
    if (s.won) return false;
    int nx = s.px + dx, ny = s.py + dy;
    auto nk = key(nx, ny);
    if (nk in s.walls) return false;
    if (nk in s.boxes) {
        int bx = nx + dx, by = ny + dy;
        auto bk = key(bx, by);
        if (bk in s.walls || bk in s.boxes) return false;
        s.hist ~= Hist(s.px, s.py, nk, bk, true);
        s.boxes.remove(nk);
        s.boxes[bk] = true;
        s.px = nx; s.py = ny;
        s.moves++;
        checkWin(s);
        return true;
    }
    s.hist ~= Hist(s.px, s.py, "", "", false);
    s.px = nx; s.py = ny;
    return true;
}

bool undo(ref GameState s) {
    if (s.won || s.hist.length == 0) return false;
    while (s.hist.length > 0) {
        auto e = s.hist[$ - 1];
        s.hist = s.hist[0 .. $ - 1];
        if (e.isPush) {
            s.px = e.px; s.py = e.py;
            s.boxes.remove(e.boxTo);
            s.boxes[e.boxFrom] = true;
            if (s.moves > 0) s.moves--;
            s.won = false;
            return true;
        }
        s.px = e.px; s.py = e.py;
    }
    return true;
}

string renderAscii(const ref GameState s) {
    auto app = appender!string();
    foreach (y; 0 .. s.height) {
        foreach (x; 0 .. s.width) {
            auto k = key(x, y);
            if (s.px == x && s.py == y) app.put(k in s.goals ? '+' : '@');
            else if (k in s.boxes) app.put(k in s.goals ? '*' : '$');
            else if (k in s.walls) app.put('#');
            else if (k in s.goals) app.put('.');
            else app.put(' ');
        }
        app.put('\n');
    }
    return app.data;
}
""",
    )
    write(
        "dlangapp1/main.d",
        r"""// dlangapp1 — D 推箱子终端版（教学）
// 编译: dmd -O main.d game.d -of=sokoban
// 或: ldc2 -O main.d game.d -of sokoban
import std.stdio;
import std.string;
import std.uni;
import game;

void main() {
    immutable level = [
        "#######",
        "#. . .#",
        "# $$$ #",
        "#.$@$.#",
        "# $$$ #",
        "#. . .#",
        "#######",
    ];
    auto state = fromRows(level.dup, 0);
    writeln("sokoban_d — wasd 移动, z 撤销, r 重置, q 退出");
    while (true) {
        writeln();
        write(renderAscii(state));
        auto flag = state.won ? " WIN!" : "";
        writef("moves=%s%s\n> ", state.moves, flag);
        auto line = readln();
        if (line is null) break;
        line = line.strip;
        if (line.length == 0) continue;
        auto ch = line[0].toLower;
        if (ch == 'w') tryMove(state, 0, -1);
        else if (ch == 's') tryMove(state, 0, 1);
        else if (ch == 'a') tryMove(state, -1, 0);
        else if (ch == 'd') tryMove(state, 1, 0);
        else if (ch == 'z') undo(state);
        else if (ch == 'r') state = fromRows(level.dup, 0);
        else if (ch == 'q') break;
        if (state.won) writeln("Level clear!");
    }
}
""",
    )
    write(
        "dlangapp1/readme.md",
        readme(
            "dlangapp1 — D 推箱子（教学）",
            "需要 [DMD](https://dlang.org/) 或 LDC（`dmd` / `ldc2`）。",
            "cd dlangapp1\ndmd -O main.d game.d -of=sokoban\n./sokoban",
        ),
    )
    write("dlangapp1/CHANGELOG.md", changelog("D"))


def gen_swift() -> None:
    write(
        "swiftapp1/Game.swift",
        r"""// 推箱子核心逻辑（Swift CLI 教学）

struct Hist {
    let px: Int
    let py: Int
    let boxFrom: String?
    let boxTo: String?
}

final class GameState {
    var walls = Set<String>()
    var goals = Set<String>()
    var boxes = Set<String>()
    var px = 0
    var py = 0
    var moves = 0
    var won = false
    var width = 0
    var height = 0
    var hist: [Hist] = []

    static func key(_ x: Int, _ y: Int) -> String { "\(x),\(y)" }

    static func fromRows(_ rows: [String], index: Int = 0) -> GameState {
        let s = GameState()
        var maxX = 0, maxY = 0
        for (y, row) in rows.enumerated() {
            maxY = y
            for (x, ch) in row.enumerated() {
                if x > maxX { maxX = x }
                let k = key(x, y)
                switch ch {
                case "#": s.walls.insert(k)
                case ".": s.goals.insert(k)
                case "$": s.boxes.insert(k)
                case "*":
                    s.boxes.insert(k)
                    s.goals.insert(k)
                case "@":
                    s.px = x; s.py = y
                case "+":
                    s.px = x; s.py = y
                    s.goals.insert(k)
                default: break
                }
            }
        }
        s.width = maxX + 1
        s.height = maxY + 1
        return s
    }

    func checkWin() {
        won = boxes.allSatisfy { goals.contains($0) }
    }

    @discardableResult
    func tryMove(dx: Int, dy: Int) -> Bool {
        if won { return false }
        let nx = px + dx, ny = py + dy
        let nk = GameState.key(nx, ny)
        if walls.contains(nk) { return false }
        if boxes.contains(nk) {
            let bx = nx + dx, by = ny + dy
            let bk = GameState.key(bx, by)
            if walls.contains(bk) || boxes.contains(bk) { return false }
            hist.append(Hist(px: px, py: py, boxFrom: nk, boxTo: bk))
            boxes.remove(nk)
            boxes.insert(bk)
            px = nx; py = ny
            moves += 1
            checkWin()
            return true
        }
        hist.append(Hist(px: px, py: py, boxFrom: nil, boxTo: nil))
        px = nx; py = ny
        return true
    }

    @discardableResult
    func undo() -> Bool {
        if won || hist.isEmpty { return false }
        while !hist.isEmpty {
            let e = hist.removeLast()
            if let bf = e.boxFrom, let bt = e.boxTo {
                px = e.px; py = e.py
                boxes.remove(bt)
                boxes.insert(bf)
                if moves > 0 { moves -= 1 }
                won = false
                return true
            }
            px = e.px; py = e.py
        }
        return true
    }

    func renderAscii() -> String {
        var out = ""
        for y in 0..<height {
            for x in 0..<width {
                let k = GameState.key(x, y)
                if px == x && py == y {
                    out.append(goals.contains(k) ? "+" : "@")
                } else if boxes.contains(k) {
                    out.append(goals.contains(k) ? "*" : "$")
                } else if walls.contains(k) {
                    out.append("#")
                } else if goals.contains(k) {
                    out.append(".")
                } else {
                    out.append(" ")
                }
            }
            out.append("\n")
        }
        return out
    }
}
""",
    )
    write(
        "swiftapp1/main.swift",
        r"""// swiftapp1 — Swift 推箱子终端版（教学）
// 运行: swift main.swift
// 或: swiftc Game.swift main.swift -o sokoban && ./sokoban

let level = [
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
]

var state = GameState.fromRows(level)
print("sokoban_swift — wasd 移动, z 撤销, r 重置, q 退出")

while true {
    print()
    print(state.renderAscii(), terminator: "")
    let flag = state.won ? " WIN!" : ""
    print("moves=\(state.moves)\(flag)")
    print("> ", terminator: "")
    guard let line = readLine() else { break }
    let t = line.trimmingCharacters(in: .whitespacesAndNewlines)
    if t.isEmpty { continue }
    let ch = Character(t.prefix(1).lowercased())
    switch ch {
    case "w": state.tryMove(dx: 0, dy: -1)
    case "s": state.tryMove(dx: 0, dy: 1)
    case "a": state.tryMove(dx: -1, dy: 0)
    case "d": state.tryMove(dx: 1, dy: 0)
    case "z": state.undo()
    case "r": state = GameState.fromRows(level)
    case "q": break
    default: break
    }
    if ch == "q" { break }
    if state.won { print("Level clear!") }
}
""",
    )
    write(
        "swiftapp1/readme.md",
        readme(
            "swiftapp1 — Swift 推箱子（教学）",
            "需要 Swift toolchain（`swift` / `swiftc`）。与 `iosapp1` 的 SwiftUI 版独立，本目录为纯终端。",
            "cd swiftapp1\nswiftc Game.swift main.swift -o sokoban\n./sokoban",
        ),
    )
    write("swiftapp1/CHANGELOG.md", changelog("Swift CLI"))


def gen_awk() -> None:
    write(
        "awkapp1/sokoban.awk",
        r"""# awkapp1 — AWK 推箱子终端版（教学）
# 运行: awk -f sokoban.awk
# 需要 gawk（多维数组 / 关联数组）

BEGIN {
    level[0] = "#######"
    level[1] = "#. . .#"
    level[2] = "# $$$ #"
    level[3] = "#.$@$.#"
    level[4] = "# $$$ #"
    level[5] = "#. . .#"
    level[6] = "#######"
    nlevel = 7
    init()
    print "sokoban_awk — wasd 移动, z 撤销, r 重置, q 退出"
    while (1) {
        print ""
        render()
        flag = (won ? " WIN!" : "")
        printf "moves=%d%s\n> ", moves, flag
        if ((getline line < "/dev/stdin") <= 0) break
        gsub(/^[ \t]+|[ \t]+$/, "", line)
        if (line == "") continue
        ch = tolower(substr(line, 1, 1))
        if (ch == "w") try_move(0, -1)
        else if (ch == "s") try_move(0, 1)
        else if (ch == "a") try_move(-1, 0)
        else if (ch == "d") try_move(1, 0)
        else if (ch == "z") undo()
        else if (ch == "r") init()
        else if (ch == "q") break
        if (won) print "Level clear!"
    }
}

function key(x, y) { return x SUBSEP y }

function init(   y, x, row, ch, k) {
    delete walls; delete goals; delete boxes; delete hist_px; delete hist_py
    delete hist_bfx; delete hist_bfy; delete hist_btx; delete hist_bty; delete hist_push
    moves = 0; won = 0; hist_n = 0; width = 0; height = nlevel
    px = 0; py = 0
    for (y = 0; y < nlevel; y++) {
        row = level[y]
        if (length(row) > width) width = length(row)
        for (x = 0; x < length(row); x++) {
            ch = substr(row, x + 1, 1)
            k = key(x, y)
            if (ch == "#") walls[k] = 1
            else if (ch == ".") goals[k] = 1
            else if (ch == "$") boxes[k] = 1
            else if (ch == "*") { boxes[k] = 1; goals[k] = 1 }
            else if (ch == "@") { px = x; py = y }
            else if (ch == "+") { px = x; py = y; goals[k] = 1 }
        }
    }
}

function check_win(   b) {
    for (b in boxes) if (!(b in goals)) { won = 0; return }
    won = 1
}

function try_move(dx, dy,   nx, ny, nk, bx, by, bk) {
    if (won) return 0
    nx = px + dx; ny = py + dy
    nk = key(nx, ny)
    if (nk in walls) return 0
    if (nk in boxes) {
        bx = nx + dx; by = ny + dy
        bk = key(bx, by)
        if ((bk in walls) || (bk in boxes)) return 0
        hist_n++
        hist_px[hist_n] = px; hist_py[hist_n] = py
        hist_bfx[hist_n] = nx; hist_bfy[hist_n] = ny
        hist_btx[hist_n] = bx; hist_bty[hist_n] = by
        hist_push[hist_n] = 1
        delete boxes[nk]
        boxes[bk] = 1
        px = nx; py = ny
        moves++
        check_win()
        return 1
    }
    hist_n++
    hist_px[hist_n] = px; hist_py[hist_n] = py
    hist_push[hist_n] = 0
    px = nx; py = ny
    return 1
}

function undo(   e) {
    if (won || hist_n == 0) return 0
    while (hist_n > 0) {
        e = hist_n
        hist_n--
        if (hist_push[e]) {
            px = hist_px[e]; py = hist_py[e]
            delete boxes[key(hist_btx[e], hist_bty[e])]
            boxes[key(hist_bfx[e], hist_bfy[e])] = 1
            if (moves > 0) moves--
            won = 0
            return 1
        }
        px = hist_px[e]; py = hist_py[e]
    }
    return 1
}

function render(   y, x, k, ch) {
    for (y = 0; y < height; y++) {
        for (x = 0; x < width; x++) {
            k = key(x, y)
            if (x == px && y == py) ch = ((k in goals) ? "+" : "@")
            else if (k in boxes) ch = ((k in goals) ? "*" : "$")
            else if (k in walls) ch = "#"
            else if (k in goals) ch = "."
            else ch = " "
            printf "%s", ch
        }
        print ""
    }
}
""",
    )
    write(
        "awkapp1/readme.md",
        readme(
            "awkapp1 — AWK 推箱子（教学）",
            "需要 gawk（GNU Awk）。Windows 可用 Git Bash / MSYS 中的 `gawk`。",
            "cd awkapp1\ngawk -f sokoban.awk",
        ),
    )
    write("awkapp1/CHANGELOG.md", changelog("AWK"))


def gen_sql() -> None:
    # SQL teaching demo: pure SQL schema + sqlite driver script in Python-free shell using sqlite3 CLI
    write(
        "sqlapp1/schema.sql",
        r"""-- sqlapp1 — Sokoban state in SQLite（教学）
-- 地图格：kind in wall/goal/box/floor；玩家单独表

DROP TABLE IF EXISTS cell;
DROP TABLE IF EXISTS player;
DROP TABLE IF EXISTS meta;
DROP TABLE IF EXISTS hist;

CREATE TABLE cell (
  x INTEGER NOT NULL,
  y INTEGER NOT NULL,
  kind TEXT NOT NULL, -- wall | floor | goal | box | box_goal
  PRIMARY KEY (x, y)
);

CREATE TABLE player (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  x INTEGER NOT NULL,
  y INTEGER NOT NULL
);

CREATE TABLE meta (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  moves INTEGER NOT NULL DEFAULT 0,
  won INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE hist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  px INTEGER NOT NULL,
  py INTEGER NOT NULL,
  bfx INTEGER,
  bfy INTEGER,
  btx INTEGER,
  bty INTEGER,
  is_push INTEGER NOT NULL
);

INSERT INTO meta(id, moves, won) VALUES (1, 0, 0);
""",
    )
    write(
        "sqlapp1/init_level.sql",
        r"""-- 迷你关卡加载
DELETE FROM cell;
DELETE FROM player;
DELETE FROM hist;
UPDATE meta SET moves = 0, won = 0 WHERE id = 1;

-- #######
-- #. . .#
-- # $$$ #
-- #.$@$.#
-- # $$$ #
-- #. . .#
-- #######
WITH raw(y, row) AS (
  VALUES
    (0, '#######'),
    (1, '#. . .#'),
    (2, '# $$$ #'),
    (3, '#.$@$.#'),
    (4, '# $$$ #'),
    (5, '#. . .#'),
    (6, '#######')
),
chars AS (
  SELECT y,
         value - 1 AS x,
         substr(row, value, 1) AS ch
  FROM raw
  JOIN generate_series(1, length(row))
)
INSERT INTO cell(x, y, kind)
SELECT x, y,
  CASE ch
    WHEN '#' THEN 'wall'
    WHEN '.' THEN 'goal'
    WHEN '$' THEN 'box'
    WHEN '*' THEN 'box_goal'
    WHEN '@' THEN 'floor'
    WHEN '+' THEN 'goal'
    ELSE 'floor'
  END
FROM chars
WHERE ch != ' ';

INSERT INTO player(id, x, y)
SELECT 1, value - 1, y
FROM (
  SELECT y, row FROM (VALUES
    (0, '#######'),
    (1, '#. . .#'),
    (2, '# $$$ #'),
    (3, '#.$@$.#'),
    (4, '# $$$ #'),
    (5, '#. . .#'),
    (6, '#######')
  ) AS t(y, row)
)
JOIN generate_series(1, length(row))
WHERE substr(row, value, 1) IN ('@', '+')
LIMIT 1;
""",
    )
    write(
        "sqlapp1/main.sh",
        r"""#!/usr/bin/env bash
# sqlapp1 — SQLite 推箱子（教学驱动）
# 状态存在 DB；玩法用 SQL 更新。需要 sqlite3。
set -euo pipefail
DIR=$(cd "$(dirname "$0")" && pwd)
DB=${SOKOBAN_DB:-"$DIR/sokoban.db"}
rm -f "$DB"
sqlite3 "$DB" < "$DIR/schema.sql"
# generate_series may need SQLite 3.39+; fallback init without it if needed
if ! sqlite3 "$DB" < "$DIR/init_level.sql" 2>/dev/null; then
  sqlite3 "$DB" < "$DIR/init_level_compat.sql"
fi

render() {
  sqlite3 -batch "$DB" <<'SQL'
.mode list
SELECT group_concat(line, char(10)) FROM (
  SELECT y,
    group_concat(
      CASE
        WHEN p.x = c.x AND p.y = c.y AND c.kind IN ('goal','box_goal') THEN '+'
        WHEN p.x = c.x AND p.y = c.y THEN '@'
        WHEN c.kind = 'wall' THEN '#'
        WHEN c.kind = 'box' THEN '$'
        WHEN c.kind = 'box_goal' THEN '*'
        WHEN c.kind = 'goal' THEN '.'
        ELSE ' '
      END, ''
    ) AS line
  FROM cell c
  CROSS JOIN player p
  GROUP BY y
  ORDER BY y
);
SELECT 'moves=' || moves || CASE WHEN won THEN ' WIN!' ELSE '' END FROM meta WHERE id=1;
SQL
}

try_move() {
  local dx=$1 dy=$2
  sqlite3 "$DB" "SELECT 1;" >/dev/null
  # use a SQL file with parameters via temp
  sqlite3 "$DB" <<SQL
BEGIN;
-- block if won
SELECT CASE WHEN won=1 THEN RAISE(ABORT,'won') END FROM meta WHERE id=1;
-- compute next
WITH p AS (SELECT x,y FROM player WHERE id=1),
n AS (SELECT p.x+($dx) AS nx, p.y+($dy) AS ny FROM p),
dst AS (SELECT c.kind FROM cell c, n WHERE c.x=n.nx AND c.y=n.ny)
SELECT CASE WHEN (SELECT kind FROM dst)='wall' THEN RAISE(ABORT,'wall') END;
-- if box
WITH p AS (SELECT x,y FROM player WHERE id=1),
n AS (SELECT p.x+($dx) AS nx, p.y+($dy) AS ny FROM p),
dst AS (SELECT c.x,c.y,c.kind FROM cell c, n WHERE c.x=n.nx AND c.y=n.ny)
SELECT CASE
  WHEN kind IN ('box','box_goal') THEN (
    WITH bto AS (SELECT n.nx+($dx) AS bx, n.ny+($dy) AS by FROM n),
    beyond AS (SELECT c.kind FROM cell c, bto WHERE c.x=bto.bx AND c.y=bto.by)
    SELECT CASE WHEN (SELECT kind FROM beyond) IN ('wall','box','box_goal') THEN RAISE(ABORT,'blocked') END
  )
END FROM dst;
-- perform
WITH p AS (SELECT x AS px, y AS py FROM player WHERE id=1),
n AS (SELECT px+($dx) AS nx, py+($dy) AS ny FROM p),
dst AS (SELECT * FROM cell, n WHERE x=nx AND y=ny)
-- record hist
INSERT INTO hist(px,py,bfx,bfy,btx,bty,is_push)
SELECT p.px, p.py,
  CASE WHEN dst.kind IN ('box','box_goal') THEN dst.x END,
  CASE WHEN dst.kind IN ('box','box_goal') THEN dst.y END,
  CASE WHEN dst.kind IN ('box','box_goal') THEN dst.x+($dx) END,
  CASE WHEN dst.kind IN ('box','box_goal') THEN dst.y+($dy) END,
  CASE WHEN dst.kind IN ('box','box_goal') THEN 1 ELSE 0 END
FROM p, dst;

-- move box if needed
UPDATE cell SET kind = CASE kind WHEN 'box_goal' THEN 'goal' ELSE 'floor' END
WHERE (x,y) IN (SELECT nx,ny FROM (SELECT px+($dx) nx, py+($dy) ny FROM player WHERE id=1) t)
  AND kind IN ('box','box_goal')
  AND EXISTS (
    SELECT 1 FROM cell c2
    WHERE c2.x = (SELECT px+($dx)*2 FROM player WHERE id=1)
      AND c2.y = (SELECT py+($dy)*2 FROM player WHERE id=1)
      AND c2.kind IN ('floor','goal')
  );

UPDATE cell SET kind = CASE kind WHEN 'goal' THEN 'box_goal' ELSE 'box' END
WHERE x = (SELECT px+($dx)*2 FROM player WHERE id=1)
  AND y = (SELECT py+($dy)*2 FROM player WHERE id=1)
  AND kind IN ('floor','goal')
  AND EXISTS (
    SELECT 1 FROM cell c0
    WHERE c0.x=(SELECT px+($dx) FROM player WHERE id=1)
      AND c0.y=(SELECT py+($dy) FROM player WHERE id=1)
      -- after previous update box already moved from here; check hist instead
  );

-- simpler approach: abort this complex SQL path — handled in main.py/sh helpers
ROLLBACK;
SQL
}

echo "sokoban_sql — wasd 移动, z 撤销, r 重置, q 退出"
echo "（完整移动逻辑见 main.py / move.sql；本 shell 仅演示渲染）"
echo
echo "推荐: python -X utf8 main.py"
render
""",
    )
    write(
        "sqlapp1/main.py",
        r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sqlapp1 - SQLite sokoban teaching: state in DB."""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
DB = DIR / "sokoban.db"

LEVEL = [
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
]


def connect() -> sqlite3.Connection:
    if DB.exists():
        DB.unlink()
    conn = sqlite3.connect(DB)
    conn.executescript((DIR / "schema.sql").read_text(encoding="utf-8"))
    load_level(conn)
    return conn


def load_level(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM cell")
    conn.execute("DELETE FROM player")
    conn.execute("DELETE FROM hist")
    conn.execute("UPDATE meta SET moves=0, won=0 WHERE id=1")
    px = py = 0
    for y, row in enumerate(LEVEL):
        for x, ch in enumerate(row):
            if ch == "#":
                kind = "wall"
            elif ch == ".":
                kind = "goal"
            elif ch == "$":
                kind = "box"
            elif ch == "*":
                kind = "box_goal"
            elif ch == "@":
                kind = "floor"
                px, py = x, y
            elif ch == "+":
                kind = "goal"
                px, py = x, y
            else:
                kind = "floor"
            conn.execute("INSERT INTO cell(x,y,kind) VALUES(?,?,?)", (x, y, kind))
    conn.execute("INSERT INTO player(id,x,y) VALUES(1,?,?)", (px, py))
    conn.commit()


def kind_at(conn: sqlite3.Connection, x: int, y: int) -> str | None:
    row = conn.execute("SELECT kind FROM cell WHERE x=? AND y=?", (x, y)).fetchone()
    return row[0] if row else None


def set_kind(conn: sqlite3.Connection, x: int, y: int, kind: str) -> None:
    conn.execute("UPDATE cell SET kind=? WHERE x=? AND y=?", (kind, x, y))


def render(conn: sqlite3.Connection) -> str:
    px, py = conn.execute("SELECT x,y FROM player WHERE id=1").fetchone()
    moves, won = conn.execute("SELECT moves,won FROM meta WHERE id=1").fetchone()
    rows = conn.execute(
        "SELECT x,y,kind FROM cell ORDER BY y,x"
    ).fetchall()
    if not rows:
        return ""
    max_x = max(r[0] for r in rows)
    max_y = max(r[1] for r in rows)
    grid = {(x, y): k for x, y, k in rows}
    lines = []
    for y in range(max_y + 1):
        line = []
        for x in range(max_x + 1):
            k = grid.get((x, y), "floor")
            if x == px and y == py:
                line.append("+" if k in ("goal", "box_goal") else "@")
            elif k == "wall":
                line.append("#")
            elif k == "box":
                line.append("$")
            elif k == "box_goal":
                line.append("*")
            elif k == "goal":
                line.append(".")
            else:
                line.append(" ")
        lines.append("".join(line))
    flag = " WIN!" if won else ""
    lines.append(f"moves={moves}{flag}")
    return "\n".join(lines) + "\n"


def try_move(conn: sqlite3.Connection, dx: int, dy: int) -> bool:
    won = conn.execute("SELECT won FROM meta WHERE id=1").fetchone()[0]
    if won:
        return False
    px, py = conn.execute("SELECT x,y FROM player WHERE id=1").fetchone()
    nx, ny = px + dx, py + dy
    dk = kind_at(conn, nx, ny)
    if dk is None or dk == "wall":
        return False
    if dk in ("box", "box_goal"):
        bx, by = nx + dx, ny + dy
        bk = kind_at(conn, bx, by)
        if bk is None or bk in ("wall", "box", "box_goal"):
            return False
        conn.execute(
            "INSERT INTO hist(px,py,bfx,bfy,btx,bty,is_push) VALUES(?,?,?,?,?,?,1)",
            (px, py, nx, ny, bx, by),
        )
        set_kind(conn, nx, ny, "goal" if dk == "box_goal" else "floor")
        set_kind(conn, bx, by, "box_goal" if bk == "goal" else "box")
        conn.execute("UPDATE player SET x=?, y=? WHERE id=1", (nx, ny))
        conn.execute("UPDATE meta SET moves = moves + 1 WHERE id=1")
        # win?
        left = conn.execute(
            "SELECT COUNT(*) FROM cell WHERE kind='box'"
        ).fetchone()[0]
        if left == 0:
            conn.execute("UPDATE meta SET won=1 WHERE id=1")
        conn.commit()
        return True
    conn.execute(
        "INSERT INTO hist(px,py,bfx,bfy,btx,bty,is_push) VALUES(?,?,NULL,NULL,NULL,NULL,0)",
        (px, py),
    )
    conn.execute("UPDATE player SET x=?, y=? WHERE id=1", (nx, ny))
    conn.commit()
    return True


def undo(conn: sqlite3.Connection) -> bool:
    won = conn.execute("SELECT won FROM meta WHERE id=1").fetchone()[0]
    if won:
        return False
    while True:
        row = conn.execute(
            "SELECT id,px,py,bfx,bfy,btx,bty,is_push FROM hist ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if not row:
            return False
        hid, px, py, bfx, bfy, btx, bty, is_push = row
        conn.execute("DELETE FROM hist WHERE id=?", (hid,))
        if is_push:
            conn.execute("UPDATE player SET x=?, y=? WHERE id=1", (px, py))
            # remove box from to
            tk = kind_at(conn, btx, bty)
            set_kind(conn, btx, bty, "goal" if tk == "box_goal" else "floor")
            fk = kind_at(conn, bfx, bfy)
            set_kind(conn, bfx, bfy, "box_goal" if fk == "goal" else "box")
            conn.execute(
                "UPDATE meta SET moves = CASE WHEN moves>0 THEN moves-1 ELSE 0 END, won=0 WHERE id=1"
            )
            conn.commit()
            return True
        conn.execute("UPDATE player SET x=?, y=? WHERE id=1", (px, py))
        conn.commit()


def main() -> None:
    conn = connect()
    print("sokoban_sql — wasd 移动, z 撤销, r 重置, q 退出")
    print("(SQLite DB:", DB, ")")
    while True:
        print()
        print(render(conn), end="")
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        ch = line[0].lower()
        if ch == "w":
            try_move(conn, 0, -1)
        elif ch == "s":
            try_move(conn, 0, 1)
        elif ch == "a":
            try_move(conn, -1, 0)
        elif ch == "d":
            try_move(conn, 1, 0)
        elif ch == "z":
            undo(conn)
        elif ch == "r":
            load_level(conn)
        elif ch == "q":
            break
        won = conn.execute("SELECT won FROM meta WHERE id=1").fetchone()[0]
        if won:
            print("Level clear!")


if __name__ == "__main__":
    main()
''',
    )
    write(
        "sqlapp1/readme.md",
        readme(
            "sqlapp1 — SQL / SQLite 推箱子（教学）",
            "需要 Python 3 + 标准库 `sqlite3`（状态全部落在 SQLite 表中）。",
            "cd sqlapp1\npython -X utf8 main.py",
        ),
    )
    write("sqlapp1/CHANGELOG.md", changelog("SQL/SQLite"))


def gen_v() -> None:
    write(
        "vapp1/game.v",
        r"""// 推箱子核心逻辑（V 教学）
module main

struct Hist {
	px       int
	py       int
	box_from string
	box_to   string
	is_push  bool
}

struct GameState {
mut:
	walls  map[string]bool
	goals  map[string]bool
	boxes  map[string]bool
	px     int
	py     int
	moves  int
	won    bool
	width  int
	height int
	hist   []Hist
}

fn key(x int, y int) string {
	return '${x},${y}'
}

fn from_rows(rows []string) GameState {
	mut s := GameState{}
	mut max_x := 0
	mut max_y := 0
	for y, row in rows {
		max_y = y
		for x, ch in row {
			if x > max_x {
				max_x = x
			}
			k := key(x, y)
			match ch {
				`#` { s.walls[k] = true }
				`.` { s.goals[k] = true }
				`$` { s.boxes[k] = true }
				`*` {
					s.boxes[k] = true
					s.goals[k] = true
				}
				`@` {
					s.px = x
					s.py = y
				}
				`+` {
					s.px = x
					s.py = y
					s.goals[k] = true
				}
				else {}
			}
		}
	}
	s.width = max_x + 1
	s.height = max_y + 1
	return s
}

fn (mut s GameState) check_win() {
	s.won = true
	for b, _ in s.boxes {
		if b !in s.goals {
			s.won = false
			return
		}
	}
}

fn (mut s GameState) try_move(dx int, dy int) bool {
	if s.won {
		return false
	}
	nx := s.px + dx
	ny := s.py + dy
	nk := key(nx, ny)
	if nk in s.walls {
		return false
	}
	if nk in s.boxes {
		bx := nx + dx
		by := ny + dy
		bk := key(bx, by)
		if bk in s.walls || bk in s.boxes {
			return false
		}
		s.hist << Hist{s.px, s.py, nk, bk, true}
		s.boxes.delete(nk)
		s.boxes[bk] = true
		s.px = nx
		s.py = ny
		s.moves++
		s.check_win()
		return true
	}
	s.hist << Hist{s.px, s.py, '', '', false}
	s.px = nx
	s.py = ny
	return true
}

fn (mut s GameState) undo() bool {
	if s.won || s.hist.len == 0 {
		return false
	}
	for s.hist.len > 0 {
		e := s.hist.pop()
		if e.is_push {
			s.px = e.px
			s.py = e.py
			s.boxes.delete(e.box_to)
			s.boxes[e.box_from] = true
			if s.moves > 0 {
				s.moves--
			}
			s.won = false
			return true
		}
		s.px = e.px
		s.py = e.py
	}
	return true
}

fn (s GameState) render_ascii() string {
	mut out := ''
	for y in 0 .. s.height {
		for x in 0 .. s.width {
			k := key(x, y)
			if s.px == x && s.py == y {
				out += if k in s.goals { '+' } else { '@' }
			} else if k in s.boxes {
				out += if k in s.goals { '*' } else { '$' }
			} else if k in s.walls {
				out += '#'
			} else if k in s.goals {
				out += '.'
			} else {
				out += ' '
			}
		}
		out += '\n'
	}
	return out
}
""",
    )
    write(
        "vapp1/main.v",
        r"""// vapp1 — V 推箱子终端版（教学）
// 运行: v run .
module main

import os

const level = [
	'#######',
	'#. . .#',
	'# $$$ #',
	'#.$@$.#',
	'# $$$ #',
	'#. . .#',
	'#######',
]

fn main() {
	mut state := from_rows(level)
	println('sokoban_v — wasd 移动, z 撤销, r 重置, q 退出')
	for {
		println('')
		print(state.render_ascii())
		flag := if state.won { ' WIN!' } else { '' }
		print('moves=${state.moves}${flag}\n> ')
		line := os.input('')
		t := line.trim_space()
		if t.len == 0 {
			continue
		}
		ch := t[0].ascii_str().to_lower()
		match ch {
			'w' { state.try_move(0, -1) }
			's' { state.try_move(0, 1) }
			'a' { state.try_move(-1, 0) }
			'd' { state.try_move(1, 0) }
			'z' { state.undo() }
			'r' { state = from_rows(level) }
			'q' { break }
			else {}
		}
		if state.won {
			println('Level clear!')
		}
	}
}
""",
    )
    write(
        "vapp1/readme.md",
        readme(
            "vapp1 — V 推箱子（教学）",
            "需要 [V](https://vlang.io/)（`v`）。",
            "cd vapp1\nv run .",
        ),
    )
    write("vapp1/CHANGELOG.md", changelog("V"))


def main() -> None:
    gen_ocaml()
    gen_clojure()
    gen_fsharp()
    gen_scala()
    gen_elixir()
    gen_erlang()
    gen_crystal()
    gen_dlang()
    gen_swift()
    gen_awk()
    gen_sql()
    gen_v()
    print("done batch B")


if __name__ == "__main__":
    main()
