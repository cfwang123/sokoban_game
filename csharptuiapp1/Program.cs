// csharptuiapp1 — C# 终端 TUI 推箱子（教学）
// 零 NuGet：ANSI 清屏 + 立即键输入，类似简易 TUI 循环。
// 不强制编译。可选: dotnet run
using System;
using System.IO;
using SokobanTui;

var state = GameState.FromRows(Levels.Mini);
try
{
    Console.CursorVisible = false;
    Console.Title = "Sokoban C# TUI";
}
catch (IOException)
{
    // 管道/无控制台环境：退化为行输入
}

try
{
    while (true)
    {
        Draw(state);
        ConsoleKeyInfo key;
        try
        {
            key = Console.ReadKey(intercept: true);
        }
        catch (InvalidOperationException)
        {
            // 非交互 stdin：行模式
            Console.Write("> ");
            var line = Console.ReadLine();
            if (line is null) return;
            if (line.Length == 0) continue;
            key = new ConsoleKeyInfo(char.ToLowerInvariant(line[0]), ConsoleKey.NoName, false, false, false);
            // map letter to key below via Char
            switch (char.ToLowerInvariant(line[0]))
            {
                case 'w': state.TryMove(0, -1); break;
                case 's': state.TryMove(0, 1); break;
                case 'a': state.TryMove(-1, 0); break;
                case 'd': state.TryMove(1, 0); break;
                case 'z': state.Undo(); break;
                case 'r': state = GameState.FromRows(Levels.Mini); break;
                case 'q': return;
            }
            continue;
        }
        switch (key.Key)
        {
            case ConsoleKey.W: case ConsoleKey.UpArrow: state.TryMove(0, -1); break;
            case ConsoleKey.S: case ConsoleKey.DownArrow: state.TryMove(0, 1); break;
            case ConsoleKey.A: case ConsoleKey.LeftArrow: state.TryMove(-1, 0); break;
            case ConsoleKey.D: case ConsoleKey.RightArrow: state.TryMove(1, 0); break;
            case ConsoleKey.Z: state.Undo(); break;
            case ConsoleKey.R: state = GameState.FromRows(Levels.Mini); break;
            case ConsoleKey.Q: case ConsoleKey.Escape: return;
        }
        if (state.Won)
        {
            Draw(state);
            Console.WriteLine("Level clear!  (any key)");
            Console.ReadKey(true);
        }
    }
}
finally
{
    Console.CursorVisible = true;
    Console.Write("\x1b[0m");
}

static void Draw(GameState s)
{
    // ANSI: 光标回原点 + 清到末尾（兼容 Windows 10+ 虚拟终端）
    Console.Write("\x1b[H\x1b[J");
    Console.WriteLine("┌─ Sokoban C# TUI ─────────────────┐");
    Console.WriteLine("│ WASD/arrows move  Z undo  R reset │");
    Console.WriteLine("│ Q/Esc quit                        │");
    Console.WriteLine("└───────────────────────────────────┘");
    Console.WriteLine();
    // 简单配色：墙灰、箱黄、人青
    var lines = s.RenderAscii().Replace("\r\n", "\n").Split('\n', StringSplitOptions.RemoveEmptyEntries);
    foreach (var line in lines)
    {
        foreach (var ch in line)
        {
            switch (ch)
            {
                case '#': Console.ForegroundColor = ConsoleColor.DarkGray; break;
                case '$': Console.ForegroundColor = ConsoleColor.Yellow; break;
                case '*': Console.ForegroundColor = ConsoleColor.Green; break;
                case '@': case '+': Console.ForegroundColor = ConsoleColor.Cyan; break;
                case '.': Console.ForegroundColor = ConsoleColor.Magenta; break;
                default: Console.ResetColor(); break;
            }
            Console.Write(ch);
        }
        Console.ResetColor();
        Console.WriteLine();
    }
    Console.WriteLine();
    Console.Write($"moves={s.Moves}");
    if (s.Won) Console.Write("  WIN!");
    Console.WriteLine();
}
