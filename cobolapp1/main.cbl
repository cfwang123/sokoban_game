      *> cobolapp1 — COBOL 推箱子终端版（教学）
      *> 编译: cobc -x -free main.cbl game.cbl -o sokoban
      *> 运行: ./sokoban
       IDENTIFICATION DIVISION.
       PROGRAM-ID. main.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  G-MAP.
           05  G-ROW OCCURS 32 TIMES.
               10  G-CELL OCCURS 32 TIMES PIC X.
       01  G-WIDTH             PIC 9(2) VALUE 0.
       01  G-HEIGHT            PIC 9(2) VALUE 0.
       01  G-PX                PIC S9(4) VALUE 0.
       01  G-PY                PIC S9(4) VALUE 0.
       01  G-MOVES             PIC 9(6) VALUE 0.
       01  G-WON               PIC X VALUE "N".
       01  G-HIST-COUNT        PIC 9(4) VALUE 0.
       01  G-HIST.
           05  G-H OCCURS 1024 TIMES.
               10  G-H-PX      PIC S9(4).
               10  G-H-PY      PIC S9(4).
               10  G-H-BFX     PIC S9(4).
               10  G-H-BFY     PIC S9(4).
               10  G-H-BTX     PIC S9(4).
               10  G-H-BTY     PIC S9(4).
               10  G-H-PUSH    PIC X.
       01  G-CMD               PIC X(16).
       01  G-DX                PIC S9(2) VALUE 0.
       01  G-DY                PIC S9(2) VALUE 0.
       01  G-RESULT            PIC X.
       01  G-LEVEL-SRC.
           05  G-LEVEL-ROW OCCURS 16 TIMES PIC X(64).
       01  G-LEVEL-N           PIC 9(2) VALUE 7.
       01  WS-LINE             PIC X(80).
       01  WS-CH               PIC X.
       01  WS-DONE             PIC X VALUE "N".
       01  WS-FLAG             PIC X(8).

       PROCEDURE DIVISION.
       MAIN-PROC.
           MOVE "#######" TO G-LEVEL-ROW(1)
           MOVE "#. . .#" TO G-LEVEL-ROW(2)
           MOVE "# $$$ #" TO G-LEVEL-ROW(3)
           MOVE "#.$@$.#" TO G-LEVEL-ROW(4)
           MOVE "# $$$ #" TO G-LEVEL-ROW(5)
           MOVE "#. . .#" TO G-LEVEL-ROW(6)
           MOVE "#######" TO G-LEVEL-ROW(7)
           MOVE 7 TO G-LEVEL-N
           PERFORM INIT-GAME
           DISPLAY "sokoban_cobol — wasd 移动, z 撤销, r 重置, q 退出"
           PERFORM UNTIL WS-DONE = "Y"
               DISPLAY " "
               MOVE "RENDER" TO G-CMD
               CALL "game" USING
                   G-MAP G-WIDTH G-HEIGHT G-PX G-PY G-MOVES G-WON
                   G-HIST-COUNT G-HIST G-CMD G-DX G-DY G-RESULT
                   G-LEVEL-SRC G-LEVEL-N
               IF G-WON = "Y"
                   MOVE " WIN!" TO WS-FLAG
               ELSE
                   MOVE SPACES TO WS-FLAG
               END-IF
               DISPLAY "moves=" G-MOVES WS-FLAG
               DISPLAY "> " WITH NO ADVANCING
               ACCEPT WS-LINE
               MOVE FUNCTION LOWER-CASE(WS-LINE(1:1)) TO WS-CH
               EVALUATE WS-CH
                   WHEN "w"
                       MOVE 0 TO G-DX
                       MOVE -1 TO G-DY
                       MOVE "MOVE" TO G-CMD
                       CALL "game" USING
                           G-MAP G-WIDTH G-HEIGHT G-PX G-PY G-MOVES
                           G-WON G-HIST-COUNT G-HIST G-CMD
                           G-DX G-DY G-RESULT
                           G-LEVEL-SRC G-LEVEL-N
                   WHEN "s"
                       MOVE 0 TO G-DX
                       MOVE 1 TO G-DY
                       MOVE "MOVE" TO G-CMD
                       CALL "game" USING
                           G-MAP G-WIDTH G-HEIGHT G-PX G-PY G-MOVES
                           G-WON G-HIST-COUNT G-HIST G-CMD
                           G-DX G-DY G-RESULT
                           G-LEVEL-SRC G-LEVEL-N
                   WHEN "a"
                       MOVE -1 TO G-DX
                       MOVE 0 TO G-DY
                       MOVE "MOVE" TO G-CMD
                       CALL "game" USING
                           G-MAP G-WIDTH G-HEIGHT G-PX G-PY G-MOVES
                           G-WON G-HIST-COUNT G-HIST G-CMD
                           G-DX G-DY G-RESULT
                           G-LEVEL-SRC G-LEVEL-N
                   WHEN "d"
                       MOVE 1 TO G-DX
                       MOVE 0 TO G-DY
                       MOVE "MOVE" TO G-CMD
                       CALL "game" USING
                           G-MAP G-WIDTH G-HEIGHT G-PX G-PY G-MOVES
                           G-WON G-HIST-COUNT G-HIST G-CMD
                           G-DX G-DY G-RESULT
                           G-LEVEL-SRC G-LEVEL-N
                   WHEN "z"
                       MOVE "UNDO" TO G-CMD
                       CALL "game" USING
                           G-MAP G-WIDTH G-HEIGHT G-PX G-PY G-MOVES
                           G-WON G-HIST-COUNT G-HIST G-CMD
                           G-DX G-DY G-RESULT
                           G-LEVEL-SRC G-LEVEL-N
                   WHEN "r"
                       PERFORM INIT-GAME
                   WHEN "q"
                       MOVE "Y" TO WS-DONE
                   WHEN OTHER
                       CONTINUE
               END-EVALUATE
               IF G-WON = "Y" AND WS-DONE = "N"
                   DISPLAY "Level clear!"
               END-IF
           END-PERFORM
           STOP RUN.

       INIT-GAME.
           MOVE "INIT" TO G-CMD
           CALL "game" USING
               G-MAP G-WIDTH G-HEIGHT G-PX G-PY G-MOVES G-WON
               G-HIST-COUNT G-HIST G-CMD G-DX G-DY G-RESULT
               G-LEVEL-SRC G-LEVEL-N.
