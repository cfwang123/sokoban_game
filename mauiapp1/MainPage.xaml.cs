// mauiapp1 — .NET MAUI 主页（教学）
namespace SokobanMaui;

public partial class MainPage : ContentPage
{
    private GameState _state = GameState.FromRows(Levels.Mini);

    public MainPage()
    {
        InitializeComponent();
        Redraw();
    }

    private void Redraw()
    {
        BoardLabel.Text = _state.RenderBoard();
        StatusLabel.Text = $"moves={_state.Moves}{(_state.Won ? " WIN!" : "")}";
        if (_state.Won)
            StatusLabel.Text += "  Level clear!";
    }

    private void OnUp(object? s, EventArgs e) { _state.TryMove(0, -1); Redraw(); }
    private void OnDown(object? s, EventArgs e) { _state.TryMove(0, 1); Redraw(); }
    private void OnLeft(object? s, EventArgs e) { _state.TryMove(-1, 0); Redraw(); }
    private void OnRight(object? s, EventArgs e) { _state.TryMove(1, 0); Redraw(); }
    private void OnUndo(object? s, EventArgs e) { _state.Undo(); Redraw(); }
    private void OnReset(object? s, EventArgs e)
    {
        _state = GameState.FromRows(Levels.Mini);
        Redraw();
    }
}
