;; asm_wasmapp1 — WebAssembly Text Format 推箱子核心（教学）
;; 完整交互见 index.html（JS 主机 + 本模块导出）
;;
;; 导出:
;;   (reset) (try_move dx dy) -> i32
;;   (undo) -> i32
;;   (get_moves) (get_won) (get_w) (get_h)
;;   (cell x y) -> i32 字符码
;;
;; 内存布局:
;;   0..1023   map 32*32 字节
;;   1024      width i32
;;   1028      height
;;   1032      px
;;   1036      py
;;   1040      moves
;;   1044      won
;;   1048      hist_n
;;   1052..    hist entries 28 bytes each: px py bfx bfy btx bty is_push (i32*7)

(module
  (memory (export "memory") 1)
  (global $W i32 (i32.const 1024))
  (global $H i32 (i32.const 1028))
  (global $PX i32 (i32.const 1032))
  (global $PY i32 (i32.const 1036))
  (global $MOVES i32 (i32.const 1040))
  (global $WON i32 (i32.const 1044))
  (global $HIST_N i32 (i32.const 1048))
  (global $HIST_BASE i32 (i32.const 1052))
  (global $MAP i32 (i32.const 0))
  (global $STRIDE i32 (i32.const 32))

  (func $at (param $x i32) (param $y i32) (result i32)
    (i32.load8_u
      (i32.add (global.get $MAP)
        (i32.add (local.get $x)
          (i32.mul (local.get $y) (global.get $STRIDE))))))

  (func $set (param $x i32) (param $y i32) (param $c i32)
    (i32.store8
      (i32.add (global.get $MAP)
        (i32.add (local.get $x)
          (i32.mul (local.get $y) (global.get $STRIDE))))
      (local.get $c)))

  (func $check_win
    (local $x i32) (local $y i32)
    (i32.store (global.get $WON) (i32.const 1))
    (local.set $y (i32.const 0))
    (loop $ly
      (local.set $x (i32.const 0))
      (loop $lx
        (if (i32.eq (call $at (local.get $x) (local.get $y)) (i32.const 36)) ;; '$'
          (then (i32.store (global.get $WON) (i32.const 0))))
        (local.set $x (i32.add (local.get $x) (i32.const 1)))
        (br_if $lx (i32.lt_s (local.get $x) (i32.load (global.get $W)))))
      (local.set $y (i32.add (local.get $y) (i32.const 1)))
      (br_if $ly (i32.lt_s (local.get $y) (i32.load (global.get $H))))))

  (func $reset (export "reset")
    (local $y i32) (local $x i32)
    ;; clear map
    (memory.fill (i32.const 0) (i32.const 32) (i32.const 1024))
    (i32.store (global.get $W) (i32.const 7))
    (i32.store (global.get $H) (i32.const 7))
    (i32.store (global.get $MOVES) (i32.const 0))
    (i32.store (global.get $WON) (i32.const 0))
    (i32.store (global.get $HIST_N) (i32.const 0))
    ;; row0 #######
    (local.set $x (i32.const 0))
    (loop $r0
      (call $set (local.get $x) (i32.const 0) (i32.const 35))
      (local.set $x (i32.add (local.get $x) (i32.const 1)))
      (br_if $r0 (i32.lt_s (local.get $x) (i32.const 7))))
    ;; simplified: hardcode key rows via data-like stores
    ;; row1 #. . .#
    (call $set (i32.const 0) (i32.const 1) (i32.const 35))
    (call $set (i32.const 1) (i32.const 1) (i32.const 46))
    (call $set (i32.const 2) (i32.const 1) (i32.const 32))
    (call $set (i32.const 3) (i32.const 1) (i32.const 46))
    (call $set (i32.const 4) (i32.const 1) (i32.const 32))
    (call $set (i32.const 5) (i32.const 1) (i32.const 46))
    (call $set (i32.const 6) (i32.const 1) (i32.const 35))
    ;; row2 # $$$ #
    (call $set (i32.const 0) (i32.const 2) (i32.const 35))
    (call $set (i32.const 1) (i32.const 2) (i32.const 32))
    (call $set (i32.const 2) (i32.const 2) (i32.const 36))
    (call $set (i32.const 3) (i32.const 2) (i32.const 36))
    (call $set (i32.const 4) (i32.const 2) (i32.const 36))
    (call $set (i32.const 5) (i32.const 2) (i32.const 32))
    (call $set (i32.const 6) (i32.const 2) (i32.const 35))
    ;; row3 #.$@$.#
    (call $set (i32.const 0) (i32.const 3) (i32.const 35))
    (call $set (i32.const 1) (i32.const 3) (i32.const 46))
    (call $set (i32.const 2) (i32.const 3) (i32.const 36))
    (call $set (i32.const 3) (i32.const 3) (i32.const 32)) ;; player stands on floor
    (call $set (i32.const 4) (i32.const 3) (i32.const 36))
    (call $set (i32.const 5) (i32.const 3) (i32.const 46))
    (call $set (i32.const 6) (i32.const 3) (i32.const 35))
    (i32.store (global.get $PX) (i32.const 3))
    (i32.store (global.get $PY) (i32.const 3))
    ;; row4 # $$$ #
    (call $set (i32.const 0) (i32.const 4) (i32.const 35))
    (call $set (i32.const 1) (i32.const 4) (i32.const 32))
    (call $set (i32.const 2) (i32.const 4) (i32.const 36))
    (call $set (i32.const 3) (i32.const 4) (i32.const 36))
    (call $set (i32.const 4) (i32.const 4) (i32.const 36))
    (call $set (i32.const 5) (i32.const 4) (i32.const 32))
    (call $set (i32.const 6) (i32.const 4) (i32.const 35))
    ;; row5 #. . .#
    (call $set (i32.const 0) (i32.const 5) (i32.const 35))
    (call $set (i32.const 1) (i32.const 5) (i32.const 46))
    (call $set (i32.const 2) (i32.const 5) (i32.const 32))
    (call $set (i32.const 3) (i32.const 5) (i32.const 46))
    (call $set (i32.const 4) (i32.const 5) (i32.const 32))
    (call $set (i32.const 5) (i32.const 5) (i32.const 46))
    (call $set (i32.const 6) (i32.const 5) (i32.const 35))
    ;; row6 #######
    (local.set $x (i32.const 0))
    (loop $r6
      (call $set (local.get $x) (i32.const 6) (i32.const 35))
      (local.set $x (i32.add (local.get $x) (i32.const 1)))
      (br_if $r6 (i32.lt_s (local.get $x) (i32.const 7)))))

  (func $push_hist (param $px i32) (param $py i32)
                   (param $bfx i32) (param $bfy i32)
                   (param $btx i32) (param $bty i32)
                   (param $push i32)
    (local $base i32) (local $n i32)
    (local.set $n (i32.load (global.get $HIST_N)))
    (local.set $base (i32.add (global.get $HIST_BASE) (i32.mul (local.get $n) (i32.const 28))))
    (i32.store (local.get $base) (local.get $px))
    (i32.store (i32.add (local.get $base) (i32.const 4)) (local.get $py))
    (i32.store (i32.add (local.get $base) (i32.const 8)) (local.get $bfx))
    (i32.store (i32.add (local.get $base) (i32.const 12)) (local.get $bfy))
    (i32.store (i32.add (local.get $base) (i32.const 16)) (local.get $btx))
    (i32.store (i32.add (local.get $base) (i32.const 20)) (local.get $bty))
    (i32.store (i32.add (local.get $base) (i32.const 24)) (local.get $push))
    (i32.store (global.get $HIST_N) (i32.add (local.get $n) (i32.const 1))))

  (func $try_move (export "try_move") (param $dx i32) (param $dy i32) (result i32)
    (local $nx i32) (local $ny i32) (local $bx i32) (local $by i32) (local $ch i32)
    (if (i32.load (global.get $WON)) (then (return (i32.const 0))))
    (local.set $nx (i32.add (i32.load (global.get $PX)) (local.get $dx)))
    (local.set $ny (i32.add (i32.load (global.get $PY)) (local.get $dy)))
    (local.set $ch (call $at (local.get $nx) (local.get $ny)))
    (if (i32.eq (local.get $ch) (i32.const 35)) (then (return (i32.const 0))))
    (if (i32.or (i32.eq (local.get $ch) (i32.const 36)) (i32.eq (local.get $ch) (i32.const 42)))
      (then
        (local.set $bx (i32.add (local.get $nx) (local.get $dx)))
        (local.set $by (i32.add (local.get $ny) (local.get $dy)))
        (local.set $ch (call $at (local.get $bx) (local.get $by)))
        (if (i32.or (i32.or (i32.eq (local.get $ch) (i32.const 35))
                            (i32.eq (local.get $ch) (i32.const 36)))
                    (i32.eq (local.get $ch) (i32.const 42)))
          (then (return (i32.const 0))))
        (call $push_hist (i32.load (global.get $PX)) (i32.load (global.get $PY))
                         (local.get $nx) (local.get $ny)
                         (local.get $bx) (local.get $by) (i32.const 1))
        (call $set (local.get $nx) (local.get $ny)
          (select (i32.const 46) (i32.const 32)
            (i32.eq (call $at (local.get $nx) (local.get $ny)) (i32.const 42))))
        (call $set (local.get $bx) (local.get $by)
          (select (i32.const 42) (i32.const 36)
            (i32.eq (call $at (local.get $bx) (local.get $by)) (i32.const 46))))
        (i32.store (global.get $PX) (local.get $nx))
        (i32.store (global.get $PY) (local.get $ny))
        (i32.store (global.get $MOVES) (i32.add (i32.load (global.get $MOVES)) (i32.const 1)))
        (call $check_win)
        (return (i32.const 1))))
    (call $push_hist (i32.load (global.get $PX)) (i32.load (global.get $PY))
                     (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 0))
    (i32.store (global.get $PX) (local.get $nx))
    (i32.store (global.get $PY) (local.get $ny))
    (i32.const 1))

  (func $undo (export "undo") (result i32)
    (local $n i32) (local $base i32) (local $push i32)
    (local $px i32) (local $py i32) (local $bfx i32) (local $bfy i32) (local $btx i32) (local $bty i32)
    (if (i32.or (i32.load (global.get $WON)) (i32.eqz (i32.load (global.get $HIST_N))))
      (then (return (i32.const 0))))
    (block $done
      (loop $loop
        (local.set $n (i32.load (global.get $HIST_N)))
        (if (i32.eqz (local.get $n)) (then (br $done)))
        (local.set $n (i32.sub (local.get $n) (i32.const 1)))
        (i32.store (global.get $HIST_N) (local.get $n))
        (local.set $base (i32.add (global.get $HIST_BASE) (i32.mul (local.get $n) (i32.const 28))))
        (local.set $px (i32.load (local.get $base)))
        (local.set $py (i32.load (i32.add (local.get $base) (i32.const 4))))
        (local.set $bfx (i32.load (i32.add (local.get $base) (i32.const 8))))
        (local.set $bfy (i32.load (i32.add (local.get $base) (i32.const 12))))
        (local.set $btx (i32.load (i32.add (local.get $base) (i32.const 16))))
        (local.set $bty (i32.load (i32.add (local.get $base) (i32.const 20))))
        (local.set $push (i32.load (i32.add (local.get $base) (i32.const 24))))
        (if (local.get $push)
          (then
            (i32.store (global.get $PX) (local.get $px))
            (i32.store (global.get $PY) (local.get $py))
            (call $set (local.get $btx) (local.get $bty)
              (select (i32.const 46) (i32.const 32)
                (i32.eq (call $at (local.get $btx) (local.get $bty)) (i32.const 42))))
            (call $set (local.get $bfx) (local.get $bfy)
              (select (i32.const 42) (i32.const 36)
                (i32.eq (call $at (local.get $bfx) (local.get $bfy)) (i32.const 46))))
            (if (i32.gt_s (i32.load (global.get $MOVES)) (i32.const 0))
              (then (i32.store (global.get $MOVES)
                      (i32.sub (i32.load (global.get $MOVES)) (i32.const 1)))))
            (i32.store (global.get $WON) (i32.const 0))
            (return (i32.const 1)))
          (else
            (i32.store (global.get $PX) (local.get $px))
            (i32.store (global.get $PY) (local.get $py))
            (br $loop)))))
    (i32.const 1))

  (func $get_moves (export "get_moves") (result i32) (i32.load (global.get $MOVES)))
  (func $get_won (export "get_won") (result i32) (i32.load (global.get $WON)))
  (func $get_w (export "get_w") (result i32) (i32.load (global.get $W)))
  (func $get_h (export "get_h") (result i32) (i32.load (global.get $H)))
  (func $cell (export "cell") (param $x i32) (param $y i32) (result i32)
    (local $ch i32)
    (local.set $ch (call $at (local.get $x) (local.get $y)))
    (if (i32.and (i32.eq (local.get $x) (i32.load (global.get $PX)))
                 (i32.eq (local.get $y) (i32.load (global.get $PY))))
      (then (return (select (i32.const 43) (i32.const 64)
                      (i32.eq (local.get $ch) (i32.const 46))))))
    (local.get $ch))
)
