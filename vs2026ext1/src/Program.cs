using System;

namespace Sokoban.VSExt
{
    /// <summary>
    /// 主机控制台试玩（无 VS SDK 时验证 GameLogic）。
    /// 扩展真正入口是 VSIX Package，不是 Main。
    /// </summary>
    public static class Program
    {
        public static void Main()
        {
            var win = new SokobanToolWindow();
            Console.WriteLine("vs2026ext1 console host — WASD move, Z undo, Q quit");
            Console.WriteLine("(In real VS: View → Other Windows → 推箱子)");
            for (;;)
            {
                Console.WriteLine();
                Console.WriteLine(win.Caption);
                Console.WriteLine(win.BoardText);
                Console.Write("> ");
                var line = Console.ReadLine();
                if (string.IsNullOrEmpty(line)) continue;
                switch (char.ToLowerInvariant(line[0]))
                {
                    case 'w': win.MoveUp(); break;
                    case 's': win.MoveDown(); break;
                    case 'a': win.MoveLeft(); break;
                    case 'd': win.MoveRight(); break;
                    case 'z': win.Undo(); break;
                    case 'q': return;
                }
            }
        }
    }
}
