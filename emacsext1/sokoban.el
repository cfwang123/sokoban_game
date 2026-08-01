;;; sokoban.el --- Teaching demo: Sokoban in Emacs -*- lexical-binding: t; -*-

;; Author: sokoban teaching ports
;; Version: 1.0.0
;; Keywords: games
;; Package-Requires: ((emacs "26.1"))

;;; Commentary:

;; M-x sokoban  打开游戏缓冲。
;; 键位: h/j/k/l 或方向键移动, u 撤销, r 重置, n/p 换关, q 退出。

;;; Code:

(defgroup sokoban nil
  "Sokoban teaching game."
  :group 'games)

(defvar sokoban-levels
  '(("###" "#@#" "#$#" "#.#" "###")
    ("#####" "#.$@#" "#####")
    ("###" "#.###" "#*$-#" "#--@#" "#####"))
  "List of levels; each level is a list of row strings.")

(defvar-local sokoban--level 0)
(defvar-local sokoban--moves 0)
(defvar-local sokoban--won nil)
(defvar-local sokoban--px 0)
(defvar-local sokoban--py 0)
(defvar-local sokoban--w 0)
(defvar-local sokoban--h 0)
(defvar-local sokoban--walls nil)
(defvar-local sokoban--goals nil)
(defvar-local sokoban--boxes nil)
(defvar-local sokoban--hist nil)

(defun sokoban--key (x y)
  (format "%d,%d" x y))

(defun sokoban--parse (rows)
  (setq sokoban--walls (make-hash-table :test 'equal)
        sokoban--goals (make-hash-table :test 'equal)
        sokoban--boxes (make-hash-table :test 'equal)
        sokoban--hist nil
        sokoban--moves 0
        sokoban--won nil
        sokoban--h (length rows)
        sokoban--w 0)
  (let ((y 0))
    (dolist (row rows)
      (let ((x 0))
        (dolist (ch (append row nil))
          (setq sokoban--w (max sokoban--w (1+ x)))
          (let ((k (sokoban--key x y)))
            (cond
             ((eq ch ?#) (puthash k t sokoban--walls))
             ((eq ch ?.) (puthash k t sokoban--goals))
             ((eq ch ?$) (puthash k t sokoban--boxes))
             ((eq ch ?*)
              (puthash k t sokoban--boxes)
              (puthash k t sokoban--goals))
             ((eq ch ?@)
              (setq sokoban--px x sokoban--py y))
             ((eq ch ?+)
              (setq sokoban--px x sokoban--py y)
              (puthash k t sokoban--goals))))
          (setq x (1+ x))))
      (setq y (1+ y)))))

(defun sokoban--check-win ()
  (setq sokoban--won t)
  (maphash
   (lambda (k _)
     (unless (gethash k sokoban--goals)
       (setq sokoban--won nil)))
   sokoban--boxes))

(defun sokoban--try-move (dx dy)
  (unless sokoban--won
    (let* ((nx (+ sokoban--px dx))
           (ny (+ sokoban--py dy))
           (nk (sokoban--key nx ny)))
      (unless (gethash nk sokoban--walls)
        (if (gethash nk sokoban--boxes)
            (let ((bk (sokoban--key (+ nx dx) (+ ny dy))))
              (unless (or (gethash bk sokoban--walls)
                          (gethash bk sokoban--boxes))
                (push (list sokoban--px sokoban--py nk bk t) sokoban--hist)
                (remhash nk sokoban--boxes)
                (puthash bk t sokoban--boxes)
                (setq sokoban--px nx
                      sokoban--py ny
                      sokoban--moves (1+ sokoban--moves))
                (sokoban--check-win)))
          (push (list sokoban--px sokoban--py nil nil nil) sokoban--hist)
          (setq sokoban--px nx sokoban--py ny))))))

(defun sokoban--undo ()
  "Undo last push (skip pure walks), matching html_app."
  (when (and (not sokoban--won) sokoban--hist)
    (let ((done nil))
      (while (and sokoban--hist (not done))
        (let ((e (pop sokoban--hist)))
          (if (nth 4 e)
              (progn
                (setq sokoban--px (nth 0 e)
                      sokoban--py (nth 1 e))
                (remhash (nth 3 e) sokoban--boxes)
                (puthash (nth 2 e) t sokoban--boxes)
                (when (> sokoban--moves 0)
                  (setq sokoban--moves (1- sokoban--moves)))
                (setq sokoban--won nil
                      done t))
            (setq sokoban--px (nth 0 e)
                  sokoban--py (nth 1 e))))))))

(defun sokoban--render ()
  (let (lines)
    (dotimes (y sokoban--h)
      (let ((row ""))
        (dotimes (x sokoban--w)
          (let ((k (sokoban--key x y)))
            (setq row
                  (concat row
                          (cond
                           ((and (= x sokoban--px) (= y sokoban--py))
                            (if (gethash k sokoban--goals) "+" "@"))
                           ((gethash k sokoban--boxes)
                            (if (gethash k sokoban--goals) "*" "$"))
                           ((gethash k sokoban--walls) "#")
                           ((gethash k sokoban--goals) ".")
                           (t " "))))))
        (push row lines)))
    (setq lines (nreverse lines))
    (append lines
            (list ""
                  (format "LV%d/%d  moves:%d%s"
                          (1+ sokoban--level)
                          (length sokoban-levels)
                          sokoban--moves
                          (if sokoban--won "  WIN!" ""))
                  "h/j/k/l move | u undo | r reset | n/p level | q quit"))))

(defun sokoban--redraw ()
  (let ((inhibit-read-only t))
    (erase-buffer)
    (dolist (line (sokoban--render))
      (insert line "\n"))
    (goto-char (point-min))))

(defun sokoban--load (i)
  (setq sokoban--level (max 0 (min (1- (length sokoban-levels)) i)))
  (sokoban--parse (nth sokoban--level sokoban-levels))
  (sokoban--redraw))

(defun sokoban-move (dx dy)
  "Move player by DX DY."
  (interactive)
  (sokoban--try-move dx dy)
  (sokoban--redraw))

(defun sokoban-undo-cmd ()
  (interactive)
  (sokoban--undo)
  (sokoban--redraw))

(defun sokoban-reset ()
  (interactive)
  (sokoban--load sokoban--level))

(defun sokoban-next ()
  (interactive)
  (sokoban--load (1+ sokoban--level)))

(defun sokoban-prev ()
  (interactive)
  (sokoban--load (1- sokoban--level)))

(defvar sokoban-mode-map
  (let ((map (make-sparse-keymap)))
    (define-key map (kbd "h") (lambda () (interactive) (sokoban-move -1 0)))
    (define-key map (kbd "l") (lambda () (interactive) (sokoban-move 1 0)))
    (define-key map (kbd "k") (lambda () (interactive) (sokoban-move 0 -1)))
    (define-key map (kbd "j") (lambda () (interactive) (sokoban-move 0 1)))
    (define-key map (kbd "<left>") (lambda () (interactive) (sokoban-move -1 0)))
    (define-key map (kbd "<right>") (lambda () (interactive) (sokoban-move 1 0)))
    (define-key map (kbd "<up>") (lambda () (interactive) (sokoban-move 0 -1)))
    (define-key map (kbd "<down>") (lambda () (interactive) (sokoban-move 0 1)))
    (define-key map (kbd "u") #'sokoban-undo-cmd)
    (define-key map (kbd "r") #'sokoban-reset)
    (define-key map (kbd "n") #'sokoban-next)
    (define-key map (kbd "p") #'sokoban-prev)
    (define-key map (kbd "q") #'kill-this-buffer)
    map)
  "Keymap for Sokoban mode.")

(define-derived-mode sokoban-mode special-mode "Sokoban"
  "Major mode for the Sokoban teaching game."
  (setq buffer-read-only t)
  (sokoban--load 0))

;;;###autoload
(defun sokoban ()
  "Play Sokoban in a new buffer."
  (interactive)
  (switch-to-buffer (get-buffer-create "*Sokoban*"))
  (sokoban-mode))

(provide 'sokoban)
;;; sokoban.el ends here
