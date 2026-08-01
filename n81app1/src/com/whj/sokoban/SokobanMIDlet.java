package com.whj.sokoban;

import javax.microedition.lcdui.Alert;
import javax.microedition.lcdui.AlertType;
import javax.microedition.lcdui.Command;
import javax.microedition.lcdui.CommandListener;
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.Displayable;
import javax.microedition.lcdui.List;
import javax.microedition.midlet.MIDlet;
import javax.microedition.midlet.MIDletStateChangeException;

/**
 * MIDlet 入口（对应 Android {@code MainActivity} / iOS {@code @main App}）。
 * <p>
 * <b>生命周期</b>（必考知识点）：
 * <ul>
 *   <li>{@link #startApp()} — 进入前台，可显示界面</li>
 *   <li>{@link #pauseApp()} — 来电/切后台，应暂停动画与声音</li>
 *   <li>{@link #destroyApp(boolean)} — 退出，释放 RMS/线程</li>
 * </ul>
 * Nokia N81：Series 60 3rd Edition FP1，支持 MIDP 2.0 / CLDC 1.1。
 */
public class SokobanMIDlet extends MIDlet implements CommandListener {
    private Display display;
    private GameCanvas canvas;
    private List menu;
    private boolean started;

    private final Command cmdBack = new Command("返回", Command.BACK, 1);
    private final Command cmdOk = new Command("选择", Command.OK, 1);

    protected void startApp() throws MIDletStateChangeException {
        if (!started) {
            display = Display.getDisplay(this);
            canvas = new GameCanvas(this);
            buildMenu();
            started = true;
        }
        display.setCurrent(canvas);
    }

    protected void pauseApp() {
        // 来电时系统调用；演示程序无 BGM，答案线程会自然停在下一步检查
    }

    protected void destroyApp(boolean unconditional) {
        // 可在此关闭 RecordStore / 停止线程
        notifyDestroyed();
    }

    private void buildMenu() {
        menu = new List("菜单", List.IMPLICIT);
        menu.append("继续游戏", null);
        menu.append("上一关", null);
        menu.append("下一关", null);
        menu.append("重置本关", null);
        menu.append("撤销推箱", null);
        menu.append("查看/停止答案", null);
        menu.append("演示BFS寻路", null);
        menu.append("选择关卡...", null);
        menu.append("操作说明", null);
        menu.append("关于", null);
        menu.append("退出", null);
        menu.addCommand(cmdBack);
        menu.addCommand(cmdOk);
        menu.setCommandListener(this);
    }

    public void showMenu() {
        display.setCurrent(menu);
    }

    public void showHelp() {
        Alert a = new Alert(
                "操作说明",
                "方向键/2 4 6 8: 移动\n"
                        + "左软键/7: 撤销\n"
                        + "0: 重置  1:上关  3:下关\n"
                        + "*: 查看/停止答案\n"
                        + "#: 帮助\n"
                        + "右软键: 菜单/通关后下一关\n"
                        + "菜单内可演示 BFS 自动走到较远空地\n"
                        + "(N81 无触屏，点地寻路用菜单演示)",
                null,
                AlertType.INFO
        );
        a.setTimeout(Alert.FOREVER);
        display.setCurrent(a, canvas);
    }

    public void commandAction(Command c, Displayable d) {
        if (d == menu) {
            if (c == cmdBack || c == List.SELECT_COMMAND || c == cmdOk) {
                int i = menu.getSelectedIndex();
                if (c == cmdBack) {
                    display.setCurrent(canvas);
                    return;
                }
                handleMenu(i);
            }
        }
    }

    private void handleMenu(int index) {
        switch (index) {
            case 0: // 继续
                display.setCurrent(canvas);
                break;
            case 1:
                canvas.loadLevel(canvas.getLevelIndex() - 1);
                display.setCurrent(canvas);
                break;
            case 2:
                canvas.loadLevel(canvas.getLevelIndex() + 1);
                display.setCurrent(canvas);
                break;
            case 3:
                canvas.resetLevel();
                display.setCurrent(canvas);
                break;
            case 4:
                // 撤销：通过模拟按键逻辑 —— 直接调 canvas 不便 private，用重置后说明；
                // 改为 public 方法：已有 key 路径；这里 fire 撤销
                display.setCurrent(canvas);
                canvas.keyPressed(CanvasKey.UNDO);
                break;
            case 5:
                display.setCurrent(canvas);
                canvas.keyPressed(CanvasKey.STAR);
                break;
            case 6:
                canvas.demoPathfindStep();
                display.setCurrent(canvas);
                break;
            case 7:
                showLevelPicker();
                break;
            case 8:
                showHelp();
                break;
            case 9:
                showAbout();
                break;
            case 10:
                destroyApp(true);
                break;
            default:
                display.setCurrent(canvas);
                break;
        }
    }

    private void showLevelPicker() {
        List list = new List("选择关卡", List.IMPLICIT);
        for (int i = 0; i < LevelsData.COUNT; i++) {
            list.append((i + 1) + ". " + LevelsData.name(i), null);
        }
        list.addCommand(cmdBack);
        list.setCommandListener(new CommandListener() {
            public void commandAction(Command c, Displayable d) {
                if (c == cmdBack) {
                    display.setCurrent(menu);
                    return;
                }
                int i = ((List) d).getSelectedIndex();
                canvas.loadLevel(i);
                display.setCurrent(canvas);
            }
        });
        display.setCurrent(list);
    }

    private void showAbout() {
        Alert a = new Alert(
                "关于",
                "推箱子 n81app1\n"
                        + "Java ME MIDP 2.0 教学演示\n"
                        + "目标机型: Nokia N81 (S60 3rd FP1)\n"
                        + "关卡数: " + LevelsData.COUNT + " (演示子集)\n"
                        + "玩法对齐 html_app / androidapp1",
                null,
                AlertType.INFO
        );
        a.setTimeout(Alert.FOREVER);
        display.setCurrent(a, canvas);
    }

    /** 供菜单把“逻辑键”传给 Canvas 的常量（避免依赖 Canvas 私有 API）。 */
    public static final class CanvasKey {
        public static final int UNDO = -1006;
        public static final int STAR = Canvas.KEY_STAR;

        private CanvasKey() {}
    }
}
