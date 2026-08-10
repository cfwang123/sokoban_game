;;;; schemeapp1 — Scheme 推箱子终端版（教学）
;;;; 运行: guile -l game.scm -s main.scm
;;;;   或: csi -s main.scm   (CHICKEN, 需先 load game)
;;;;   或: gosh -l game.scm main.scm

(load "game.scm")

;; 可移植 read-line（不依赖 Guile ice-9 / R7RS）
(define (read-line-portable)
  (let loop ((chars '()))
    (let ((c (read-char)))
      (cond
       ((eof-object? c)
        (if (null? chars) c (list->string (reverse chars))))
       ((char=? c #\newline)
        (list->string (reverse chars)))
       ((char=? c #\return)
        (let ((n (peek-char)))
          (if (and (not (eof-object? n)) (char=? n #\newline))
              (read-char))
          (list->string (reverse chars))))
       (else (loop (cons c chars)))))))

(define *level*
  '("#######"
    "#. . .#"
    "# $$$ #"
    "#.$@$.#"
    "# $$$ #"
    "#. . .#"
    "#######"))

(define (char-downcase-safe c)
  (if (and (char>=? c #\A) (char<=? c #\Z))
      (integer->char (+ (char->integer c) 32))
      c))

(define (main)
  (let ((state (from-rows *level*)))
    (display "sokoban_scheme — wasd 移动, z 撤销, r 重置, q 退出")
    (newline)
    (let loop ((state state))
      (newline)
      (display (render-ascii state))
      (display "moves=")
      (display (st-moves state))
      (if (st-won state) (display " WIN!"))
      (newline)
      (display "> ")
      (let ((line (read-line-portable)))
        (if (eof-object? line)
            #t
            (let* ((trimmed (let ((s line))
                              ;; 简单去空白：取首字符
                              s))
                   (ch (if (zero? (string-length trimmed))
                           #\space
                           (char-downcase-safe (string-ref trimmed 0)))))
              (cond
               ((char=? ch #\q) #t)
               (else
                (let ((state2
                       (cond
                        ((char=? ch #\w) (try-move state 0 -1))
                        ((char=? ch #\s) (try-move state 0 1))
                        ((char=? ch #\a) (try-move state -1 0))
                        ((char=? ch #\d) (try-move state 1 0))
                        ((char=? ch #\z) (undo state))
                        ((char=? ch #\r) (from-rows *level*))
                        (else state))))
                  (if (st-won state2)
                      (begin (display "Level clear!") (newline)))
                  (loop state2))))))))))

(main)
