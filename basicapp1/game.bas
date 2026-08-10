/' 推箱子核心逻辑（FreeBASIC 教学） '/

Const MAX_W = 32
Const MAX_H = 32
Const MAX_HIST = 1024

Type HistEntry
    px As Integer
    py As Integer
    bfx As Integer
    bfy As Integer
    btx As Integer
    bty As Integer
    isPush As Integer
End Type

Type GameState
    map(1 To MAX_W, 1 To MAX_H) As String
    width As Integer
    height As Integer
    px As Integer
    py As Integer
    moves As Integer
    won As Integer
    histN As Integer
    hist(1 To MAX_HIST) As HistEntry
End Type

Sub CheckWin(ByRef s As GameState)
    Dim As Integer x, y
    s.won = 1
    For y = 1 To s.height
        For x = 1 To s.width
            If s.map(x, y) = "$" Then
                s.won = 0
                Exit Sub
            End If
        Next
    Next
End Sub

Sub FromRows(rows() As String, n As Integer, ByRef s As GameState)
    Dim As Integer y, x, lenr
    Dim As String ch
    s.width = 0
    s.height = n
    s.px = 1
    s.py = 1
    s.moves = 0
    s.won = 0
    s.histN = 0
    For y = 1 To MAX_H
        For x = 1 To MAX_W
            s.map(x, y) = " "
        Next
    Next
    For y = 0 To n - 1
        lenr = Len(rows(y))
        If lenr > s.width Then s.width = lenr
        For x = 1 To lenr
            ch = Mid(rows(y), x, 1)
            Select Case ch
            Case "#"
                s.map(x, y + 1) = "#"
            Case "."
                s.map(x, y + 1) = "."
            Case "$"
                s.map(x, y + 1) = "$"
            Case "*"
                s.map(x, y + 1) = "*"
            Case "@"
                s.map(x, y + 1) = " "
                s.px = x
                s.py = y + 1
            Case "+"
                s.map(x, y + 1) = "."
                s.px = x
                s.py = y + 1
            Case Else
                s.map(x, y + 1) = " "
            End Select
        Next
    Next
End Sub

Function TryMove(ByRef s As GameState, dx As Integer, dy As Integer) As Integer
    Dim As Integer nx, ny, bx, by
    Dim As String ch
    TryMove = 0
    If s.won Then Exit Function
    nx = s.px + dx
    ny = s.py + dy
    If nx < 1 Or ny < 1 Or nx > s.width Or ny > s.height Then Exit Function
    ch = s.map(nx, ny)
    If ch = "#" Then Exit Function
    If ch = "$" Or ch = "*" Then
        bx = nx + dx
        by = ny + dy
        If bx < 1 Or by < 1 Or bx > s.width Or by > s.height Then Exit Function
        ch = s.map(bx, by)
        If ch = "#" Or ch = "$" Or ch = "*" Then Exit Function
        If s.histN >= MAX_HIST Then Exit Function
        s.histN += 1
        s.hist(s.histN).px = s.px
        s.hist(s.histN).py = s.py
        s.hist(s.histN).bfx = nx
        s.hist(s.histN).bfy = ny
        s.hist(s.histN).btx = bx
        s.hist(s.histN).bty = by
        s.hist(s.histN).isPush = 1
        If s.map(nx, ny) = "*" Then
            s.map(nx, ny) = "."
        Else
            s.map(nx, ny) = " "
        End If
        If s.map(bx, by) = "." Then
            s.map(bx, by) = "*"
        Else
            s.map(bx, by) = "$"
        End If
        s.px = nx
        s.py = ny
        s.moves += 1
        CheckWin(s)
        TryMove = 1
        Exit Function
    End If
    If s.histN >= MAX_HIST Then Exit Function
    s.histN += 1
    s.hist(s.histN).px = s.px
    s.hist(s.histN).py = s.py
    s.hist(s.histN).isPush = 0
    s.px = nx
    s.py = ny
    TryMove = 1
End Function

Function Undo(ByRef s As GameState) As Integer
    Dim As HistEntry h
    Dim As Integer nx, ny, bx, by
    Undo = 0
    If s.won Or s.histN = 0 Then Exit Function
    While s.histN > 0
        h = s.hist(s.histN)
        s.histN -= 1
        If h.isPush Then
            s.px = h.px
            s.py = h.py
            nx = h.bfx : ny = h.bfy
            bx = h.btx : by = h.bty
            If s.map(bx, by) = "*" Then
                s.map(bx, by) = "."
            Else
                s.map(bx, by) = " "
            End If
            If s.map(nx, ny) = "." Then
                s.map(nx, ny) = "*"
            Else
                s.map(nx, ny) = "$"
            End If
            If s.moves > 0 Then s.moves -= 1
            s.won = 0
            Undo = 1
            Exit Function
        Else
            s.px = h.px
            s.py = h.py
        End If
    Wend
    Undo = 1
End Function

Sub RenderAscii(ByRef s As GameState)
    Dim As Integer x, y
    Dim As String line, ch
    For y = 1 To s.height
        line = ""
        For x = 1 To s.width
            If x = s.px And y = s.py Then
                If s.map(x, y) = "." Then
                    ch = "+"
                Else
                    ch = "@"
                End If
            Else
                ch = s.map(x, y)
            End If
            line += ch
        Next
        Print line
    Next
End Sub
