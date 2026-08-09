using SokobanCli;

// csharpapp1 — 推箱子终端版（教学）

string[] level =
[
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
];

var state = GameState.FromRows(level, 0);
Console.WriteLine("sokoban_csharp — wasd 移动, z 撤销, r 重置, q 退出");

while (true)
{
    Console.WriteLine();
    Console.Write(state.RenderAscii());
    Console.Write($"moves={state.Moves}{(state.Won ? " WIN!" : "")}\n> ");
    var line = Console.ReadLine();
    if (line is null) break;
    line = line.Trim();
    if (line.Length == 0) continue;
    switch (char.ToLowerInvariant(line[0]))
    {
        case 'w': state.TryMove(0, -1); break;
        case 's': state.TryMove(0, 1); break;
        case 'a': state.TryMove(-1, 0); break;
        case 'd': state.TryMove(1, 0); break;
        case 'z': state.Undo(); break;
        case 'r': state = GameState.FromRows(level, 0); break;
        case 'q': return;
    }
    if (state.Won) Console.WriteLine("Level clear!");
}
