; Parenthesis Hell Sokoban — pure () program
; Default: cat / identity — returns the input value unchanged.
; Host (main.py) passes the game state (Cons/Nil tree); identity
; preserves it. Non-() characters are comments/ignored by the reader
; except we strip ; lines in main.py.
;
; () evaluates to the program argument (the state).
()
