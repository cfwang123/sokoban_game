"smalltalkapp1 — GNU Smalltalk 推箱子终端版（教学）
 运行: gst -f main.st
"
FileStream fileIn: 'Game.st'.

| level state line ch |
level := #(
  '#######'
  '#. . .#'
  '# $$$ #'
  '#.$@$.#'
  '# $$$ #'
  '#. . .#'
  '#######'
).
state := GameState fromRows: level.
Transcript show: 'sokoban_smalltalk — wasd 移动, z 撤销, r 重置, q 退出'; cr.

[
  Transcript cr.
  Transcript show: state renderAscii.
  Transcript show: 'moves='; show: state moves printString.
  state won ifTrue: [ Transcript show: ' WIN!' ].
  Transcript cr; show: '> '.
  line := stdin nextLine.
  line isNil ifTrue: [ false ] ifFalse: [
    line := line withBlanksTrimmed.
    line isEmpty ifTrue: [ true ] ifFalse: [
      ch := line first asLowercase.
      ch = $w ifTrue: [ state tryMoveDx: 0 dy: -1 ].
      ch = $s ifTrue: [ state tryMoveDx: 0 dy: 1 ].
      ch = $a ifTrue: [ state tryMoveDx: -1 dy: 0 ].
      ch = $d ifTrue: [ state tryMoveDx: 1 dy: 0 ].
      ch = $z ifTrue: [ state undo ].
      ch = $r ifTrue: [ state := GameState fromRows: level ].
      ch = $q ifTrue: [ false ] ifFalse: [
        state won ifTrue: [ Transcript show: 'Level clear!'; cr ].
        true
      ]
    ]
  ]
] whileTrue.
