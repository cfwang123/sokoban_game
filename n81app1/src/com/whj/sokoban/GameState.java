package com.whj.sokoban;

/**
 * 推箱子运行时状态（对齐 html_app / androidapp1）。
 * <p>
 * 教学说明：J2ME 无 {@code HashSet}，这里用定长 boolean 网格表示墙/目标/箱子。
 */
public final class GameState {
    public final int width;
    public final int height;
    public final int levelIndex;

    public final boolean[] walls;
    public final boolean[] goals;
    public final boolean[] boxes;

    public int playerX;
    public int playerY;
    public int moves;
    public boolean won;

    /** 历史：每步 5 个 int：px,py,boxFrom,boxTo,isPush(0/1) */
    private final IntStack history = new IntStack(256);

    private GameState(int w, int h, int levelIndex) {
        this.width = w;
        this.height = h;
        this.levelIndex = levelIndex;
        int n = w * h;
        walls = new boolean[n];
        goals = new boolean[n];
        boxes = new boolean[n];
    }

    public int idx(int x, int y) {
        return y * width + x;
    }

    public boolean inBounds(int x, int y) {
        return x >= 0 && y >= 0 && x < width && y < height;
    }

    public boolean tryMove(int dx, int dy) {
        if (won) {
            return false;
        }
        int nx = playerX + dx;
        int ny = playerY + dy;
        if (!inBounds(nx, ny) || walls[idx(nx, ny)]) {
            return false;
        }

        int nIdx = idx(nx, ny);
        if (boxes[nIdx]) {
            int bx = nx + dx;
            int by = ny + dy;
            if (!inBounds(bx, by) || walls[idx(bx, by)] || boxes[idx(bx, by)]) {
                return false;
            }
            history.push(playerX);
            history.push(playerY);
            history.push(nIdx);
            history.push(idx(bx, by));
            history.push(1);

            boxes[nIdx] = false;
            boxes[idx(bx, by)] = true;
            playerX = nx;
            playerY = ny;
            moves++;
            checkWin();
            return true;
        }

        history.push(playerX);
        history.push(playerY);
        history.push(-1);
        history.push(-1);
        history.push(0);
        playerX = nx;
        playerY = ny;
        return true;
    }

    public boolean tryMoveDir(int dir) {
        if (dir < 0 || dir > 3) {
            return false;
        }
        return tryMove(Direction.DX[dir], Direction.DY[dir]);
    }

    /**
     * 撤销：跳过纯移动，只撤销最近一次推箱（与网页版一致）。
     */
    public boolean undo() {
        if (won || history.size() == 0) {
            return false;
        }
        int isPush = 0;
        int boxFrom = -1;
        int boxTo = -1;
        int px = playerX;
        int py = playerY;
        while (history.size() >= 5) {
            isPush = history.pop();
            boxTo = history.pop();
            boxFrom = history.pop();
            py = history.pop();
            px = history.pop();
            if (isPush == 1) {
                break;
            }
            playerX = px;
            playerY = py;
        }
        if (isPush != 1 || boxFrom < 0 || boxTo < 0) {
            return true;
        }
        playerX = px;
        playerY = py;
        boxes[boxTo] = false;
        boxes[boxFrom] = true;
        if (moves > 0) {
            moves--;
        }
        won = false;
        return true;
    }

    private void checkWin() {
        for (int i = 0; i < boxes.length; i++) {
            if (boxes[i] && !goals[i]) {
                won = false;
                return;
            }
        }
        won = true;
    }

    public static GameState fromLevel(int levelIndex) {
        String[] rows = LevelsData.puzzle(levelIndex);
        int h = rows.length;
        int w = 0;
        for (int i = 0; i < h; i++) {
            if (rows[i].length() > w) {
                w = rows[i].length();
            }
        }
        GameState s = new GameState(w, h, levelIndex);
        s.playerX = 0;
        s.playerY = 0;
        for (int y = 0; y < h; y++) {
            String row = rows[y];
            for (int x = 0; x < row.length(); x++) {
                char ch = row.charAt(x);
                int i = s.idx(x, y);
                switch (ch) {
                    case '#':
                        s.walls[i] = true;
                        break;
                    case '.':
                        s.goals[i] = true;
                        break;
                    case '$':
                        s.boxes[i] = true;
                        break;
                    case '*':
                        s.boxes[i] = true;
                        s.goals[i] = true;
                        break;
                    case '@':
                        s.playerX = x;
                        s.playerY = y;
                        break;
                    case '+':
                        s.playerX = x;
                        s.playerY = y;
                        s.goals[i] = true;
                        break;
                    default:
                        break;
                }
            }
        }
        return s;
    }

    /** 简易 int 栈，避免 java.util（部分配置下可用，但教学用自写更清晰）。 */
    private static final class IntStack {
        private int[] data;
        private int top;

        IntStack(int cap) {
            data = new int[cap];
            top = 0;
        }

        void push(int v) {
            if (top >= data.length) {
                int[] n = new int[data.length * 2];
                System.arraycopy(data, 0, n, 0, data.length);
                data = n;
            }
            data[top++] = v;
        }

        int pop() {
            return data[--top];
        }

        int size() {
            return top;
        }
    }
}
