' vbapp1 — Visual Basic .NET 推箱子终端版（教学）
' 运行: dotnet run

Module Program
    Sub Main()
        Dim level As String() = {
            "#######",
            "#. . .#",
            "# $$$ #",
            "#.$@$.#",
            "# $$$ #",
            "#. . .#",
            "#######"
        }

        Dim state = GameState.FromRows(level, 0)
        Console.WriteLine("sokoban_vb — wasd 移动, z 撤销, r 重置, q 退出")

        While True
            Console.WriteLine()
            Console.Write(state.RenderAscii())
            Dim flag = If(state.Won, " WIN!", "")
            Console.Write($"moves={state.Moves}{flag}{vbLf}> ")
            Dim line = Console.ReadLine()
            If line Is Nothing Then Exit While
            line = line.Trim()
            If line.Length = 0 Then Continue While
            Select Case Char.ToLowerInvariant(line(0))
                Case "w"c : state.TryMove(0, -1)
                Case "s"c : state.TryMove(0, 1)
                Case "a"c : state.TryMove(-1, 0)
                Case "d"c : state.TryMove(1, 0)
                Case "z"c : state.Undo()
                Case "r"c : state = GameState.FromRows(level, 0)
                Case "q"c : Return
            End Select
            If state.Won Then Console.WriteLine("Level clear!")
        End While
    End Sub
End Module
