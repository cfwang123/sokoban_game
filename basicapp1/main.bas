/' basicapp1 — FreeBASIC 推箱子终端版（教学）
   编译: fbc main.bas
   运行: ./main  或 main.exe '/

#include "game.bas"

Dim Shared level(0 To 6) As String
Dim Shared state As GameState
Dim line As String
Dim ch As String
Dim flag As String

level(0) = "#######"
level(1) = "#. . .#"
level(2) = "# $$$ #"
level(3) = "#.$@$.#"
level(4) = "# $$$ #"
level(5) = "#. . .#"
level(6) = "#######"

FromRows(level(), 7, state)
Print "sokoban_basic — wasd 移动, z 撤销, r 重置, q 退出"

Do
    Print
    RenderAscii(state)
    If state.won Then
        flag = " WIN!"
    Else
        flag = ""
    End If
    Print "moves="; state.moves; flag
    Input "> ", line
    If Len(line) = 0 Then Continue Do
    ch = LCase(Left(line, 1))
    Select Case ch
    Case "w"
        TryMove(state, 0, -1)
    Case "s"
        TryMove(state, 0, 1)
    Case "a"
        TryMove(state, -1, 0)
    Case "d"
        TryMove(state, 1, 0)
    Case "z"
        Undo(state)
    Case "r"
        FromRows(level(), 7, state)
    Case "q"
        Exit Do
    End Select
    If state.won Then Print "Level clear!"
Loop
