      *> 推箱子核心逻辑（COBOL 教学，GnuCOBOL）
       IDENTIFICATION DIVISION.
       PROGRAM-ID. game.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-MAX-W            PIC 9(2) VALUE 32.
       01  WS-MAX-H            PIC 9(2) VALUE 32.
       01  WS-MAX-HIST         PIC 9(4) VALUE 1024.
       01  WS-I                PIC 9(4).
       01  WS-J                PIC 9(4).
       01  WS-X                PIC S9(4).
       01  WS-Y                PIC S9(4).
       01  WS-NX               PIC S9(4).
       01  WS-NY               PIC S9(4).
       01  WS-BX               PIC S9(4).
       01  WS-BY               PIC S9(4).
       01  WS-CH               PIC X.
       01  WS-OK               PIC X.
       01  WS-LINE             PIC X(64).
       01  WS-LEN              PIC 9(4).
       01  WS-ENTRY-FOUND      PIC X.

       LINKAGE SECTION.
       01  L-MAP.
           05  L-ROW OCCURS 32 TIMES.
               10  L-CELL OCCURS 32 TIMES PIC X.
       01  L-WIDTH             PIC 9(2).
       01  L-HEIGHT            PIC 9(2).
       01  L-PX                PIC S9(4).
       01  L-PY                PIC S9(4).
       01  L-MOVES             PIC 9(6).
       01  L-WON               PIC X.
       01  L-HIST-COUNT        PIC 9(4).
       01  L-HIST.
           05  L-H OCCURS 1024 TIMES.
               10  L-H-PX      PIC S9(4).
               10  L-H-PY      PIC S9(4).
               10  L-H-BFX     PIC S9(4).
               10  L-H-BFY     PIC S9(4).
               10  L-H-BTX     PIC S9(4).
               10  L-H-BTY     PIC S9(4).
               10  L-H-PUSH    PIC X.
       01  L-CMD               PIC X(16).
       01  L-DX                PIC S9(2).
       01  L-DY                PIC S9(2).
       01  L-RESULT            PIC X.
       01  L-LEVEL-SRC.
           05  L-LEVEL-ROW OCCURS 16 TIMES PIC X(64).
       01  L-LEVEL-N           PIC 9(2).

       PROCEDURE DIVISION USING
           L-MAP L-WIDTH L-HEIGHT L-PX L-PY L-MOVES L-WON
           L-HIST-COUNT L-HIST L-CMD L-DX L-DY L-RESULT
           L-LEVEL-SRC L-LEVEL-N.

       MAIN-LOGIC.
           EVALUATE L-CMD
               WHEN "INIT"
                   PERFORM DO-INIT
               WHEN "MOVE"
                   PERFORM DO-MOVE
               WHEN "UNDO"
                   PERFORM DO-UNDO
               WHEN "RENDER"
                   PERFORM DO-RENDER
               WHEN "CHECKWIN"
                   PERFORM DO-CHECK-WIN
               WHEN OTHER
                   MOVE "N" TO L-RESULT
           END-EVALUATE
           GOBACK.

       DO-INIT.
           MOVE 0 TO L-WIDTH L-HEIGHT L-MOVES L-HIST-COUNT
           MOVE "N" TO L-WON
           MOVE 0 TO L-PX L-PY
           PERFORM VARYING WS-Y FROM 1 BY 1 UNTIL WS-Y > 32
               PERFORM VARYING WS-X FROM 1 BY 1 UNTIL WS-X > 32
                   MOVE SPACE TO L-CELL(WS-Y, WS-X)
               END-PERFORM
           END-PERFORM
           PERFORM VARYING WS-I FROM 1 BY 1 UNTIL WS-I > L-LEVEL-N
               MOVE L-LEVEL-ROW(WS-I) TO WS-LINE
               MOVE FUNCTION LENGTH(
                   FUNCTION TRIM(WS-LINE TRAILING)) TO WS-LEN
               IF WS-LEN > L-WIDTH
                   MOVE WS-LEN TO L-WIDTH
               END-IF
               MOVE WS-I TO L-HEIGHT
               PERFORM VARYING WS-J FROM 1 BY 1 UNTIL WS-J > WS-LEN
                   MOVE WS-LINE(WS-J:1) TO WS-CH
                   EVALUATE WS-CH
                       WHEN "#"
                           MOVE "#" TO L-CELL(WS-I, WS-J)
                       WHEN "."
                           MOVE "." TO L-CELL(WS-I, WS-J)
                       WHEN "$"
                           MOVE "$" TO L-CELL(WS-I, WS-J)
                       WHEN "*"
                           MOVE "*" TO L-CELL(WS-I, WS-J)
                       WHEN "@"
                           MOVE SPACE TO L-CELL(WS-I, WS-J)
                           COMPUTE L-PX = WS-J
                           COMPUTE L-PY = WS-I
                       WHEN "+"
                           MOVE "." TO L-CELL(WS-I, WS-J)
                           COMPUTE L-PX = WS-J
                           COMPUTE L-PY = WS-I
                       WHEN OTHER
                           MOVE SPACE TO L-CELL(WS-I, WS-J)
                   END-EVALUATE
               END-PERFORM
           END-PERFORM
           MOVE "Y" TO L-RESULT.

       DO-MOVE.
           IF L-WON = "Y"
               MOVE "N" TO L-RESULT
               EXIT PARAGRAPH
           END-IF
           COMPUTE WS-NX = L-PX + L-DX
           COMPUTE WS-NY = L-PY + L-DY
           IF WS-NX < 1 OR WS-NY < 1
               OR WS-NX > L-WIDTH OR WS-NY > L-HEIGHT
               MOVE "N" TO L-RESULT
               EXIT PARAGRAPH
           END-IF
           MOVE L-CELL(WS-NY, WS-NX) TO WS-CH
           IF WS-CH = "#"
               MOVE "N" TO L-RESULT
               EXIT PARAGRAPH
           END-IF
           IF WS-CH = "$" OR WS-CH = "*"
               COMPUTE WS-BX = WS-NX + L-DX
               COMPUTE WS-BY = WS-NY + L-DY
               IF WS-BX < 1 OR WS-BY < 1
                   OR WS-BX > L-WIDTH OR WS-BY > L-HEIGHT
                   MOVE "N" TO L-RESULT
                   EXIT PARAGRAPH
               END-IF
               MOVE L-CELL(WS-BY, WS-BX) TO WS-CH
               IF WS-CH = "#" OR WS-CH = "$" OR WS-CH = "*"
                   MOVE "N" TO L-RESULT
                   EXIT PARAGRAPH
               END-IF
               ADD 1 TO L-HIST-COUNT
               MOVE L-PX TO L-H-PX(L-HIST-COUNT)
               MOVE L-PY TO L-H-PY(L-HIST-COUNT)
               MOVE WS-NX TO L-H-BFX(L-HIST-COUNT)
               MOVE WS-NY TO L-H-BFY(L-HIST-COUNT)
               MOVE WS-BX TO L-H-BTX(L-HIST-COUNT)
               MOVE WS-BY TO L-H-BTY(L-HIST-COUNT)
               MOVE "Y" TO L-H-PUSH(L-HIST-COUNT)
               *> clear old box cell
               IF L-CELL(WS-NY, WS-NX) = "*"
                   MOVE "." TO L-CELL(WS-NY, WS-NX)
               ELSE
                   MOVE SPACE TO L-CELL(WS-NY, WS-NX)
               END-IF
               *> place box
               IF L-CELL(WS-BY, WS-BX) = "."
                   MOVE "*" TO L-CELL(WS-BY, WS-BX)
               ELSE
                   MOVE "$" TO L-CELL(WS-BY, WS-BX)
               END-IF
               MOVE WS-NX TO L-PX
               MOVE WS-NY TO L-PY
               ADD 1 TO L-MOVES
               PERFORM DO-CHECK-WIN
               MOVE "Y" TO L-RESULT
               EXIT PARAGRAPH
           END-IF
           ADD 1 TO L-HIST-COUNT
           MOVE L-PX TO L-H-PX(L-HIST-COUNT)
           MOVE L-PY TO L-H-PY(L-HIST-COUNT)
           MOVE 0 TO L-H-BFX(L-HIST-COUNT)
           MOVE 0 TO L-H-BFY(L-HIST-COUNT)
           MOVE 0 TO L-H-BTX(L-HIST-COUNT)
           MOVE 0 TO L-H-BTY(L-HIST-COUNT)
           MOVE "N" TO L-H-PUSH(L-HIST-COUNT)
           MOVE WS-NX TO L-PX
           MOVE WS-NY TO L-PY
           MOVE "Y" TO L-RESULT.

       DO-UNDO.
           IF L-WON = "Y" OR L-HIST-COUNT = 0
               MOVE "N" TO L-RESULT
               EXIT PARAGRAPH
           END-IF
           MOVE "N" TO WS-ENTRY-FOUND
           PERFORM UNTIL L-HIST-COUNT = 0 OR WS-ENTRY-FOUND = "Y"
               IF L-H-PUSH(L-HIST-COUNT) = "Y"
                   MOVE "Y" TO WS-ENTRY-FOUND
                   MOVE L-H-PX(L-HIST-COUNT) TO L-PX
                   MOVE L-H-PY(L-HIST-COUNT) TO L-PY
                   MOVE L-H-BFX(L-HIST-COUNT) TO WS-NX
                   MOVE L-H-BFY(L-HIST-COUNT) TO WS-NY
                   MOVE L-H-BTX(L-HIST-COUNT) TO WS-BX
                   MOVE L-H-BTY(L-HIST-COUNT) TO WS-BY
                   *> remove box from to
                   IF L-CELL(WS-BY, WS-BX) = "*"
                       MOVE "." TO L-CELL(WS-BY, WS-BX)
                   ELSE
                       MOVE SPACE TO L-CELL(WS-BY, WS-BX)
                   END-IF
                   *> restore box at from
                   IF L-CELL(WS-NY, WS-NX) = "."
                       MOVE "*" TO L-CELL(WS-NY, WS-NX)
                   ELSE
                       MOVE "$" TO L-CELL(WS-NY, WS-NX)
                   END-IF
                   IF L-MOVES > 0
                       SUBTRACT 1 FROM L-MOVES
                   END-IF
                   MOVE "N" TO L-WON
               ELSE
                   MOVE L-H-PX(L-HIST-COUNT) TO L-PX
                   MOVE L-H-PY(L-HIST-COUNT) TO L-PY
               END-IF
               SUBTRACT 1 FROM L-HIST-COUNT
           END-PERFORM
           MOVE "Y" TO L-RESULT.

       DO-CHECK-WIN.
           MOVE "Y" TO L-WON
           PERFORM VARYING WS-Y FROM 1 BY 1 UNTIL WS-Y > L-HEIGHT
               PERFORM VARYING WS-X FROM 1 BY 1 UNTIL WS-X > L-WIDTH
                   IF L-CELL(WS-Y, WS-X) = "$"
                       MOVE "N" TO L-WON
                   END-IF
               END-PERFORM
           END-PERFORM.

       DO-RENDER.
           PERFORM VARYING WS-Y FROM 1 BY 1 UNTIL WS-Y > L-HEIGHT
               MOVE SPACES TO WS-LINE
               PERFORM VARYING WS-X FROM 1 BY 1 UNTIL WS-X > L-WIDTH
                   IF WS-X = L-PX AND WS-Y = L-PY
                       IF L-CELL(WS-Y, WS-X) = "."
                           MOVE "+" TO WS-LINE(WS-X:1)
                       ELSE
                           MOVE "@" TO WS-LINE(WS-X:1)
                       END-IF
                   ELSE
                       MOVE L-CELL(WS-Y, WS-X) TO WS-LINE(WS-X:1)
                       IF WS-LINE(WS-X:1) = SPACE
                           MOVE " " TO WS-LINE(WS-X:1)
                       END-IF
                   END-IF
               END-PERFORM
               DISPLAY FUNCTION TRIM(WS-LINE TRAILING)
           END-PERFORM
           MOVE "Y" TO L-RESULT.
