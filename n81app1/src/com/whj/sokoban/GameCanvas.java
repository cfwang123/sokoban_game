package com.whj.sokoban;

import javax.microedition.lcdui.Canvas;
import javax.microedition.lcdui.Font;
import javax.microedition.lcdui.Graphics;

/**
 * 游戏画面与按键处理。
 * <p>
 * 教学对照：
 * <ul>
 *   <li>Android {@code GameBoardView.onDraw} / iOS {@code Canvas}</li>
 *   <li>HTML {@code <canvas>} + keydown</li>
 * </ul>
 * Nokia N81：方向键 / 2,4,6,8 移动；软键与数字键做功能。
 */
public final class GameCanvas extends Canvas implements Runnable {
    private final SokobanMIDlet midlet;

    private GameState state;
    private String status = "";
    private boolean answerActive;
    private boolean inputLocked;

    private int[] animQueue = new int[512];
    private int animLen;
    private int animPos;
    private Thread animThread;
    private volatile boolean animRunning;

    private static final int COLOR_BG = 0x1A1A2E;
    private static final int COLOR_PANEL = 0x16213E;
    private static final int COLOR_FLOOR = 0x3A3A55;
    private static final int COLOR_WALL = 0x4A4A6A;
    private static final int COLOR_GOAL = 0xE94560;
    private static final int COLOR_BOX = 0xF39C12;
    private static final int COLOR_BOX_OK = 0x2ECC71;
    private static final int COLOR_PLAYER = 0x3498DB;
    private static final int COLOR_TEXT = 0xEEEEEE;
    private static final int COLOR_MUTED = 0xAAAAAA;
    private static final int COLOR_ACCENT = 0xE94560;

    public GameCanvas(SokobanMIDlet midlet) {
        this.midlet = midlet;
        setFullScreenMode(true);
        loadLevel(Prefs.loadLastLevel());
    }

    public void loadLevel(int index) {
        stopAnswer(true);
        if (index < 0) {
            index = 0;
        }
        if (index >= LevelsData.COUNT) {
            index = LevelsData.COUNT - 1;
        }
        state = GameState.fromLevel(index);
        Prefs.saveLastLevel(index);
        refreshStatus();
        repaint();
    }

    private void refreshStatus() {
        if (answerActive) {
            return;
        }
        if (state == null) {
            status = "";
            return;
        }
        if (state.won) {
            status = "已过关 右软键下一关";
        } else if (LevelsData.hasSolution(state.levelIndex)) {
            status = "本关有答案 *查看";
        } else {
            status = "本关暂无答案";
        }
    }

    protected void paint(Graphics g) {
        int w = getWidth();
        int h = getHeight();
        g.setColor(COLOR_BG);
        g.fillRect(0, 0, w, h);

        // 顶栏
        g.setColor(COLOR_PANEL);
        g.fillRect(0, 0, w, 36);
        g.setColor(COLOR_TEXT);
        g.setFont(Font.getFont(Font.FACE_SYSTEM, Font.STYLE_BOLD, Font.SIZE_SMALL));
        String title = "推箱子";
        if (state != null) {
            title = (state.levelIndex + 1) + "/" + LevelsData.COUNT
                    + " " + LevelsData.name(state.levelIndex);
        }
        g.drawString(title, 4, 2, Graphics.TOP | Graphics.LEFT);
        g.setColor(COLOR_MUTED);
        g.setFont(Font.getDefaultFont());
        String moves = state == null ? "步:0" : ("步:" + state.moves);
        g.drawString(moves, w - 4, 2, Graphics.TOP | Graphics.RIGHT);
        g.setColor(COLOR_MUTED);
        g.drawString(status, 4, 18, Graphics.TOP | Graphics.LEFT);

        // 棋盘区域
        int boardTop = 40;
        int boardBottom = h - 22;
        int boardH = boardBottom - boardTop;
        if (state != null && state.width > 0 && state.height > 0) {
            int cell = Math.min(w / state.width, boardH / state.height);
            if (cell < 6) {
                cell = 6;
            }
            int boardW = cell * state.width;
            int boardHt = cell * state.height;
            int ox = (w - boardW) / 2;
            int oy = boardTop + (boardH - boardHt) / 2;
            drawBoard(g, ox, oy, cell);
        }

        // 底栏软键提示
        g.setColor(COLOR_PANEL);
        g.fillRect(0, h - 20, w, 20);
        g.setColor(COLOR_TEXT);
        g.setFont(Font.getFont(Font.FACE_SYSTEM, Font.STYLE_PLAIN, Font.SIZE_SMALL));
        g.drawString("撤销/重置", 4, h - 18, Graphics.TOP | Graphics.LEFT);
        g.drawString("下一关/菜单", w - 4, h - 18, Graphics.TOP | Graphics.RIGHT);

        if (state != null && state.won) {
            drawWinBanner(g, w, h);
        }
    }

    private void drawBoard(Graphics g, int ox, int oy, int cell) {
        for (int y = 0; y < state.height; y++) {
            for (int x = 0; x < state.width; x++) {
                int i = state.idx(x, y);
                int px = ox + x * cell;
                int py = oy + y * cell;
                if (state.walls[i]) {
                    g.setColor(COLOR_WALL);
                    g.fillRect(px, py, cell, cell);
                } else {
                    g.setColor(COLOR_FLOOR);
                    g.fillRect(px, py, cell, cell);
                    g.setColor(0x444466);
                    g.drawRect(px, py, cell - 1, cell - 1);
                }
                if (state.goals[i] && !state.walls[i]) {
                    g.setColor(COLOR_GOAL);
                    int r = Math.max(2, cell / 5);
                    g.fillArc(px + cell / 2 - r, py + cell / 2 - r, r * 2, r * 2, 0, 360);
                }
                if (state.boxes[i]) {
                    g.setColor(state.goals[i] ? COLOR_BOX_OK : COLOR_BOX);
                    int m = Math.max(1, cell / 8);
                    g.fillRect(px + m, py + m, cell - m * 2, cell - m * 2);
                }
            }
        }
        // 玩家
        int px = ox + state.playerX * cell + cell / 2;
        int py = oy + state.playerY * cell + cell / 2;
        int r = Math.max(3, cell * 35 / 100);
        g.setColor(COLOR_PLAYER);
        g.fillArc(px - r, py - r, r * 2, r * 2, 0, 360);
    }

    private void drawWinBanner(Graphics g, int w, int h) {
        // MIDP setColor 为 0x00RRGGBB，无 alpha
        int bw = Math.min(w - 20, 200);
        int bh = 70;
        int bx = (w - bw) / 2;
        int by = (h - bh) / 2;
        g.setColor(COLOR_PANEL);
        g.fillRect(bx, by, bw, bh);
        g.setColor(COLOR_ACCENT);
        g.drawRect(bx, by, bw - 1, bh - 1);
        g.setFont(Font.getFont(Font.FACE_SYSTEM, Font.STYLE_BOLD, Font.SIZE_MEDIUM));
        g.drawString("恭喜过关!", w / 2, by + 12, Graphics.TOP | Graphics.HCENTER);
        g.setColor(COLOR_MUTED);
        g.setFont(Font.getDefaultFont());
        g.drawString("共用 " + state.moves + " 步", w / 2, by + 34, Graphics.TOP | Graphics.HCENTER);
        g.drawString("右软键:下一关", w / 2, by + 50, Graphics.TOP | Graphics.HCENTER);
    }

    protected void keyPressed(int keyCode) {
        if (state == null) {
            return;
        }
        int action = getGameAction(keyCode);

        // 菜单注入的逻辑键（同包调用 protected keyPressed）
        if (keyCode == SokobanMIDlet.CanvasKey.UNDO) {
            if (!inputLocked && !answerActive && !state.won) {
                state.undo();
                refreshStatus();
                repaint();
            }
            return;
        }

        // 软键：不同机型 keyCode 不同，N81/S60 常见 -6 左 / -7 右
        if (keyCode == -6) {
            // 左软键：撤销
            if (!inputLocked && !answerActive && !state.won) {
                state.undo();
                refreshStatus();
                repaint();
            }
            return;
        }
        if (keyCode == -7) {
            if (state.won) {
                nextLevel();
            } else {
                midlet.showMenu();
            }
            return;
        }

        if (answerActive && keyCode != KEY_STAR) {
            // 回放中仅允许 * 停止
            if (keyCode == KEY_POUND) {
                stopAnswer(false);
                repaint();
            }
            return;
        }

        if (inputLocked) {
            return;
        }

        if (state.won) {
            if (action == FIRE || keyCode == KEY_NUM5) {
                nextLevel();
            }
            return;
        }

        // 方向
        int dir = -1;
        if (action == UP || keyCode == KEY_NUM2) {
            dir = Direction.UP;
        } else if (action == DOWN || keyCode == KEY_NUM8) {
            dir = Direction.DOWN;
        } else if (action == LEFT || keyCode == KEY_NUM4) {
            dir = Direction.LEFT;
        } else if (action == RIGHT || keyCode == KEY_NUM6) {
            dir = Direction.RIGHT;
        }

        if (dir >= 0) {
            if (state.tryMoveDir(dir)) {
                refreshStatus();
                repaint();
            }
            return;
        }

        // 功能键
        if (keyCode == KEY_NUM0) {
            // 重置
            loadLevel(state.levelIndex);
            return;
        }
        if (keyCode == KEY_NUM1) {
            prevLevel();
            return;
        }
        if (keyCode == KEY_NUM3) {
            nextLevel();
            return;
        }
        if (keyCode == KEY_STAR) {
            toggleAnswer();
            return;
        }
        if (keyCode == KEY_POUND) {
            midlet.showHelp();
            return;
        }
        if (keyCode == KEY_NUM7) {
            if (!answerActive) {
                state.undo();
                refreshStatus();
                repaint();
            }
            return;
        }
        if (keyCode == KEY_NUM9) {
            // 指针模式提示：N81 无触屏，用 5 键“选中”演示寻路到相邻可走格的说明见 help
            return;
        }
    }

    private void prevLevel() {
        if (state.levelIndex > 0) {
            loadLevel(state.levelIndex - 1);
        }
    }

    private void nextLevel() {
        if (state.levelIndex + 1 < LevelsData.COUNT) {
            loadLevel(state.levelIndex + 1);
        } else {
            status = "已经是最后一关";
            state.won = false;
            repaint();
        }
    }

    private void toggleAnswer() {
        if (answerActive) {
            stopAnswer(false);
            repaint();
            return;
        }
        if (state.won || !LevelsData.hasSolution(state.levelIndex)) {
            status = "本关暂无答案";
            repaint();
            return;
        }
        String sol = LevelsData.solution(state.levelIndex);
        animLen = 0;
        for (int i = 0; i < sol.length(); i++) {
            int d = Direction.fromCode(sol.charAt(i));
            if (d >= 0) {
                if (animLen >= animQueue.length) {
                    break;
                }
                animQueue[animLen++] = d;
            }
        }
        if (animLen == 0) {
            status = "本关暂无答案";
            repaint();
            return;
        }
        int lv = state.levelIndex;
        loadLevel(lv);
        answerActive = true;
        inputLocked = true;
        animPos = 0;
        status = "答案回放中 " + animLen + "步 *停";
        animRunning = true;
        animThread = new Thread(this);
        animThread.start();
        repaint();
    }

    private void stopAnswer(boolean silent) {
        animRunning = false;
        answerActive = false;
        inputLocked = false;
        animLen = 0;
        animPos = 0;
        if (!silent) {
            refreshStatus();
        }
    }

    /** 答案回放线程 */
    public void run() {
        try {
            while (animRunning && animPos < animLen) {
                final int dir = animQueue[animPos++];
                // 在 UI 线程语义上 MIDP 通常允许从其它线程 repaint，状态修改需注意
                if (state != null) {
                    state.tryMoveDir(dir);
                }
                repaint();
                if (state != null && state.won) {
                    break;
                }
                Thread.sleep(60);
            }
        } catch (InterruptedException e) {
            // ignore
        }
        animRunning = false;
        inputLocked = false;
        answerActive = false;
        refreshStatus();
        repaint();
    }

    /**
     * 演示：从玩家向某一方向连续走（模拟“点击可达格”的简化版）。
     * 真机无触屏时，可用菜单触发「自动走一步寻路示例」。
     */
    public void demoPathfindStep() {
        if (state == null || state.won || inputLocked || answerActive) {
            return;
        }
        // 找一个与玩家曼哈顿距离尽量远的空地作为目标（演示 BFS）
        int bestX = state.playerX;
        int bestY = state.playerY;
        int bestD = -1;
        for (int y = 0; y < state.height; y++) {
            for (int x = 0; x < state.width; x++) {
                int i = state.idx(x, y);
                if (state.walls[i] || state.boxes[i]) {
                    continue;
                }
                int d = Math.abs(x - state.playerX) + Math.abs(y - state.playerY);
                if (d > bestD) {
                    bestD = d;
                    bestX = x;
                    bestY = y;
                }
            }
        }
        int[] path = new int[state.width * state.height];
        int len = Pathfinding.findPath(state, bestX, bestY, path);
        if (len > 0) {
            for (int i = 0; i < len; i++) {
                state.tryMoveDir(path[i]);
                if (state.won) {
                    break;
                }
            }
            refreshStatus();
            repaint();
        }
    }

    public void resetLevel() {
        if (state != null) {
            loadLevel(state.levelIndex);
        }
    }

    public int getLevelIndex() {
        return state == null ? 0 : state.levelIndex;
    }
}
