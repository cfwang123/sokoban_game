using System.Collections.Generic;

namespace Sokoban.Game
{
    /// <summary>推箱子逻辑（与 html_app 对齐）。可挂到空物体上由 GameController 驱动。</summary>
    public sealed class GameState
    {
        public readonly HashSet<string> Walls = new HashSet<string>();
        public readonly HashSet<string> Goals = new HashSet<string>();
        public readonly HashSet<string> Boxes = new HashSet<string>();
        public int PlayerX, PlayerY;
        public int Moves;
        public bool Won;
        public int LevelIndex;
        public int Width, Height;

        readonly List<Hist> _hist = new List<Hist>();

        struct Hist
        {
            public int Px, Py;
            public string BoxFrom, BoxTo;
        }

        public static string Key(int x, int y) => x + "," + y;

        public bool TryMove(int dx, int dy)
        {
            if (Won) return false;
            int nx = PlayerX + dx, ny = PlayerY + dy;
            string nk = Key(nx, ny);
            if (Walls.Contains(nk)) return false;
            if (Boxes.Contains(nk))
            {
                string bk = Key(nx + dx, ny + dy);
                if (Walls.Contains(bk) || Boxes.Contains(bk)) return false;
                _hist.Add(new Hist { Px = PlayerX, Py = PlayerY, BoxFrom = nk, BoxTo = bk });
                Boxes.Remove(nk);
                Boxes.Add(bk);
                PlayerX = nx;
                PlayerY = ny;
                Moves++;
                CheckWin();
                return true;
            }
            _hist.Add(new Hist { Px = PlayerX, Py = PlayerY, BoxFrom = null, BoxTo = null });
            PlayerX = nx;
            PlayerY = ny;
            return true;
        }

        public bool Undo()
        {
            if (Won || _hist.Count == 0) return false;
            Hist e = default;
            while (_hist.Count > 0)
            {
                e = _hist[_hist.Count - 1];
                _hist.RemoveAt(_hist.Count - 1);
                if (e.BoxFrom != null) break;
                PlayerX = e.Px;
                PlayerY = e.Py;
            }
            if (e.BoxFrom == null) return true;
            PlayerX = e.Px;
            PlayerY = e.Py;
            Boxes.Remove(e.BoxTo);
            Boxes.Add(e.BoxFrom);
            if (Moves > 0) Moves--;
            Won = false;
            return true;
        }

        void CheckWin()
        {
            foreach (var b in Boxes)
            {
                if (!Goals.Contains(b)) { Won = false; return; }
            }
            Won = true;
        }

        public static GameState FromRows(string[] rows, int index)
        {
            var s = new GameState { LevelIndex = index };
            int maxX = 0, maxY = 0;
            for (int y = 0; y < rows.Length; y++)
            {
                var row = rows[y];
                maxY = y;
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
                        case '@': s.PlayerX = x; s.PlayerY = y; break;
                        case '+': s.PlayerX = x; s.PlayerY = y; s.Goals.Add(k); break;
                    }
                }
            }
            s.Width = maxX + 1;
            s.Height = maxY + 1;
            return s;
        }
    }
}
