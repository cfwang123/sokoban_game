' 推箱子核心逻辑（Visual Basic .NET 教学）

Imports System.Collections.Generic
Imports System.Text

Public Class Hist
    Public Property Px As Integer
    Public Property Py As Integer
    Public Property BoxFrom As String
    Public Property BoxTo As String
    Public Property IsPush As Boolean
End Class

Public Class GameState
    Public Walls As New HashSet(Of String)()
    Public Goals As New HashSet(Of String)()
    Public Boxes As New HashSet(Of String)()
    Public Px As Integer
    Public Py As Integer
    Public Moves As Integer
    Public Won As Boolean
    Public Width As Integer
    Public Height As Integer
    Public Hist As New List(Of Hist)()

    Public Shared Function Key(x As Integer, y As Integer) As String
        Return $"{x},{y}"
    End Function

    Public Shared Function FromRows(rows As String(), Optional index As Integer = 0) As GameState
        Dim s As New GameState()
        Dim maxX As Integer = 0
        Dim maxY As Integer = 0
        For y = 0 To rows.Length - 1
            maxY = y
            Dim row = rows(y)
            For x = 0 To row.Length - 1
                If x > maxX Then maxX = x
                Dim ch = row(x)
                Dim k = Key(x, y)
                Select Case ch
                    Case "#"c : s.Walls.Add(k)
                    Case "."c : s.Goals.Add(k)
                    Case "$"c : s.Boxes.Add(k)
                    Case "*"c
                        s.Boxes.Add(k)
                        s.Goals.Add(k)
                    Case "@"c
                        s.Px = x
                        s.Py = y
                    Case "+"c
                        s.Px = x
                        s.Py = y
                        s.Goals.Add(k)
                End Select
            Next
        Next
        s.Width = maxX + 1
        s.Height = maxY + 1
        Return s
    End Function

    Private Sub CheckWin()
        For Each b In Boxes
            If Not Goals.Contains(b) Then
                Won = False
                Return
            End If
        Next
        Won = True
    End Sub

    Public Function TryMove(dx As Integer, dy As Integer) As Boolean
        If Won Then Return False
        Dim nx = Px + dx
        Dim ny = Py + dy
        Dim nk = Key(nx, ny)
        If Walls.Contains(nk) Then Return False
        If Boxes.Contains(nk) Then
            Dim bx = nx + dx
            Dim by = ny + dy
            Dim bk = Key(bx, by)
            If Walls.Contains(bk) OrElse Boxes.Contains(bk) Then Return False
            Hist.Add(New Hist With {
                .Px = Px, .Py = Py,
                .BoxFrom = nk, .BoxTo = bk, .IsPush = True
            })
            Boxes.Remove(nk)
            Boxes.Add(bk)
            Px = nx
            Py = ny
            Moves += 1
            CheckWin()
            Return True
        End If
        Hist.Add(New Hist With {.Px = Px, .Py = Py, .IsPush = False})
        Px = nx
        Py = ny
        Return True
    End Function

    Public Function Undo() As Boolean
        If Won OrElse Hist.Count = 0 Then Return False
        While Hist.Count > 0
            Dim e = Hist(Hist.Count - 1)
            Hist.RemoveAt(Hist.Count - 1)
            If e.IsPush Then
                Px = e.Px
                Py = e.Py
                Boxes.Remove(e.BoxTo)
                Boxes.Add(e.BoxFrom)
                If Moves > 0 Then Moves -= 1
                Won = False
                Return True
            End If
            Px = e.Px
            Py = e.Py
        End While
        Return True
    End Function

    Public Function RenderAscii() As String
        Dim sb As New StringBuilder()
        For y = 0 To Height - 1
            For x = 0 To Width - 1
                Dim k = Key(x, y)
                If Px = x AndAlso Py = y Then
                    sb.Append(If(Goals.Contains(k), "+"c, "@"c))
                ElseIf Boxes.Contains(k) Then
                    sb.Append(If(Goals.Contains(k), "*"c, "$"c))
                ElseIf Walls.Contains(k) Then
                    sb.Append("#"c)
                ElseIf Goals.Contains(k) Then
                    sb.Append("."c)
                Else
                    sb.Append(" "c)
                End If
            Next
            sb.AppendLine()
        Next
        Return sb.ToString()
    End Function
End Class
