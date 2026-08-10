// netaotapp1 — .NET Native AOT 推箱子（教学）
// 发布: dotnet publish -c Release
// 产物为原生可执行文件（无需安装 .NET 运行时）
using System;
using SokobanAot;

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

var state = GameState.FromRows(level);
Console.WriteLine("sokoban_netaot — wasd 移动, z 撤销, r 重置, q 退出");
Console.WriteLine("(.NET Native AOT 教学；PublishAot=true)");

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
        case 'r': state = GameState.FromRows(level); break;
        case 'q': return;
    }
    if (state.Won) Console.WriteLine("Level clear!");
}
