// fsharpapp1 — F# 推箱子终端版（教学）
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
