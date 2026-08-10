;;;; 推箱子核心逻辑（Scheme 教学，R5RS 兼容：Guile / CHICKEN / Gauche）

(define (cell-key x y)
  (string-append (number->string x) "," (number->string y)))

(define (set-has? s k)
  (member k s))

(define (set-add s k)
  (if (member k s) s (cons k s)))

(define (set-del s k)
  (cond
   ((null? s) '())
   ((equal? (car s) k) (cdr s))
   (else (cons (car s) (set-del (cdr s) k)))))

;; state: (walls goals boxes px py moves won width height hist)
(define (st-walls s) (list-ref s 0))
(define (st-goals s) (list-ref s 1))
(define (st-boxes s) (list-ref s 2))
(define (st-px s) (list-ref s 3))
(define (st-py s) (list-ref s 4))
(define (st-moves s) (list-ref s 5))
(define (st-won s) (list-ref s 6))
(define (st-width s) (list-ref s 7))
(define (st-height s) (list-ref s 8))
(define (st-hist s) (list-ref s 9))

(define (make-state walls goals boxes px py moves won width height hist)
  (list walls goals boxes px py moves won width height hist))

(define (from-rows rows)
  (let ((walls '()) (goals '()) (boxes '())
        (px 0) (py 0) (max-x 0) (max-y 0) (y 0))
    (for-each
     (lambda (row)
       (set! max-y y)
       (let ((len (string-length row)))
         (do ((x 0 (+ x 1)))
             ((>= x len))
           (if (> x max-x) (set! max-x x))
           (let ((ch (string-ref row x))
                 (k (cell-key x y)))
             (cond
              ((char=? ch #\#) (set! walls (set-add walls k)))
              ((char=? ch #\.) (set! goals (set-add goals k)))
              ((char=? ch #\$) (set! boxes (set-add boxes k)))
              ((char=? ch #\*)
               (set! boxes (set-add boxes k))
               (set! goals (set-add goals k)))
              ((char=? ch #\@)
               (set! px x) (set! py y))
              ((char=? ch #\+)
               (set! px x) (set! py y)
               (set! goals (set-add goals k)))))))
       (set! y (+ y 1)))
     rows)
    (make-state walls goals boxes px py 0 #f
                (+ max-x 1) (+ max-y 1) '())))

(define (check-win boxes goals)
  (let loop ((bs boxes))
    (cond
     ((null? bs) #t)
     ((set-has? goals (car bs)) (loop (cdr bs)))
     (else #f))))

(define (try-move s dx dy)
  (if (st-won s)
      s
      (let* ((px (st-px s))
             (py (st-py s))
             (nx (+ px dx))
             (ny (+ py dy))
             (nk (cell-key nx ny))
             (walls (st-walls s))
             (goals (st-goals s))
             (boxes (st-boxes s)))
        (cond
         ((set-has? walls nk) s)
         ((set-has? boxes nk)
          (let* ((bx (+ nx dx))
                 (by (+ ny dy))
                 (bk (cell-key bx by)))
            (if (or (set-has? walls bk) (set-has? boxes bk))
                s
                (let* ((boxes2 (set-add (set-del boxes nk) bk))
                       (won2 (check-win boxes2 goals)))
                  (make-state walls goals boxes2 nx ny
                              (+ (st-moves s) 1) won2
                              (st-width s) (st-height s)
                              (cons (list px py nk bk) (st-hist s)))))))
         (else
          (make-state walls goals boxes nx ny
                      (st-moves s) #f
                      (st-width s) (st-height s)
                      (cons (list px py #f #f) (st-hist s))))))))

(define (undo s)
  (if (or (st-won s) (null? (st-hist s)))
      s
      (let loop ((hist (st-hist s)) (px (st-px s)) (py (st-py s))
                 (boxes (st-boxes s)) (moves (st-moves s)))
        (if (null? hist)
            (make-state (st-walls s) (st-goals s) boxes px py moves #f
                        (st-width s) (st-height s) '())
            (let* ((e (car hist))
                   (rest (cdr hist))
                   (hx (list-ref e 0))
                   (hy (list-ref e 1))
                   (bf (list-ref e 2))
                   (bt (list-ref e 3)))
              (if bf
                  (make-state (st-walls s) (st-goals s)
                              (set-add (set-del boxes bt) bf)
                              hx hy
                              (if (> moves 0) (- moves 1) 0)
                              #f
                              (st-width s) (st-height s) rest)
                  (loop rest hx hy boxes moves)))))))

(define (render-ascii s)
  (let ((out ""))
    (do ((y 0 (+ y 1)))
        ((>= y (st-height s)))
      (do ((x 0 (+ x 1)))
          ((>= x (st-width s)))
        (let ((k (cell-key x y))
              (ch #\space))
          (cond
           ((and (= x (st-px s)) (= y (st-py s)))
            (set! ch (if (set-has? (st-goals s) k) #\+ #\@)))
           ((set-has? (st-boxes s) k)
            (set! ch (if (set-has? (st-goals s) k) #\* #\$)))
           ((set-has? (st-walls s) k)
            (set! ch #\#))
           ((set-has? (st-goals s) k)
            (set! ch #\.)))
          (set! out (string-append out (string ch)))))
      (set! out (string-append out "\n")))
    out))
