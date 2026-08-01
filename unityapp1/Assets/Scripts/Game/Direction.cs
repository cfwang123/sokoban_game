namespace Sokoban.Game
{
    public enum Direction
    {
        Up, Down, Left, Right
    }

    public static class DirectionUtil
    {
        public static void ToDelta(Direction d, out int dx, out int dy)
        {
            dx = dy = 0;
            switch (d)
            {
                case Direction.Up: dy = -1; break;
                case Direction.Down: dy = 1; break;
                case Direction.Left: dx = -1; break;
                case Direction.Right: dx = 1; break;
            }
        }

        public static bool TryParse(char c, out Direction d)
        {
            switch (char.ToUpperInvariant(c))
            {
                case 'U': d = Direction.Up; return true;
                case 'D': d = Direction.Down; return true;
                case 'L': d = Direction.Left; return true;
                case 'R': d = Direction.Right; return true;
                default: d = Direction.Up; return false;
            }
        }
    }
}
