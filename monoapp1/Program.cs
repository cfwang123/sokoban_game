// monoapp1 — Mono / 经典 CLR 推箱子终端版（教学）
// 编译: mcs -out:sokoban.exe Program.cs Game.cs
// 运行: mono sokoban.exe
// 也可用: csc /out:sokoban.exe *.cs  或  dotnet（见 netaotapp1）
using System;

namespace SokobanMono
{
    class Program
    {
        static readonly string[] Level = new string[]
        {
            "#######",
            "#. . .#",
            "# $$$ #",
            "#.$@$.#",
            "# $$$ #",
            "#. . .#",
            "#######",
        };

        static void Main(string[] args)
        {
            GameState state = GameState.FromRows(Level);
            Console.WriteLine("sokoban_mono — wasd 移动, z 撤销, r 重置, q 退出");
            Console.WriteLine("(Mono / mcs 教学；逻辑与 csharpapp1 同构)");
            while (true)
            {
                Console.WriteLine();
                Console.Write(state.RenderAscii());
                Console.Write("moves=" + state.Moves + (state.Won ? " WIN!" : "") + "\n> ");
                string line = Console.ReadLine();
                if (line == null) break;
                line = line.Trim();
                if (line.Length == 0) continue;
                char ch = char.ToLowerInvariant(line[0]);
                if (ch == 'w') state.TryMove(0, -1);
                else if (ch == 's') state.TryMove(0, 1);
                else if (ch == 'a') state.TryMove(-1, 0);
                else if (ch == 'd') state.TryMove(1, 0);
                else if (ch == 'z') state.Undo();
                else if (ch == 'r') state = GameState.FromRows(Level);
                else if (ch == 'q') break;
                if (state.Won) Console.WriteLine("Level clear!");
            }
        }
    }
}
