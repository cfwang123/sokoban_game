namespace Sokoban.VSExt
{
    /// <summary>
    /// Visual Studio Tool Window 状态示意（教学）。
    /// 真实扩展：继承 ToolWindowPane，Content 绑定 WPF 控件，菜单由 VSCT 注册。
    /// </summary>
    public sealed class SokobanToolWindow
    {
        public const string Title = "推箱子";

        static readonly string[] DemoLevel =
        {
            "###",
            "#@#",
            "#$#",
            "#.#",
            "###",
        };

        GameLogic _game;

        public SokobanToolWindow()
        {
            _game = GameLogic.FromRows(DemoLevel, 0);
        }

        public string Caption =>
            Title + "  步数:" + _game.Moves + (_game.Won ? " 过关" : "");

        public string BoardText => _game.Ascii();

        public void MoveUp() => _game.TryMove(0, -1);
        public void MoveDown() => _game.TryMove(0, 1);
        public void MoveLeft() => _game.TryMove(-1, 0);
        public void MoveRight() => _game.TryMove(1, 0);
        public void Undo() => _game.Undo();

        public void Reset()
        {
            _game = GameLogic.FromRows(DemoLevel, 0);
        }

        public GameLogic Snapshot => _game;
    }

    /// <summary>Package / 命令 GUID 示意（写入真实 VSIX 工程）。</summary>
    public static class SokobanPackageGuide
    {
        public const string PackageGuid = "A1B2C3D4-E5F6-7890-ABCD-EF1234567890";
        public const string CommandSetGuid = "B2C3D4E5-F6A7-8901-BCDE-F12345678901";
        public const int CmdIdOpenToolWindow = 0x0100;

        /*
         * Visual Studio 2022 / 后续版本（含 2026 一代）扩展步骤：
         * 1. 安装「Visual Studio 扩展开发」工作负载
         * 2. 新建 VSIX Project（C#），目标勾选已安装的 VS 版本
         * 3. 添加 Tool Window，将 GameLogic 接到 WPF（TextBlock 显示 Ascii 或自绘）
         * 4. VSCT：视图 → 其它窗口 → 推箱子
         * 5. F5 实验实例；产出 .vsix 安装
         */
    }
}
