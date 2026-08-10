# 推箱子核心逻辑（Tcl 教学）

namespace eval ::sokoban {
  namespace export fromRows tryMove undo renderAscii
}

proc ::sokoban::key {x y} { return "$x,$y" }

proc ::sokoban::fromRows {rows {index 0}} {
  set walls {}
  set goals {}
  set boxes {}
  set px 0
  set py 0
  set maxX 0
  set maxY 0
  set y 0
  foreach row $rows {
    set maxY $y
    set len [string length $row]
    for {set x 0} {$x < $len} {incr x} {
      if {$x > $maxX} { set maxX $x }
      set ch [string index $row $x]
      set k [key $x $y]
      if {$ch eq "#"} {
        dict set walls $k 1
      } elseif {$ch eq "."} {
        dict set goals $k 1
      } elseif {$ch eq "\$"} {
        dict set boxes $k 1
      } elseif {$ch eq "*"} {
        dict set boxes $k 1
        dict set goals $k 1
      } elseif {$ch eq "@"} {
        set px $x
        set py $y
      } elseif {$ch eq "+"} {
        set px $x
        set py $y
        dict set goals $k 1
      }
    }
    incr y
  }
  return [dict create \
    walls $walls goals $goals boxes $boxes \
    px $px py $py moves 0 won 0 \
    width [expr {$maxX + 1}] height [expr {$maxY + 1}] \
    level_index $index hist {}]
}

proc ::sokoban::checkWin {sVar} {
  upvar 1 $sVar s
  dict for {b _} [dict get $s boxes] {
    if {![dict exists [dict get $s goals] $b]} {
      dict set s won 0
      return
    }
  }
  dict set s won 1
}

proc ::sokoban::tryMove {sVar dx dy} {
  upvar 1 $sVar s
  if {[dict get $s won]} { return 0 }
  set px [dict get $s px]
  set py [dict get $s py]
  set nx [expr {$px + $dx}]
  set ny [expr {$py + $dy}]
  set nk [key $nx $ny]
  if {[dict exists [dict get $s walls] $nk]} { return 0 }
  if {[dict exists [dict get $s boxes] $nk]} {
    set bx [expr {$nx + $dx}]
    set by [expr {$ny + $dy}]
    set bk [key $bx $by]
    if {[dict exists [dict get $s walls] $bk] ||
        [dict exists [dict get $s boxes] $bk]} {
      return 0
    }
    set hist [dict get $s hist]
    lappend hist [list $px $py $nk $bk]
    dict set s hist $hist
    set boxes [dict get $s boxes]
    dict unset boxes $nk
    dict set boxes $bk 1
    dict set s boxes $boxes
    dict set s px $nx
    dict set s py $ny
    dict set s moves [expr {[dict get $s moves] + 1}]
    checkWin s
    return 1
  }
  set hist [dict get $s hist]
  lappend hist [list $px $py {} {}]
  dict set s hist $hist
  dict set s px $nx
  dict set s py $ny
  return 1
}

proc ::sokoban::undo {sVar} {
  upvar 1 $sVar s
  set hist [dict get $s hist]
  if {[dict get $s won] || [llength $hist] == 0} { return 0 }
  while {[llength $hist] > 0} {
    set entry [lindex $hist end]
    set hist [lrange $hist 0 end-1]
    lassign $entry hx hy bf bt
    if {$bf ne ""} {
      dict set s px $hx
      dict set s py $hy
      set boxes [dict get $s boxes]
      dict unset boxes $bt
      dict set boxes $bf 1
      dict set s boxes $boxes
      set m [dict get $s moves]
      if {$m > 0} { dict set s moves [expr {$m - 1}] }
      dict set s won 0
      dict set s hist $hist
      return 1
    }
    dict set s px $hx
    dict set s py $hy
  }
  dict set s hist $hist
  return 1
}

proc ::sokoban::renderAscii {s} {
  set out ""
  set h [dict get $s height]
  set w [dict get $s width]
  set px [dict get $s px]
  set py [dict get $s py]
  for {set y 0} {$y < $h} {incr y} {
    for {set x 0} {$x < $w} {incr x} {
      set k [key $x $y]
      if {$x == $px && $y == $py} {
        if {[dict exists [dict get $s goals] $k]} {
          append out "+"
        } else {
          append out "@"
        }
      } elseif {[dict exists [dict get $s boxes] $k]} {
        if {[dict exists [dict get $s goals] $k]} {
          append out "*"
        } else {
          append out "\$"
        }
      } elseif {[dict exists [dict get $s walls] $k]} {
        append out "#"
      } elseif {[dict exists [dict get $s goals] $k]} {
        append out "."
      } else {
        append out " "
      }
    }
    append out "\n"
  }
  return $out
}
