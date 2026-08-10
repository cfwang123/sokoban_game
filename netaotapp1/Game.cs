// 推箱子核心（.NET Native AOT 教学 — 避免反射/动态特性）
using System.Collections.Generic;
using System.Text;

namespace SokobanAot;

public sealed class GameState
{
    public HashSet<string> Walls { get; } = new();
    public HashSet<string> Goals { get; } = new();
    public HashSet<string> Boxes { get; } = new();
    public int Px { get; private set; }
    public int Py { get; private set; }
    public int Moves { get; private set; }
    public bool Won { get; private set; }
    public int Width { get; private set; }
    public int Height { get; private set; }
    private readonly List<Hist> _hist = new();
    private readonly record struct Hist(int Px, int Py, string? BoxFrom, string? BoxTo, bool IsPush);

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
                    case '@': s.Px = x; s.Py = y; break;
                    case '+': s.Px = x; s.Py = y; s.Goals.Add(k); break;
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
        int nx = Px + dx, ny = Py + dy;
        var nk = Key(nx, ny);
        if (Walls.Contains(nk)) return false;
        if (Boxes.Contains(nk))
        {
            int bx = nx + dx, by = ny + dy;
            var bk = Key(bx, by);
            if (Walls.Contains(bk) || Boxes.Contains(bk)) return false;
            _hist.Add(new Hist(Px, Py, nk, bk, true));
            Boxes.Remove(nk);
            Boxes.Add(bk);
            Px = nx; Py = ny;
            Moves++;
            Won = true;
            foreach (var b in Boxes)
                if (!Goals.Contains(b)) { Won = false; break; }
            return true;
        }
        _hist.Add(new Hist(Px, Py, null, null, false));
        Px = nx; Py = ny;
        return true;
    }

    public bool Undo()
    {
        if (Won || _hist.Count == 0) return false;
        while (_hist.Count > 0)
        {
            var e = _hist[_hist.Count - 1];
            _hist.RemoveAt(_hist.Count - 1);
            if (e.IsPush)
            {
                Px = e.Px; Py = e.Py;
                Boxes.Remove(e.BoxTo!);
                Boxes.Add(e.BoxFrom!);
                if (Moves > 0) Moves--;
                Won = false;
                return true;
            }
            Px = e.Px; Py = e.Py;
        }
        return true;
    }

    public string RenderAscii()
    {
        var sb = new StringBuilder();
        for (int y = 0; y < Height; y++)
        {
            for (int x = 0; x < Width; x++)
            {
                var k = Key(x, y);
                if (Px == x && Py == y) sb.Append(Goals.Contains(k) ? '+' : '@');
                else if (Boxes.Contains(k)) sb.Append(Goals.Contains(k) ? '*' : '$');
                else if (Walls.Contains(k)) sb.Append('#');
                else if (Goals.Contains(k)) sb.Append('.');
                else sb.Append(' ');
            }
            sb.AppendLine();
        }
        return sb.ToString();
    }
}
