// wpfapp1 — WPF 推箱子（教学）
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Shapes;

namespace SokobanWpf;

public partial class MainWindow : Window
{
    private const double Cell = 40;
    private const double Pad = 16;
    private GameState _state = GameState.FromRows(Levels.Mini);

    public MainWindow()
    {
        InitializeComponent();
        Loaded += (_, _) => { Focus(); Redraw(); };
    }

    private void Redraw()
    {
        Board.Children.Clear();
        var s = _state;
        Board.Width = Pad * 2 + s.Width * Cell;
        Board.Height = Pad * 2 + s.Height * Cell;
        for (int y = 0; y < s.Height; y++)
        {
            for (int x = 0; x < s.Width; x++)
            {
                var k = GameState.Key(x, y);
                double left = Pad + x * Cell, top = Pad + y * Cell;
                if (s.Walls.Contains(k))
                    AddRect(left, top, Cell, Cell, Color.FromRgb(74, 74, 106));
                else
                {
                    AddRect(left, top, Cell, Cell, Color.FromRgb(58, 58, 85));
                    if (s.Goals.Contains(k))
                        AddEllipse(left + Cell / 2 - 6, top + Cell / 2 - 6, 12, 12,
                            Color.FromRgb(233, 69, 96));
                    if (s.Boxes.Contains(k))
                    {
                        var on = s.Goals.Contains(k);
                        AddRect(left + 4, top + 4, Cell - 8, Cell - 8,
                            on ? Color.FromRgb(46, 204, 113) : Color.FromRgb(243, 156, 18));
                    }
                }
                if (s.Player == (x, y))
                    AddEllipse(left + 6, top + 6, Cell - 12, Cell - 12,
                        Color.FromRgb(52, 152, 219));
            }
        }
        Status.Text = $"moves={s.Moves}{(s.Won ? " WIN" : "")}  WASD Z R Esc";
    }

    private void AddRect(double l, double t, double w, double h, Color c)
    {
        var r = new Rectangle { Width = w, Height = h, Fill = new SolidColorBrush(c) };
        Canvas.SetLeft(r, l);
        Canvas.SetTop(r, t);
        Board.Children.Add(r);
    }

    private void AddEllipse(double l, double t, double w, double h, Color c)
    {
        var e = new Ellipse { Width = w, Height = h, Fill = new SolidColorBrush(c) };
        Canvas.SetLeft(e, l);
        Canvas.SetTop(e, t);
        Board.Children.Add(e);
    }

    private void Window_KeyDown(object sender, KeyEventArgs e)
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
