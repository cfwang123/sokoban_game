// 推箱子核心（.NET MAUI 教学）
namespace SokobanMaui;

public sealed class GameState
{
    public HashSet<string> Walls { get; } = new();
    public HashSet<string> Goals { get; } = new();
    public HashSet<string> Boxes { get; } = new();
    public (int X, int Y) Player { get; private set; }
    public int Moves { get; private set; }
    public bool Won { get; private set; }
    public int Width { get; private set; }
    public int Height { get; private set; }
    private readonly List<Hist> _hist = new();
    private readonly record struct Hist((int X, int Y) Player, string? BoxFrom, string? BoxTo);

    public static string Key(int x, int y) => $"{x},{y}";

    public static GameState FromRows(string[] rows)
    {
        var s = new GameState();
        int maxX = 0, maxY = 0;
        for (int y = 0; y < rows.Length; y++)
        {
            maxY = y;
            for (int x = 0; x < rows[y].Length; x++)
            {
                if (x > maxX) maxX = x;
                var k = Key(x, y);
                switch (rows[y][x])
                {
                    case '#': s.Walls.Add(k); break;
                    case '.': s.Goals.Add(k); break;
                    case '$': s.Boxes.Add(k); break;
                    case '*': s.Boxes.Add(k); s.Goals.Add(k); break;
                    case '@': s.Player = (x, y); break;
                    case '+': s.Player = (x, y); s.Goals.Add(k); break;
                }
            }
        }
        s.Width = maxX + 1;
        s.Height = maxY + 1;
        return s;
    }

    public bool TryMove(int dx, int dy)
    {
        if (Won) return false;
        var (px, py) = Player;
        int nx = px + dx, ny = py + dy;
        var nk = Key(nx, ny);
        if (Walls.Contains(nk)) return false;
        if (Boxes.Contains(nk))
        {
            int bx = nx + dx, by = ny + dy;
            var bk = Key(bx, by);
            if (Walls.Contains(bk) || Boxes.Contains(bk)) return false;
            _hist.Add(new Hist(Player, nk, bk));
            Boxes.Remove(nk);
            Boxes.Add(bk);
            Player = (nx, ny);
            Moves++;
            Won = Boxes.All(b => Goals.Contains(b));
            return true;
        }
        _hist.Add(new Hist(Player, null, null));
        Player = (nx, ny);
        return true;
    }

    public bool Undo()
    {
        if (Won || _hist.Count == 0) return false;
        Hist? e = null;
        while (_hist.Count > 0)
        {
            e = _hist[^1];
            _hist.RemoveAt(_hist.Count - 1);
            if (e.Value.BoxFrom != null) break;
            Player = e.Value.Player;
        }
        if (e is null || e.Value.BoxFrom is null) return true;
        Player = e.Value.Player;
        Boxes.Remove(e.Value.BoxTo!);
        Boxes.Add(e.Value.BoxFrom);
        if (Moves > 0) Moves--;
        Won = false;
        return true;
    }

    public char CellAt(int x, int y)
    {
        var k = Key(x, y);
        if (Player == (x, y)) return Goals.Contains(k) ? '+' : '@';
        if (Boxes.Contains(k)) return Goals.Contains(k) ? '*' : '$';
        if (Walls.Contains(k)) return '#';
        if (Goals.Contains(k)) return '.';
        return ' ';
    }

    public string RenderBoard()
    {
        var lines = new List<string>();
        for (int y = 0; y < Height; y++)
        {
            var row = new char[Width];
            for (int x = 0; x < Width; x++)
                row[x] = CellAt(x, y) == ' ' ? '·' : CellAt(x, y);
            lines.Add(new string(row));
        }
        return string.Join("\n", lines);
    }
}

public static class Levels
{
    public static readonly string[] Mini =
    {
        "#######", "#. . .#", "# $$$ #", "#.$@$.#",
        "# $$$ #", "#. . .#", "#######",
    };
}
