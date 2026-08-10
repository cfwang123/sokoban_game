;; 推箱子核心逻辑（Clojure 教学）
(ns game)

(defn cell-key [x y] (str x "," y))

(defn from-rows
  ([rows] (from-rows rows 0))
  ([rows _index]
   (let [parsed
         (reduce
          (fn [acc [y row]]
            (reduce
             (fn [a [x ch]]
               (let [k (cell-key x y)]
                 (case ch
                   \# (update a :walls conj k)
                   \. (update a :goals conj k)
                   \$ (update a :boxes conj k)
                   \* (-> a (update :boxes conj k) (update :goals conj k))
                   \@ (assoc a :px x :py y)
                   \+ (-> a (assoc :px x :py y) (update :goals conj k))
                   a)))
             (assoc acc :max-y y :max-x (max (:max-x acc 0) (dec (count row))))
             (map-indexed vector row)))
          {:walls #{} :goals #{} :boxes #{} :px 0 :py 0 :max-x 0 :max-y 0}
          (map-indexed vector rows))]
     {:walls (:walls parsed)
      :goals (:goals parsed)
      :boxes (:boxes parsed)
      :px (:px parsed)
      :py (:py parsed)
      :moves 0
      :won false
      :width (inc (:max-x parsed))
      :height (inc (:max-y parsed))
      :hist []})))

(defn check-win [boxes goals]
  (every? #(contains? goals %) boxes))

(defn try-move [s dx dy]
  (if (:won s)
    s
    (let [px (:px s) py (:py s)
          nx (+ px dx) ny (+ py dy)
          nk (cell-key nx ny)]
      (cond
        (contains? (:walls s) nk) s
        (contains? (:boxes s) nk)
        (let [bx (+ nx dx) by (+ ny dy) bk (cell-key bx by)]
          (if (or (contains? (:walls s) bk) (contains? (:boxes s) bk))
            s
            (let [boxes (-> (:boxes s) (disj nk) (conj bk))]
              (assoc s
                     :boxes boxes
                     :px nx :py ny
                     :moves (inc (:moves s))
                     :won (check-win boxes (:goals s))
                     :hist (conj (:hist s) {:px px :py py :box-from nk :box-to bk})))))
        :else
        (assoc s :px nx :py ny
               :hist (conj (:hist s) {:px px :py py :box-from nil :box-to nil}))))))

(defn undo [s]
  (if (or (:won s) (empty? (:hist s)))
    s
    (loop [hist (:hist s)
           px (:px s) py (:py s)
           boxes (:boxes s)
           moves (:moves s)]
      (if (empty? hist)
        (assoc s :px px :py py :boxes boxes :moves moves :won false :hist [])
        (let [e (peek hist)
              rest (pop hist)]
          (if (:box-from e)
            (assoc s
                   :px (:px e) :py (:py e)
                   :boxes (-> boxes (disj (:box-to e)) (conj (:box-from e)))
                   :moves (max 0 (dec moves))
                   :won false
                   :hist rest)
            (recur rest (:px e) (:py e) boxes moves)))))))

(defn render-ascii [s]
  (let [sb (StringBuilder.)]
    (doseq [y (range (:height s))
            x (range (:width s))]
      (let [k (cell-key x y)
            ch (cond
                 (and (= x (:px s)) (= y (:py s)))
                 (if (contains? (:goals s) k) \+ \@)
                 (contains? (:boxes s) k)
                 (if (contains? (:goals s) k) \* \$)
                 (contains? (:walls s) k) \#
                 (contains? (:goals s) k) \.
                 :else \space)]
        (.append sb ch)
        (when (= x (dec (:width s))) (.append sb \newline))))
    (str sb)))
