// 推箱子核心（Mono 教学 — 偏经典 C# 语法，便于 mcs 编译）
using System;
using System.Collections.Generic;
using System.Text;

namespace SokobanMono
{
    public sealed class GameState
    {
        public HashSet<string> Walls = new HashSet<string>();
        public HashSet<string> Goals = new HashSet<string>();
        public HashSet<string> Boxes = new HashSet<string>();
        public int Px, Py, Moves, Width, Height;
        public bool Won;
        private readonly List<Hist> _hist = new List<Hist>();

        private struct Hist
        {
            public int Px, Py;
            public string BoxFrom, BoxTo;
            public bool IsPush;
        }

        public static string Key(int x, int y)
        {
            return x.ToString() + "," + y.ToString();
        }

        public static GameState FromRows(string[] rows)
        {
            var s = new GameState();
            int maxX = 0, maxY = 0;
            for (int y = 0; y < rows.Length; y++)
            {
                maxY = y;
                string row = rows[y];
                for (int x = 0; x < row.Length; x++)
                {
                    if (x > maxX) maxX = x;
                    string k = Key(x, y);
                    switch (row[x])
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
            string nk = Key(nx, ny);
            if (Walls.Contains(nk)) return false;
            if (Boxes.Contains(nk))
            {
                int bx = nx + dx, by = ny + dy;
                string bk = Key(bx, by);
                if (Walls.Contains(bk) || Boxes.Contains(bk)) return false;
                Hist h = new Hist();
                h.Px = Px; h.Py = Py; h.BoxFrom = nk; h.BoxTo = bk; h.IsPush = true;
                _hist.Add(h);
                Boxes.Remove(nk);
                Boxes.Add(bk);
                Px = nx; Py = ny;
                Moves++;
                CheckWin();
                return true;
            }
            Hist w = new Hist();
            w.Px = Px; w.Py = Py; w.IsPush = false;
            _hist.Add(w);
            Px = nx; Py = ny;
            return true;
        }

        public bool Undo()
        {
            if (Won || _hist.Count == 0) return false;
            while (_hist.Count > 0)
            {
                Hist e = _hist[_hist.Count - 1];
                _hist.RemoveAt(_hist.Count - 1);
                if (e.IsPush)
                {
                    Px = e.Px; Py = e.Py;
                    Boxes.Remove(e.BoxTo);
                    Boxes.Add(e.BoxFrom);
                    if (Moves > 0) Moves--;
                    Won = false;
                    return true;
                }
                Px = e.Px; Py = e.Py;
            }
            return true;
        }

        private void CheckWin()
        {
            foreach (string b in Boxes)
            {
                if (!Goals.Contains(b)) { Won = false; return; }
            }
            Won = true;
        }

        public string RenderAscii()
        {
            var sb = new StringBuilder();
            for (int y = 0; y < Height; y++)
            {
                for (int x = 0; x < Width; x++)
                {
                    string k = Key(x, y);
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
}
