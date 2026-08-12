Attribute VB_Name = "Game"
' 推箱子核心逻辑（VBA 教学，Excel / 通用 VBA 宿主）
' 用法见 main.bas / readme.md

Option Explicit

Public Type HistEntry
    Px As Long
    Py As Long
    BoxFrom As String
    BoxTo As String
    IsPush As Boolean
End Type

Public Type GameState
    Walls As Object   ' Scripting.Dictionary
    Goals As Object
    Boxes As Object
    Px As Long
    Py As Long
    Moves As Long
    Won As Boolean
    Width As Long
    Height As Long
    Hist() As HistEntry
    HistN As Long
End Type

Public Function CellKey(ByVal x As Long, ByVal y As Long) As String
    CellKey = CStr(x) & "," & CStr(y)
End Function

Public Function NewDict() As Object
    Set NewDict = CreateObject("Scripting.Dictionary")
End Function

Public Function FromRows(ByRef rows() As String) As GameState
    Dim s As GameState
    Dim y As Long, x As Long, maxX As Long, maxY As Long
    Dim ch As String, k As String
    Dim row As String

    Set s.Walls = NewDict()
    Set s.Goals = NewDict()
    Set s.Boxes = NewDict()
    s.Px = 0: s.Py = 0: s.Moves = 0: s.Won = False: s.HistN = 0
    ReDim s.Hist(0 To 1023)
    maxX = 0: maxY = 0

    For y = LBound(rows) To UBound(rows)
        maxY = y
        row = rows(y)
        For x = 1 To Len(row)
            If x - 1 > maxX Then maxX = x - 1
            ch = Mid$(row, x, 1)
            k = CellKey(x - 1, y)
            Select Case ch
                Case "#"
                    s.Walls(k) = True
                Case "."
                    s.Goals(k) = True
                Case "$"
                    s.Boxes(k) = True
                Case "*"
                    s.Boxes(k) = True
                    s.Goals(k) = True
                Case "@"
                    s.Px = x - 1
                    s.Py = y
                Case "+"
                    s.Px = x - 1
                    s.Py = y
                    s.Goals(k) = True
            End Select
        Next x
    Next y
    s.Width = maxX + 1
    s.Height = maxY + 1
    FromRows = s
End Function

Private Sub CheckWin(ByRef s As GameState)
    Dim k As Variant
    For Each k In s.Boxes.Keys
        If Not s.Goals.Exists(CStr(k)) Then
            s.Won = False
            Exit Sub
        End If
    Next k
    s.Won = True
End Sub

Public Function TryMove(ByRef s As GameState, ByVal dx As Long, ByVal dy As Long) As Boolean
    Dim nx As Long, ny As Long, nk As String
    Dim bx As Long, by As Long, bk As String

    TryMove = False
    If s.Won Then Exit Function
    nx = s.Px + dx
    ny = s.Py + dy
    nk = CellKey(nx, ny)
    If s.Walls.Exists(nk) Then Exit Function

    If s.Boxes.Exists(nk) Then
        bx = nx + dx
        by = ny + dy
        bk = CellKey(bx, by)
        If s.Walls.Exists(bk) Or s.Boxes.Exists(bk) Then Exit Function
        If s.HistN >= 1024 Then Exit Function
        s.Hist(s.HistN).Px = s.Px
        s.Hist(s.HistN).Py = s.Py
        s.Hist(s.HistN).BoxFrom = nk
        s.Hist(s.HistN).BoxTo = bk
        s.Hist(s.HistN).IsPush = True
        s.HistN = s.HistN + 1
        s.Boxes.Remove nk
        s.Boxes(bk) = True
        s.Px = nx
        s.Py = ny
        s.Moves = s.Moves + 1
        CheckWin s
        TryMove = True
        Exit Function
    End If

    If s.HistN >= 1024 Then Exit Function
    s.Hist(s.HistN).Px = s.Px
    s.Hist(s.HistN).Py = s.Py
    s.Hist(s.HistN).IsPush = False
    s.HistN = s.HistN + 1
    s.Px = nx
    s.Py = ny
    TryMove = True
End Function

Public Function UndoMove(ByRef s As GameState) As Boolean
    Dim e As HistEntry
    UndoMove = False
    If s.Won Or s.HistN = 0 Then Exit Function
    Do While s.HistN > 0
        s.HistN = s.HistN - 1
        e = s.Hist(s.HistN)
        If e.IsPush Then
            s.Px = e.Px
            s.Py = e.Py
            If s.Boxes.Exists(e.BoxTo) Then s.Boxes.Remove e.BoxTo
            s.Boxes(e.BoxFrom) = True
            If s.Moves > 0 Then s.Moves = s.Moves - 1
            s.Won = False
            UndoMove = True
            Exit Function
        End If
        s.Px = e.Px
        s.Py = e.Py
    Loop
    UndoMove = True
End Function

Public Function RenderAscii(ByRef s As GameState) As String
    Dim y As Long, x As Long, k As String
    Dim line As String, out As String
    out = ""
    For y = 0 To s.Height - 1
        line = ""
        For x = 0 To s.Width - 1
            k = CellKey(x, y)
            If s.Px = x And s.Py = y Then
                If s.Goals.Exists(k) Then line = line & "+" Else line = line & "@"
            ElseIf s.Boxes.Exists(k) Then
                If s.Goals.Exists(k) Then line = line & "*" Else line = line & "$"
            ElseIf s.Walls.Exists(k) Then
                line = line & "#"
            ElseIf s.Goals.Exists(k) Then
                line = line & "."
            Else
                line = line & " "
            End If
        Next x
        out = out & line & vbCrLf
    Next y
    RenderAscii = out
End Function
