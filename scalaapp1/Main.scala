// scalaapp1 — Scala 推箱子终端版（教学）
// 运行: scala Main.scala
// 或: scalac Game.scala Main.scala && scala Main

object Main {
  val Level = Seq(
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######"
  )

  def main(args: Array[String]): Unit = {
    var state = GameState.fromRows(Level)
    println("sokoban_scala — wasd 移动, z 撤销, r 重置, q 退出")
    var cont = true
    while (cont) {
      println()
      print(state.renderAscii())
      val flag = if (state.won) " WIN!" else ""
      print(s"moves=${state.moves}$flag\n> ")
      val line = scala.io.StdIn.readLine()
      if (line == null) cont = false
      else {
        val t = line.trim
        if (t.nonEmpty) {
          t.head.toLower match {
            case 'w' => state.tryMove(0, -1)
            case 's' => state.tryMove(0, 1)
            case 'a' => state.tryMove(-1, 0)
            case 'd' => state.tryMove(1, 0)
            case 'z' => state.undo()
            case 'r' => state = GameState.fromRows(Level)
            case 'q' => cont = false
            case _ =>
          }
          if (state.won) println("Level clear!")
        }
      }
    }
  }
}
