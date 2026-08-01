using System.Collections.Generic;

namespace Sokoban.VSExt
{
    /// <summary>与 html_app 对齐的推箱子逻辑（可在 Tool Window 中驱动）。</summary>
    public sealed class GameLogic
    {
        public HashSet<string> Walls { get; } = new HashSet<string>();
        public HashSet<string> Goals { get; } = new HashSet<string>();
        public HashSet<string> Boxes { get; } = new HashSet<string>();
        public int PlayerX, PlayerY, Moves, Width, Height, LevelIndex;
        public bool Won;
        readonly List<(int px, int py, string? from, string? to, bool push)> _hist = new();

        public static string Key(int x, int y) => x + "," + y;

        public static GameLogic FromRows(string[] rows, int index)
        {
            var s = new GameLogic { LevelIndex = index };
            int maxX = 0, maxY = 0;
            for (int y = 0; y < rows.Length; y++)
            {
                maxY = y;
                var row = rows[y];
                for (int x = 0; x < row.Length; x++)
                {
                    if (x > maxX) maxX = x;
                    var k = Key(x, y);
                    switch (row[x])
                    {
                        case '#': s.Walls.Add(k); break;
                        case '.': s.Goals.Add(k); break;
                        case '$': s.Boxes.Add(k); break;
                        case '*': s.Boxes.Add(k); s.Goals.Add(k); break;
                        case '@': s.PlayerX = x; s.PlayerY = y; break;
                        case '+': s.PlayerX = x; s.PlayerY = y; s.Goals.Add(k); break;
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
            int nx = PlayerX + dx, ny = PlayerY + dy;
            var nk = Key(nx, ny);
            if (Walls.Contains(nk)) return false;
            if (Boxes.Contains(nk))
            {
                var bk = Key(nx + dx, ny + dy);
                if (Walls.Contains(bk) || Boxes.Contains(bk)) return false;
                _hist.Add((PlayerX, PlayerY, nk, bk, true));
                Boxes.Remove(nk);
                Boxes.Add(bk);
                PlayerX = nx;
                PlayerY = ny;
                Moves++;
                Won = true;
                foreach (var b in Boxes)
                    if (!Goals.Contains(b)) { Won = false; break; }
                return true;
            }
            _hist.Add((PlayerX, PlayerY, null, null, false));
            PlayerX = nx;
            PlayerY = ny;
            return true;
        }

        public void Undo()
        {
            if (Won || _hist.Count == 0) return;
            (int px, int py, string? from, string? to, bool push) e = default;
            while (_hist.Count > 0)
            {
                e = _hist[_hist.Count - 1];
                _hist.RemoveAt(_hist.Count - 1);
                if (e.push) break;
                PlayerX = e.px;
                PlayerY = e.py;
            }
            if (!e.push) return;
            PlayerX = e.px;
            PlayerY = e.py;
            if (e.to != null) Boxes.Remove(e.to);
            if (e.from != null) Boxes.Add(e.from);
            if (Moves > 0) Moves--;
            Won = false;
        }

        public string Ascii()
        {
            var lines = new List<string>();
            for (int y = 0; y < Height; y++)
            {
                var chars = new char[Width];
                for (int x = 0; x < Width; x++)
                {
                    var k = Key(x, y);
                    if (PlayerX == x && PlayerY == y) chars[x] = Goals.Contains(k) ? '+' : '@';
                    else if (Boxes.Contains(k)) chars[x] = Goals.Contains(k) ? '*' : '$';
                    else if (Walls.Contains(k)) chars[x] = '#';
                    else if (Goals.Contains(k)) chars[x] = '.';
                    else chars[x] = ' ';
                }
                lines.Add(new string(chars));
            }
            return string.Join("\n", lines);
        }
    }
}
