#!/usr/bin/env tclsh
# tclapp1 — Tcl 推箱子终端版（教学）

set here [file dirname [file normalize [info script]]]
source [file join $here game.tcl]

set LEVEL [list \
  "#######" \
  "#. . .#" \
  "# \$\$\$ #" \
  "#.\$@\$.#" \
  "# \$\$\$ #" \
  "#. . .#" \
  "#######"]

set state [::sokoban::fromRows $LEVEL 0]
puts "sokoban_tcl — wasd 移动, z 撤销, r 重置, q 退出"

while {1} {
  puts ""
  puts -nonewline [::sokoban::renderAscii $state]
  set flag [expr {[dict get $state won] ? " WIN!" : ""}]
  puts "moves=[dict get $state moves]$flag"
  puts -nonewline "> "
  flush stdout
  if {[gets stdin line] < 0} { break }
  set line [string trim $line]
  if {$line eq ""} { continue }
  set ch [string tolower [string index $line 0]]
  switch -exact -- $ch {
    w { ::sokoban::tryMove state 0 -1 }
    s { ::sokoban::tryMove state 0 1 }
    a { ::sokoban::tryMove state -1 0 }
    d { ::sokoban::tryMove state 1 0 }
    z { ::sokoban::undo state }
    r { set state [::sokoban::fromRows $LEVEL 0] }
    q { break }
  }
  if {[dict get $state won]} {
    puts "Level clear!"
  }
}
