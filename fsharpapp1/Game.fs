// 推箱子核心逻辑（F# 教学）
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
