// winui3app1 — WinUI 3 主窗口（教学）
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Input;
using Windows.System;

namespace SokobanWinUI;

public sealed partial class MainWindow : Window
{
    private GameState _state = GameState.FromRows(Levels.Mini);

    public MainWindow()
    {
        InitializeComponent();
        Redraw();
    }

    private void Redraw()
    {
        BoardText.Text = _state.RenderBoard();
        StatusText.Text = $"moves={_state.Moves}{(_state.Won ? " WIN!" : "")}";
    }

    private void OnUp(object sender, RoutedEventArgs e) { _state.TryMove(0, -1); Redraw(); }
    private void OnDown(object sender, RoutedEventArgs e) { _state.TryMove(0, 1); Redraw(); }
    private void OnLeft(object sender, RoutedEventArgs e) { _state.TryMove(-1, 0); Redraw(); }
    private void OnRight(object sender, RoutedEventArgs e) { _state.TryMove(1, 0); Redraw(); }
    private void OnUndo(object sender, RoutedEventArgs e) { _state.Undo(); Redraw(); }
    private void OnReset(object sender, RoutedEventArgs e)
    {
        _state = GameState.FromRows(Levels.Mini);
        Redraw();
    }

    private void Window_KeyDown(object sender, KeyRoutedEventArgs e)
    {
        switch (e.Key)
        {
            case VirtualKey.W: case VirtualKey.Up: _state.TryMove(0, -1); break;
            case VirtualKey.S: case VirtualKey.Down: _state.TryMove(0, 1); break;
            case VirtualKey.A: case VirtualKey.Left: _state.TryMove(-1, 0); break;
            case VirtualKey.D: case VirtualKey.Right: _state.TryMove(1, 0); break;
            case VirtualKey.Z: _state.Undo(); break;
            case VirtualKey.R: _state = GameState.FromRows(Levels.Mini); break;
            default: return;
        }
        Redraw();
    }
}
