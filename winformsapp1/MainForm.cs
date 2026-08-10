// winformsapp1 — WinForms 推箱子（教学）
// 不强制编译。可选: dotnet run
using System.Drawing;
using System.Windows.Forms;

namespace SokobanGui;

public sealed class MainForm : Form
{
    private const int Cell = 40;
    private const int Pad = 16;
    private GameState _state = GameState.FromRows(Levels.Mini);

    public MainForm()
    {
        Text = "Sokoban WinForms";
        DoubleBuffered = true;
        KeyPreview = true;
        FormBorderStyle = FormBorderStyle.FixedSingle;
        MaximizeBox = false;
        ClientSize = new Size(Pad * 2 + _state.Width * Cell,
                              Pad * 2 + _state.Height * Cell + 28);
        BackColor = Color.FromArgb(26, 26, 46);
        KeyDown += OnKeyDown;
        Paint += OnPaint;
    }

    private void OnPaint(object? sender, PaintEventArgs e)
    {
        var g = e.Graphics;
        var s = _state;
        for (int y = 0; y < s.Height; y++)
        {
            for (int x = 0; x < s.Width; x++)
            {
                var k = GameState.Key(x, y);
                var rc = new Rectangle(Pad + x * Cell, Pad + y * Cell, Cell, Cell);
                if (s.Walls.Contains(k))
                    g.FillRectangle(new SolidBrush(Color.FromArgb(74, 74, 106)), rc);
                else
                {
                    g.FillRectangle(new SolidBrush(Color.FromArgb(58, 58, 85)), rc);
                    g.DrawRectangle(new Pen(Color.FromArgb(68, 68, 102)), rc);
                    if (s.Goals.Contains(k))
                        g.FillEllipse(new SolidBrush(Color.FromArgb(233, 69, 96)),
                            rc.X + Cell / 2 - 6, rc.Y + Cell / 2 - 6, 12, 12);
                    if (s.Boxes.Contains(k))
                    {
                        var on = s.Goals.Contains(k);
                        var br = on ? Color.FromArgb(46, 204, 113) : Color.FromArgb(243, 156, 18);
                        g.FillRectangle(new SolidBrush(br),
                            rc.X + 4, rc.Y + 4, Cell - 8, Cell - 8);
                    }
                }
                if (s.Player == (x, y))
                    g.FillEllipse(new SolidBrush(Color.FromArgb(52, 152, 219)),
                        rc.X + 6, rc.Y + 6, Cell - 12, Cell - 12);
            }
        }
        var flag = s.Won ? " WIN" : "";
        g.DrawString($"moves={s.Moves}{flag}  WASD Z R Esc",
            Font, Brushes.White, 8, Pad + s.Height * Cell + 6);
    }

    private void OnKeyDown(object? sender, KeyEventArgs e)
    {
        switch (e.KeyCode)
        {
            case Keys.W: case Keys.Up: _state.TryMove(0, -1); break;
            case Keys.S: case Keys.Down: _state.TryMove(0, 1); break;
            case Keys.A: case Keys.Left: _state.TryMove(-1, 0); break;
            case Keys.D: case Keys.Right: _state.TryMove(1, 0); break;
            case Keys.Z: _state.Undo(); break;
            case Keys.R: _state = GameState.FromRows(Levels.Mini); break;
            case Keys.Escape: case Keys.Q: Close(); return;
            default: return;
        }
        Invalidate();
    }
}
