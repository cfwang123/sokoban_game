\ forthapp1 — Forth 推箱子终端版（教学）
\ 运行: gforth sokoban.fs

32 CONSTANT MAXW
32 CONSTANT MAXH
1024 CONSTANT MAXHIST

CREATE MAP MAXW MAXH * ALLOT
VARIABLE WIDTH
VARIABLE HEIGHT
VARIABLE PX
VARIABLE PY
VARIABLE MOVES
VARIABLE WON
VARIABLE HISTN

\ hist: 7 cells each: px py bfx bfy btx bty push?
CREATE HIST MAXHIST 7 * CELLS ALLOT

: M@ ( x y -- c ) MAXW * + MAP + C@ ;
: M! ( c x y -- ) MAXW * + MAP + C! ;

: CLEAR-MAP
  MAP MAXW MAXH * BL FILL
  0 WIDTH ! 0 HEIGHT ! 0 MOVES ! 0 WON ! 0 HISTN !
  1 PX ! 1 PY ! ;

: LOAD-LEVEL ( -- )
  CLEAR-MAP
  S" #######"  DROP  \ rows via separate word
  ;

\ store rows as counted strings table
CREATE L0 7 C, CHAR # C, CHAR # C, CHAR # C, CHAR # C, CHAR # C, CHAR # C, CHAR # C,
CREATE L1 7 C, CHAR # C, CHAR . C, BL C, CHAR . C, BL C, CHAR . C, CHAR # C,
CREATE L2 7 C, CHAR # C, BL C, CHAR $ C, CHAR $ C, CHAR $ C, BL C, CHAR # C,
CREATE L3 7 C, CHAR # C, CHAR . C, CHAR $ C, CHAR @ C, CHAR $ C, CHAR . C, CHAR # C,
CREATE L4 7 C, CHAR # C, BL C, CHAR $ C, CHAR $ C, CHAR $ C, BL C, CHAR # C,
CREATE L5 7 C, CHAR # C, CHAR . C, BL C, CHAR . C, BL C, CHAR . C, CHAR # C,
CREATE L6 7 C, CHAR # C, CHAR # C, CHAR # C, CHAR # C, CHAR # C, CHAR # C, CHAR # C,

CREATE LEVELS L0 , L1 , L2 , L3 , L4 , L5 , L6 ,
7 CONSTANT NLEVEL

: LOAD-FROM-TABLE
  CLEAR-MAP
  NLEVEL 0 DO
    LEVELS I CELLS + @
    DUP C@ ( addr len )
    SWAP 1+ SWAP
    DUP WIDTH @ MAX WIDTH !
    0 DO
      DUP I + C@
      CASE
        [CHAR] # OF [CHAR] # I 1+ J 1+ M! ENDOF
        [CHAR] . OF [CHAR] . I 1+ J 1+ M! ENDOF
        [CHAR] $ OF [CHAR] $ I 1+ J 1+ M! ENDOF
        [CHAR] * OF [CHAR] * I 1+ J 1+ M! ENDOF
        [CHAR] @ OF BL I 1+ J 1+ M! I 1+ PX ! J 1+ PY ! ENDOF
        [CHAR] + OF [CHAR] . I 1+ J 1+ M! I 1+ PX ! J 1+ PY ! ENDOF
        BL OF BL I 1+ J 1+ M! ENDOF
        DUP I 1+ J 1+ M!
      ENDCASE
    LOOP
    DROP
  LOOP
  NLEVEL HEIGHT ! ;

: CHECK-WIN
  TRUE WON !
  HEIGHT @ 1+ 1 DO
    WIDTH @ 1+ 1 DO
      I J M@ [CHAR] $ = IF FALSE WON ! THEN
    LOOP
  LOOP ;

: HIST-ADDR ( n -- addr ) 1- 7 * CELLS HIST + ;

: PUSH-HIST ( px py bfx bfy btx bty push? -- )
  HISTN @ 1+ DUP HISTN !
  HIST-ADDR
  >R
  R@ 6 CELLS + !
  R@ 5 CELLS + !
  R@ 4 CELLS + !
  R@ 3 CELLS + !
  R@ 2 CELLS + !
  R@ 1 CELLS + !
  R> ! ;

: TRY-MOVE ( dx dy -- flag )
  WON @ IF 2DROP FALSE EXIT THEN
  PY @ + SWAP PX @ + SWAP ( nx ny )
  2DUP
  DUP 1 < OVER HEIGHT @ > OR IF 2DROP 2DROP FALSE EXIT THEN
  OVER 1 < OVER WIDTH @ > OR IF 2DROP 2DROP FALSE EXIT THEN
  2DUP M@
  DUP [CHAR] # = IF DROP 2DROP 2DROP FALSE EXIT THEN
  DUP [CHAR] $ = OVER [CHAR] * = OR IF
    DROP
    \ push
    2DUP ( nx ny nx ny )
    2 PICK ( dx still? need dx dy ) 
  THEN
  \ simplified: rewrite try-move in high-level style below
  2DROP 2DROP FALSE ;

\ --- clearer high-level definitions ---

VARIABLE DX VARIABLE DY

: TRY-MOVE2 ( dx dy -- )
  WON @ IF 2DROP EXIT THEN
  DY ! DX !
  PX @ DX @ +  PY @ DY @ +  ( nx ny )
  2DUP M@
  DUP [CHAR] # = IF DROP 2DROP EXIT THEN
  DUP [CHAR] $ = OVER [CHAR] * = OR IF
    DROP
    \ box push
    DX @ OVER +  DY @ 2 PICK +  ( nx ny bx by ) 
    \ stack: nx ny bx by
    2DUP M@
    DUP [CHAR] # = OVER [CHAR] $ = OR OVER [CHAR] * = OR IF
      DROP 2DROP 2DROP EXIT
    THEN
    DROP
    PX @ PY @  3 PICK 3 PICK  2 PICK 2 PICK  TRUE PUSH-HIST
    \ clear box cell
    2SWAP 2DUP M@ [CHAR] * = IF [CHAR] . ELSE BL THEN -ROT M!
    \ place box
    2DUP M@ [CHAR] . = IF [CHAR] * ELSE [CHAR] $ THEN -ROT M!
    2DROP
    PX @ DX @ + PX !
    PY @ DY @ + PY !
    1 MOVES +!
    CHECK-WIN
    EXIT
  THEN
  DROP
  PX @ PY @ 0 0 0 0 FALSE PUSH-HIST
  PX @ DX @ + PX !
  PY @ DY @ + PY !
;

: UNDO
  WON @ HISTN @ 0= OR IF EXIT THEN
  BEGIN HISTN @ WHILE
    HISTN @ HIST-ADDR
    DUP 6 CELLS + @ IF
      \ push
      DUP @ PX !  DUP 1 CELLS + @ PY !
      DUP 4 CELLS + @  OVER 5 CELLS + @  ( btx bty )
      2DUP M@ [CHAR] * = IF [CHAR] . ELSE BL THEN -ROT M!
      DUP 2 CELLS + @  OVER 3 CELLS + @
      2DUP M@ [CHAR] . = IF [CHAR] * ELSE [CHAR] $ THEN -ROT M!
      DROP
      MOVES @ 0> IF -1 MOVES +! THEN
      0 WON !
      -1 HISTN +!
      EXIT
    ELSE
      DUP @ PX !  1 CELLS + @ PY !
      -1 HISTN +!
    THEN
  REPEAT ;

: RENDER
  HEIGHT @ 1+ 1 DO
    WIDTH @ 1+ 1 DO
      I PX @ = J PY @ = AND IF
        I J M@ [CHAR] . = IF [CHAR] + ELSE [CHAR] @ THEN EMIT
      ELSE
        I J M@ EMIT
      THEN
    LOOP CR
  LOOP ;

: TOLOWER ( c -- c )
  DUP [CHAR] A [CHAR] Z 1+ WITHIN IF 32 + THEN ;

: MAIN
  LOAD-FROM-TABLE
  ." sokoban_forth — wasd 移动, z 撤销, r 重置, q 退出" CR
  BEGIN
    CR RENDER
    ." moves=" MOVES @ . WON @ IF ."  WIN!" THEN CR
    ." > " 
    PAD 80 ACCEPT PAD SWAP
    DUP 0= IF 2DROP ELSE
      DROP C@ TOLOWER
      CASE
        [CHAR] w OF 0 -1 TRY-MOVE2 ENDOF
        [CHAR] s OF 0 1 TRY-MOVE2 ENDOF
        [CHAR] a OF -1 0 TRY-MOVE2 ENDOF
        [CHAR] d OF 1 0 TRY-MOVE2 ENDOF
        [CHAR] z OF UNDO ENDOF
        [CHAR] r OF LOAD-FROM-TABLE ENDOF
        [CHAR] q OF EXIT ENDOF
      ENDCASE
      WON @ IF ." Level clear!" CR THEN
    THEN
  AGAIN ;

MAIN
BYE
