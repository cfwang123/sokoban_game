// 推箱子核心逻辑（Groovy 教学）

class Hist {
    int px, py
    String boxFrom, boxTo
    Hist(int px, int py, String boxFrom = null, String boxTo = null) {
        this.px = px; this.py = py; this.boxFrom = boxFrom; this.boxTo = boxTo
    }
}

class GameState {
    Set<String> walls = [] as Set
    Set<String> goals = [] as Set
    Set<String> boxes = [] as Set
    int px = 0, py = 0
    int moves = 0
    boolean won = false
    int width = 0, height = 0
    List<Hist> hist = []

    static String key(int x, int y) { "$x,$y" }

    static GameState fromRows(List<String> rows, int index = 0) {
        def s = new GameState()
        int maxX = 0, maxY = 0
        rows.eachWithIndex { row, y ->
            maxY = y
            row.eachWithIndex { ch, x ->
                if (x > maxX) maxX = x
                def k = key(x, y)
                switch (ch) {
                    case '#': s.walls << k; break
                    case '.': s.goals << k; break
                    case '$': s.boxes << k; break
                    case '*': s.boxes << k; s.goals << k; break
                    case '@': s.px = x; s.py = y; break
                    case '+': s.px = x; s.py = y; s.goals << k; break
                }
            }
        }
        s.width = maxX + 1
        s.height = maxY + 1
        s
    }

    void checkWin() {
        won = boxes.every { goals.contains(it) }
    }

    boolean tryMove(int dx, int dy) {
        if (won) return false
        int nx = px + dx, ny = py + dy
        def nk = key(nx, ny)
        if (walls.contains(nk)) return false
        if (boxes.contains(nk)) {
            int bx = nx + dx, by = ny + dy
            def bk = key(bx, by)
            if (walls.contains(bk) || boxes.contains(bk)) return false
            hist << new Hist(px, py, nk, bk)
            boxes.remove(nk)
            boxes << bk
            px = nx; py = ny
            moves++
            checkWin()
            return true
        }
        hist << new Hist(px, py)
        px = nx; py = ny
        true
    }

    boolean undo() {
        if (won || hist.isEmpty()) return false
        Hist entry = null
        while (!hist.isEmpty()) {
            entry = hist.remove(hist.size() - 1)
            if (entry.boxFrom != null) break
            px = entry.px; py = entry.py
        }
        if (entry == null || entry.boxFrom == null) return true
        px = entry.px; py = entry.py
        boxes.remove(entry.boxTo)
        boxes << entry.boxFrom
        if (moves > 0) moves--
        won = false
        true
    }

    String renderAscii() {
        def sb = new StringBuilder()
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                def k = key(x, y)
                if (px == x && py == y) sb << (goals.contains(k) ? '+' : '@')
                else if (boxes.contains(k)) sb << (goals.contains(k) ? '*' : '$')
                else if (walls.contains(k)) sb << '#'
                else if (goals.contains(k)) sb << '.'
                else sb << ' '
            }
            sb << '\n'
        }
        sb.toString()
    }
}
