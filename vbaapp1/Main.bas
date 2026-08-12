Attribute VB_Name = "Main"
' vbaapp1 — VBA 推箱子（教学）
' 在 Excel：开发工具 → Visual Basic → 导入 Game.bas + Main.bas
' 然后运行宏 SokobanMain（Alt+F8）
'
' 交互：InputBox 输入 wasd/z/r/q；地图用 MsgBox 显示
' （也可把 RenderAscii 写到工作表单元格，见 readme）

Option Explicit

Public Sub SokobanMain()
    Dim level(0 To 6) As String
    Dim state As GameState
    Dim line As String
    Dim ch As String
    Dim flag As String
    Dim msg As String

    level(0) = "#######"
    level(1) = "#. . .#"
    level(2) = "# $$$ #"
    level(3) = "#.$@$.#"
    level(4) = "# $$$ #"
    level(5) = "#. . .#"
    level(6) = "#######"

    state = FromRows(level)
    MsgBox "sokoban_vba — wasd 移动, z 撤销, r 重置, q 退出", vbInformation, "Sokoban VBA"

    Do
        flag = ""
        If state.Won Then flag = " WIN!"
        msg = RenderAscii(state) & "moves=" & CStr(state.Moves) & flag & vbCrLf & vbCrLf & _
              "输入 w/a/s/d 移动, z 撤销, r 重置, q 退出"
        line = InputBox(msg, "Sokoban VBA")
        If line = "" Then
            ' 用户点取消
            Exit Do
        End If
        line = Trim$(line)
        If Len(line) = 0 Then GoTo ContinueLoop
        ch = LCase$(Left$(line, 1))
        Select Case ch
            Case "w": Call TryMove(state, 0, -1)
            Case "s": Call TryMove(state, 0, 1)
            Case "a": Call TryMove(state, -1, 0)
            Case "d": Call TryMove(state, 1, 0)
            Case "z": Call UndoMove(state)
            Case "r": state = FromRows(level)
            Case "q": Exit Do
        End Select
        If state.Won Then
            MsgBox "Level clear!" & vbCrLf & vbCrLf & RenderAscii(state), vbInformation, "Sokoban VBA"
        End If
ContinueLoop:
    Loop
End Sub

' 可选：把当前局面写到活动表 A1 起
Public Sub DrawToSheet(ByRef s As GameState)
    Dim y As Long, x As Long, k As String
    Dim ws As Object
    On Error Resume Next
    Set ws = Application.ActiveSheet
    If ws Is Nothing Then Exit Sub
    On Error GoTo 0
    ws.Cells.Clear
    For y = 0 To s.Height - 1
        For x = 0 To s.Width - 1
            k = CellKey(x, y)
            If s.Px = x And s.Py = y Then
                If s.Goals.Exists(k) Then
                    ws.Cells(y + 1, x + 1).Value = "+"
                Else
                    ws.Cells(y + 1, x + 1).Value = "@"
                End If
            ElseIf s.Boxes.Exists(k) Then
                If s.Goals.Exists(k) Then
                    ws.Cells(y + 1, x + 1).Value = "*"
                Else
                    ws.Cells(y + 1, x + 1).Value = "$"
                End If
            ElseIf s.Walls.Exists(k) Then
                ws.Cells(y + 1, x + 1).Value = "#"
            ElseIf s.Goals.Exists(k) Then
                ws.Cells(y + 1, x + 1).Value = "."
            Else
                ws.Cells(y + 1, x + 1).Value = ""
            End If
        Next x
    Next y
    ws.Cells(s.Height + 2, 1).Value = "moves=" & CStr(s.Moves) & IIf(s.Won, " WIN!", "")
End Sub
