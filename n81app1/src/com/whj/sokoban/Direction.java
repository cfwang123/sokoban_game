package com.whj.sokoban;

/**
 * 四向移动（与 html_app / android 的 U D L R 编码一致）。
 * <p>
 * J2ME 无 enum（CDC/Java SE 才有完整 enum 用法；MIDP 常用 int 常量）。
 */
public final class Direction {
    public static final int UP = 0;
    public static final int DOWN = 1;
    public static final int LEFT = 2;
    public static final int RIGHT = 3;

    public static final int[] DX = { 0, 0, -1, 1 };
    public static final int[] DY = { -1, 1, 0, 0 };

    private Direction() {}

    public static int fromCode(char ch) {
        switch (ch) {
            case 'U':
            case 'u':
                return UP;
            case 'D':
            case 'd':
                return DOWN;
            case 'L':
            case 'l':
                return LEFT;
            case 'R':
            case 'r':
                return RIGHT;
            default:
                return -1;
        }
    }
}
