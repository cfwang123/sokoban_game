// 推箱子核心逻辑（Scala 教学）
import scala.collection.mutable

case class Hist(px: Int, py: Int, boxFrom: Option[String] = None, boxTo: Option[String] = None)

class GameState {
  val walls = mutable.Set.empty[String]
  val goals = mutable.Set.empty[String]
  val boxes = mutable.Set.empty[String]
  var px = 0
  var py = 0
  var moves = 0
  var won = false
  var width = 0
  var height = 0
  val hist = mutable.ArrayBuffer.empty[Hist]

  def checkWin(): Unit =
    won = boxes.forall(goals.contains)

  def tryMove(dx: Int, dy: Int): Boolean = {
    if (won) return false
    val nx = px + dx
    val ny = py + dy
    val nk = GameState.key(nx, ny)
    if (walls.contains(nk)) return false
    if (boxes.contains(nk)) {
      val bx = nx + dx
      val by = ny + dy
      val bk = GameState.key(bx, by)
      if (walls.contains(bk) || boxes.contains(bk)) return false
      hist += Hist(px, py, Some(nk), Some(bk))
      boxes -= nk
      boxes += bk
      px = nx; py = ny
      moves += 1
      checkWin()
      true
    } else {
      hist += Hist(px, py)
      px = nx; py = ny
      true
    }
  }

  def undo(): Boolean = {
    if (won || hist.isEmpty) return false
    var entry: Hist = null
    while (hist.nonEmpty) {
      entry = hist.remove(hist.length - 1)
      if (entry.boxFrom.isDefined) {
        px = entry.px; py = entry.py
        boxes -= entry.boxTo.get
        boxes += entry.boxFrom.get
        if (moves > 0) moves -= 1
        won = false
        return true
      }
      px = entry.px; py = entry.py
    }
    true
  }

  def renderAscii(): String = {
    val sb = new StringBuilder
    for (y <- 0 until height; x <- 0 until width) {
      val k = GameState.key(x, y)
      if (px == x && py == y) sb += (if (goals.contains(k)) '+' else '@')
      else if (boxes.contains(k)) sb += (if (goals.contains(k)) '*' else '$')
      else if (walls.contains(k)) sb += '#'
      else if (goals.contains(k)) sb += '.'
      else sb += ' '
      if (x == width - 1) sb += '\n'
    }
    sb.toString
  }
}

object GameState {
  def key(x: Int, y: Int): String = s"$x,$y"

  def fromRows(rows: Seq[String], index: Int = 0): GameState = {
    val s = new GameState
    var maxX = 0
    var maxY = 0
    for ((row, y) <- rows.zipWithIndex) {
      maxY = y
      for ((ch, x) <- row.zipWithIndex) {
        if (x > maxX) maxX = x
        val k = key(x, y)
        ch match {
          case '#' => s.walls += k
          case '.' => s.goals += k
          case '$' => s.boxes += k
          case '*' => s.boxes += k; s.goals += k
          case '@' => s.px = x; s.py = y
          case '+' => s.px = x; s.py = y; s.goals += k
          case _ =>
        }
      }
    }
    s.width = maxX + 1
    s.height = maxY + 1
    s
  }
}
