package com.whj.sokoban

/**
 * 真实类签名（IntelliJ SDK）：
 *
 * ```
 * class SokobanToolWindowFactory : ToolWindowFactory {
 *   override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
 *     val panel = JPanel(BorderLayout())
 *     val area = JTextArea()
 *     val logic = SokobanPanel()
 *     fun refresh() { area.text = logic.title + "\n" + logic.boardText }
 *     // 按钮 + KeyListener 调用 logic.move / undo ...
 *     toolWindow.contentManager.addContent(
 *       ContentFactory.getInstance().createContent(panel, "", false))
 *   }
 * }
 * ```
 *
 * 教学仓库用同名类占位，避免无 SDK 时无法打开工程。
 */
class SokobanToolWindowFactory {
    // 见类注释；完整实现在接入 org.jetbrains.intellij Gradle 插件后取消注释 SDK 代码。
}
