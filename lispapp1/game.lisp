;;;; 推箱子核心逻辑（Common Lisp 教学）

(defpackage :sokoban-game
  (:use :cl)
  (:export :from-rows :try-move :undo :render-ascii
           :game-moves :game-won :make-game-copy))

(in-package :sokoban-game)

(defstruct game
  walls goals boxes
  player-x player-y
  moves won
  width height
  level-index
  hist)

(defun cell-key (x y)
  (format nil "~A,~A" x y))

(defun from-rows (rows &optional (index 0))
  (let ((walls (make-hash-table :test #'equal))
        (goals (make-hash-table :test #'equal))
        (boxes (make-hash-table :test #'equal))
        (px 0) (py 0)
        (max-x 0) (max-y 0))
    (loop for y from 0
          for row in rows
          do (setf max-y y)
             (loop for x from 0 below (length row)
                   for ch = (char row x)
                   do (when (> x max-x) (setf max-x x))
                      (let ((k (cell-key x y)))
                        (case ch
                          (#\# (setf (gethash k walls) t))
                          (#\. (setf (gethash k goals) t))
                          (#\$ (setf (gethash k boxes) t))
                          (#\* (setf (gethash k boxes) t
                                     (gethash k goals) t))
                          (#\@ (setf px x py y))
                          (#\+ (setf px x py y
                                     (gethash k goals) t))))))
    (make-game :walls walls :goals goals :boxes boxes
               :player-x px :player-y py
               :moves 0 :won nil
               :width (1+ max-x) :height (1+ max-y)
               :level-index index :hist nil)))

(defun check-win (g)
  (setf (game-won g)
        (loop for k being the hash-keys of (game-boxes g)
              always (gethash k (game-goals g)))))

(defun try-move (g dx dy)
  (when (game-won g)
    (return-from try-move nil))
  (let* ((px (game-player-x g))
         (py (game-player-y g))
         (nx (+ px dx))
         (ny (+ py dy))
         (nk (cell-key nx ny)))
    (when (gethash nk (game-walls g))
      (return-from try-move nil))
    (if (gethash nk (game-boxes g))
        (let* ((bx (+ nx dx))
               (by (+ ny dy))
               (bk (cell-key bx by)))
          (when (or (gethash bk (game-walls g))
                    (gethash bk (game-boxes g)))
            (return-from try-move nil))
          (push (list px py nk bk) (game-hist g))
          (remhash nk (game-boxes g))
          (setf (gethash bk (game-boxes g)) t)
          (setf (game-player-x g) nx
                (game-player-y g) ny)
          (incf (game-moves g))
          (check-win g)
          t)
        (progn
          (push (list px py nil nil) (game-hist g))
          (setf (game-player-x g) nx
                (game-player-y g) ny)
          t))))

(defun undo (g)
  (when (or (game-won g) (null (game-hist g)))
    (return-from undo nil))
  (let (entry)
    (loop while (game-hist g)
          do (setf entry (pop (game-hist g)))
             (destructuring-bind (hx hy box-from box-to) entry
               (when box-from
                 (setf (game-player-x g) hx
                       (game-player-y g) hy)
                 (remhash box-to (game-boxes g))
                 (setf (gethash box-from (game-boxes g)) t)
                 (when (> (game-moves g) 0)
                   (decf (game-moves g)))
                 (setf (game-won g) nil)
                 (return-from undo t))
               (setf (game-player-x g) hx
                     (game-player-y g) hy)))
    t))

(defun render-ascii (g)
  (with-output-to-string (out)
    (dotimes (y (game-height g))
      (dotimes (x (game-width g))
        (let ((k (cell-key x y)))
          (cond
            ((and (= x (game-player-x g)) (= y (game-player-y g)))
             (write-char (if (gethash k (game-goals g)) #\+ #\@) out))
            ((gethash k (game-boxes g))
             (write-char (if (gethash k (game-goals g)) #\* #\$) out))
            ((gethash k (game-walls g))
             (write-char #\# out))
            ((gethash k (game-goals g))
             (write-char #\. out))
            (t (write-char #\Space out)))))
      (terpri out))))
