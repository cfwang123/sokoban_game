using Sokoban.Game;
using UnityEngine;

/// <summary>
/// 挂到场景空物体。教学工程：用 Debug 绘制格子，正式项目可改为 Sprite/Tilemap。
/// 在 Unity 编辑器中：Create Empty → Add Component → GameController。
/// </summary>
public class GameController : MonoBehaviour
{
    [TextArea(5, 20)]
    public string levelText =
        "#######\n" +
        "#. . .#\n" +
        "# $$$ #\n" +
        "#.$@$.#\n" +
        "# $$$ #\n" +
        "#. . .#\n" +
        "#######";

    GameState _state;
    float _cell = 1f;

    void Start()
    {
        LoadFromText(levelText, 0);
    }

    void Update()
    {
        if (_state == null || _state.Won) return;
        if (Input.GetKeyDown(KeyCode.W) || Input.GetKeyDown(KeyCode.UpArrow)) _state.TryMove(0, -1);
        if (Input.GetKeyDown(KeyCode.S) || Input.GetKeyDown(KeyCode.DownArrow)) _state.TryMove(0, 1);
        if (Input.GetKeyDown(KeyCode.A) || Input.GetKeyDown(KeyCode.LeftArrow)) _state.TryMove(-1, 0);
        if (Input.GetKeyDown(KeyCode.D) || Input.GetKeyDown(KeyCode.RightArrow)) _state.TryMove(1, 0);
        if (Input.GetKeyDown(KeyCode.Z)) _state.Undo();
        if (Input.GetKeyDown(KeyCode.R)) LoadFromText(levelText, _state.LevelIndex);
    }

    public void LoadFromText(string text, int index)
    {
        var lines = text.Replace("\r\n", "\n").Split('\n');
        _state = GameState.FromRows(lines, index);
    }

    void OnDrawGizmos()
    {
        if (_state == null) return;
        for (int y = 0; y < _state.Height; y++)
        {
            for (int x = 0; x < _state.Width; x++)
            {
                var k = GameState.Key(x, y);
                var p = new Vector3(x * _cell, -y * _cell, 0);
                if (_state.Walls.Contains(k)) Gizmos.color = Color.gray;
                else Gizmos.color = new Color(0.2f, 0.2f, 0.3f);
                Gizmos.DrawCube(p, Vector3.one * (_cell * 0.95f));
                if (_state.Goals.Contains(k))
                {
                    Gizmos.color = Color.red;
                    Gizmos.DrawSphere(p, _cell * 0.15f);
                }
                if (_state.Boxes.Contains(k))
                {
                    Gizmos.color = _state.Goals.Contains(k) ? Color.green : Color.yellow;
                    Gizmos.DrawCube(p, Vector3.one * (_cell * 0.7f));
                }
            }
        }
        Gizmos.color = Color.cyan;
        Gizmos.DrawSphere(new Vector3(_state.PlayerX * _cell, -_state.PlayerY * _cell, 0), _cell * 0.35f);
    }

    void OnGUI()
    {
        if (_state == null) return;
        GUI.Label(new Rect(10, 10, 400, 20), "Moves: " + _state.Moves + (_state.Won ? "  WIN!" : ""));
        GUI.Label(new Rect(10, 30, 400, 40), "WASD/Arrows move  Z undo  R reset");
    }
}
