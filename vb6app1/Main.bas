Attribute VB_Name = "Main"
' vb6app1 — Visual Basic 6.0 推箱子（教学）
' 工程属性 → 启动对象 → Sub Main
' 交互：InputBox 输入 wasd/z/r/q（与 vbaapp1 一致，无需窗体）

Option Explicit

Public Sub Main()
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

    MsgBox "sokoban_vb6 — wasd 移动, z 撤销, r 重置, q 退出" & vbCrLf & vbCrLf & _
           "在随后的输入框中输入命令。", vbInformation, "Sokoban VB6"

    Do
        flag = ""
        If state.Won Then flag = " WIN!"
        msg = RenderAscii(state) & _
              "moves=" & CStr(state.Moves) & flag & vbCrLf & vbCrLf & _
              "w/a/s/d 移动, z 撤销, r 重置, q 退出"
        line = InputBox(msg, "Sokoban VB6")
        ' 点取消：InputBox 返回空串且用户取消时 StrPtr=0（VB6）
        If StrPtr(line) = 0 Then Exit Do
        line = Trim$(line)
        If Len(line) = 0 Then GoTo ContinueLoop
        ch = LCase$(Left$(line, 1))
        Select Case ch
            Case "w"
                Call TryMove(state, 0, -1)
            Case "s"
                Call TryMove(state, 0, 1)
            Case "a"
                Call TryMove(state, -1, 0)
            Case "d"
                Call TryMove(state, 1, 0)
            Case "z"
                Call UndoMove(state)
            Case "r"
                state = FromRows(level)
            Case "q"
                Exit Do
        End Select
        If state.Won Then
            MsgBox "Level clear!" & vbCrLf & vbCrLf & RenderAscii(state), _
                   vbInformation, "Sokoban VB6"
        End If
ContinueLoop:
    Loop
End Sub
