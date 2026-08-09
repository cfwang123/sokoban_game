import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/** 推箱子核心逻辑（Java 教学）。 */
public final class Game {
    public static final class Pos {
        public final int x, y;
        public Pos(int x, int y) { this.x = x; this.y = y; }
        public String key() { return x + "," + y; }
        public Pos off(int dx, int dy) { return new Pos(x + dx, y + dy); }
    }

    private static final class Hist {
        final Pos player;
        final String boxFrom, boxTo;
        Hist(Pos player, String boxFrom, String boxTo) {
            this.player = player;
            this.boxFrom = boxFrom;
            this.boxTo = boxTo;
        }
    }

    public final Set<String> walls = new HashSet<>();
    public final Set<String> goals = new HashSet<>();
    public final Set<String> boxes = new HashSet<>();
    public Pos player = new Pos(0, 0);
    public int moves = 0;
    public boolean won = false;
    public int width = 0;
    public int height = 0;
    public int levelIndex = 0;
    private final List<Hist> hist = new ArrayList<>();

    public static Game fromRows(String[] rows, int index) {
        Game g = new Game();
        g.levelIndex = index;
        int maxX = 0, maxY = 0;
        for (int y = 0; y < rows.length; y++) {
            maxY = y;
            String row = rows[y];
            for (int x = 0; x < row.length(); x++) {
                if (x > maxX) maxX = x;
                char ch = row.charAt(x);
                String k = x + "," + y;
                switch (ch) {
                    case '#': g.walls.add(k); break;
                    case '.': g.goals.add(k); break;
                    case '$': g.boxes.add(k); break;
                    case '*': g.boxes.add(k); g.goals.add(k); break;
                    case '@': g.player = new Pos(x, y); break;
                    case '+': g.player = new Pos(x, y); g.goals.add(k); break;
                    default: break;
                }
            }
        }
        g.width = maxX + 1;
        g.height = maxY + 1;
        return g;
    }

    public boolean tryMove(int dx, int dy) {
        if (won) return false;
        Pos n = player.off(dx, dy);
        String nk = n.key();
        if (walls.contains(nk)) return false;
        if (boxes.contains(nk)) {
            Pos b = n.off(dx, dy);
            String bk = b.key();
            if (walls.contains(bk) || boxes.contains(bk)) return false;
            hist.add(new Hist(player, nk, bk));
            boxes.remove(nk);
            boxes.add(bk);
            player = n;
            moves++;
            checkWin();
            return true;
        }
        hist.add(new Hist(player, null, null));
        player = n;
        return true;
    }

    public boolean undo() {
        if (won || hist.isEmpty()) return false;
        Hist e = null;
        while (!hist.isEmpty()) {
            e = hist.remove(hist.size() - 1);
            if (e.boxFrom != null) break;
            player = e.player;
        }
        if (e == null || e.boxFrom == null) return true;
        player = e.player;
        boxes.remove(e.boxTo);
        boxes.add(e.boxFrom);
        if (moves > 0) moves--;
        won = false;
        return true;
    }

    private void checkWin() {
        for (String b : boxes) {
            if (!goals.contains(b)) {
                won = false;
                return;
            }
        }
        won = true;
    }

    public String renderAscii() {
        StringBuilder sb = new StringBuilder();
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                String k = x + "," + y;
                if (player.x == x && player.y == y) {
                    sb.append(goals.contains(k) ? '+' : '@');
                } else if (boxes.contains(k)) {
                    sb.append(goals.contains(k) ? '*' : '$');
                } else if (walls.contains(k)) {
                    sb.append('#');
                } else if (goals.contains(k)) {
                    sb.append('.');
                } else {
                    sb.append(' ');
                }
            }
            sb.append('\n');
        }
        return sb.toString();
    }
}
