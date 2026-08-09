import java.io.BufferedReader;
import java.io.InputStreamReader;

/** javaapp1 — 推箱子终端版（教学）。 */
public class Main {
    private static final String[] LEVEL = {
        "#######",
        "#. . .#",
        "# $$$ #",
        "#.$@$.#",
        "# $$$ #",
        "#. . .#",
        "#######",
    };

    public static void main(String[] args) throws Exception {
        Game state = Game.fromRows(LEVEL, 0);
        BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
        System.out.println("sokoban_java — wasd 移动, z 撤销, r 重置, q 退出");
        while (true) {
            System.out.println();
            System.out.print(state.renderAscii());
            System.out.printf("moves=%d%s%n> ", state.moves, state.won ? " WIN!" : "");
            String line = in.readLine();
            if (line == null) break;
            line = line.trim();
            if (line.isEmpty()) continue;
            char ch = Character.toLowerCase(line.charAt(0));
            switch (ch) {
                case 'w': state.tryMove(0, -1); break;
                case 's': state.tryMove(0, 1); break;
                case 'a': state.tryMove(-1, 0); break;
                case 'd': state.tryMove(1, 0); break;
                case 'z': state.undo(); break;
                case 'r': state = Game.fromRows(LEVEL, 0); break;
                case 'q': return;
                default: break;
            }
            if (state.won) System.out.println("Level clear!");
        }
    }
}
