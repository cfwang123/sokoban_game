;; clojureapp1 — Clojure 推箱子终端版（教学）
;; 运行: clojure -M main.clj
;; 或: clj -M main.clj

(load-file (str (.getParent (java.io.File. *file*)) "/game.clj"))
(require '[game :as g])

(def level
  ["#######"
   "#. . .#"
   "# $$$ #"
   "#.$@$.#"
   "# $$$ #"
   "#. . .#"
   "#######"])

(defn -main []
  (println "sokoban_clojure — wasd 移动, z 撤销, r 重置, q 退出")
  (loop [state (g/from-rows level 0)]
    (println)
    (print (g/render-ascii state))
    (print (str "moves=" (:moves state) (when (:won state) " WIN!") "\n> "))
    (flush)
    (let [line (read-line)]
      (if (nil? line)
        nil
        (let [line (clojure.string/trim line)]
          (if (empty? line)
            (recur state)
            (let [ch (Character/toLowerCase (first line))
                  state2 (case ch
                           \w (g/try-move state 0 -1)
                           \s (g/try-move state 0 1)
                           \a (g/try-move state -1 0)
                           \d (g/try-move state 1 0)
                           \z (g/undo state)
                           \r (g/from-rows level 0)
                           \q :quit
                           state)]
              (if (= state2 :quit)
                nil
                (do
                  (when (:won state2) (println "Level clear!"))
                  (recur state2))))))))))

(-main)
