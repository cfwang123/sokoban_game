// avaloniaapp1 — Avalonia 跨平台 UI 教学（字符画版，便于阅读）
using Avalonia.Controls;
using Avalonia.Input;
using System.Text;

namespace SokobanAvalonia;

public partial class MainWindow : Window
{
    private GameState _state = GameState.FromRows(Levels.Mini);

    public MainWindow()
    {
        InitializeComponent();
        Redraw();
    }

    private void Redraw()
    {
        var s = _state;
        var sb = new StringBuilder();
        for (int y = 0; y < s.Height; y++)
        {
            for (int x = 0; x < s.Width; x++)
            {
                var k = GameState.Key(x, y);
                if (s.Player == (x, y)) sb.Append(s.Goals.Contains(k) ? '+' : '@');
                else if (s.Boxes.Contains(k)) sb.Append(s.Goals.Contains(k) ? '*' : '$');
                else if (s.Walls.Contains(k)) sb.Append('#');
                else if (s.Goals.Contains(k)) sb.Append('.');
                else sb.Append(' ');
            }
            sb.AppendLine();
        }
        Board.Text = sb.ToString();
        Status.Text = $"moves={s.Moves}{(s.Won ? " WIN" : "")}  WASD Z R Esc";
    }

    private void OnKeyDown(object? sender, KeyEventArgs e)
    {
        switch (e.Key)
        {
            case Key.W: case Key.Up: _state.TryMove(0, -1); break;
            case Key.S: case Key.Down: _state.TryMove(0, 1); break;
            case Key.A: case Key.Left: _state.TryMove(-1, 0); break;
            case Key.D: case Key.Right: _state.TryMove(1, 0); break;
            case Key.Z: _state.Undo(); break;
            case Key.R: _state = GameState.FromRows(Levels.Mini); break;
            case Key.Escape: case Key.Q: Close(); return;
            default: return;
        }
        Redraw();
    }
}
