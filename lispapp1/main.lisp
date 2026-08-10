;;;; lispapp1 — Common Lisp 推箱子终端版（教学）
;;;; 运行: sbcl --script main.lisp
;;;;   或: clisp main.lisp

(load (merge-pathnames "game.lisp" *load-truename*))

(in-package :cl-user)
(use-package :sokoban-game)

(defparameter *level*
  '("#######"
    "#. . .#"
    "# $$$ #"
    "#.$@$.#"
    "# $$$ #"
    "#. . .#"
    "#######"))

(defun main ()
  (let ((state (from-rows *level* 0)))
    (format t "sokoban_lisp — wasd 移动, z 撤销, r 重置, q 退出~%")
    (loop
      (format t "~%")
      (format t "~A" (render-ascii state))
      (format t "moves=~A~A~%"
              (game-moves state)
              (if (game-won state) " WIN!" ""))
      (format t "> ")
      (force-output)
      (let ((line (read-line *standard-input* nil nil)))
        (unless line (return))
        (let* ((trimmed (string-trim '(#\Space #\Tab) line)))
          (when (plusp (length trimmed))
            (let ((ch (char-downcase (char trimmed 0))))
              (case ch
                (#\w (try-move state 0 -1))
                (#\s (try-move state 0 1))
                (#\a (try-move state -1 0))
                (#\d (try-move state 1 0))
                (#\z (undo state))
                (#\r (setf state (from-rows *level* 0)))
                (#\q (return)))
              (when (game-won state)
                (format t "Level clear!~%")))))))))

(main)
