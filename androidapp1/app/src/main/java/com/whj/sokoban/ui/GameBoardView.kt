package com.whj.sokoban.ui

import android.content.Context
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.RectF
import android.util.AttributeSet
import android.view.MotionEvent
import android.view.View
import androidx.core.content.ContextCompat
import com.whj.sokoban.R
import com.whj.sokoban.game.GameState
import kotlin.math.floor
import kotlin.math.min

/**
 * 推箱子棋盘绘制与点击交互。
 * 点击空地 → 回调 onCellTap 由外部做 BFS 寻路；
 * 点击相邻箱子 → 同样回调由外部 tryMove。
 */
class GameBoardView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0,
) : View(context, attrs, defStyleAttr) {

    interface Listener {
        fun onCellTap(gridX: Int, gridY: Int)
    }

    var listener: Listener? = null

    private var state: GameState? = null
    private var cellSize = 40f
    private var offsetX = 0f
    private var offsetY = 0f
    private var paddingPx = 12f

    private val floorPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = ContextCompat.getColor(context, R.color.floor)
        style = Paint.Style.FILL
    }
    private val gridPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = ContextCompat.getColor(context, R.color.floor_grid)
        style = Paint.Style.STROKE
        strokeWidth = 1f
    }
    private val wallPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = ContextCompat.getColor(context, R.color.wall)
        style = Paint.Style.FILL
    }
    private val wallLightPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = ContextCompat.getColor(context, R.color.wall_light)
        style = Paint.Style.FILL
    }
    private val wallShadowPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = ContextCompat.getColor(context, R.color.wall_shadow)
        style = Paint.Style.FILL
    }
    private val goalPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = ContextCompat.getColor(context, R.color.goal)
        style = Paint.Style.FILL
    }
    private val goalStrokePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = ContextCompat.getColor(context, R.color.goal_stroke)
        style = Paint.Style.STROKE
        strokeWidth = 3f
    }
    private val boxPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
    }
    private val boxStrokePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 3f
    }
    private val boxLightPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
    }
    private val boxCrossPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 2.5f
        strokeCap = Paint.Cap.ROUND
    }
    private val playerPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = ContextCompat.getColor(context, R.color.player)
        style = Paint.Style.FILL
    }
    private val playerStrokePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = ContextCompat.getColor(context, R.color.player_stroke)
        style = Paint.Style.STROKE
        strokeWidth = 3f
    }
    private val eyeWhitePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = 0xFFFFFFFF.toInt()
        style = Paint.Style.FILL
    }
    private val eyeDarkPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = ContextCompat.getColor(context, R.color.bg_dark)
        style = Paint.Style.FILL
    }

    private val colorBox = ContextCompat.getColor(context, R.color.box)
    private val colorBoxStroke = ContextCompat.getColor(context, R.color.box_stroke)
    private val colorBoxLight = ContextCompat.getColor(context, R.color.box_light)
    private val colorBoxCross = ContextCompat.getColor(context, R.color.box_cross)
    private val colorBoxOnGoal = ContextCompat.getColor(context, R.color.box_on_goal)
    private val colorBoxOnGoalStroke = ContextCompat.getColor(context, R.color.box_on_goal_stroke)
    private val colorBoxOnGoalLight = ContextCompat.getColor(context, R.color.box_on_goal_light)
    private val colorBoxOnGoalCross = ContextCompat.getColor(context, R.color.box_on_goal_cross)

    private val tmpRect = RectF()

    fun setState(newState: GameState?) {
        state = newState
        recalculateLayout()
        invalidate()
    }

    fun refresh() {
        invalidate()
    }

    private fun recalculateLayout() {
        val s = state ?: return
        if (width <= 0 || height <= 0) return
        paddingPx = min(width, height) * 0.03f
        val availW = width - paddingPx * 2
        val availH = height - paddingPx * 2
        if (availW <= 0 || availH <= 0 || s.width <= 0 || s.height <= 0) return
        cellSize = min(availW / s.width, availH / s.height)
        val boardW = cellSize * s.width
        val boardH = cellSize * s.height
        offsetX = (width - boardW) / 2f
        offsetY = (height - boardH) / 2f
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        recalculateLayout()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val s = state ?: return
        if (cellSize <= 0f) recalculateLayout()
        if (cellSize <= 0f) return

        // 地板
        for (y in 0 until s.height) {
            for (x in 0 until s.width) {
                val px = offsetX + x * cellSize
                val py = offsetY + y * cellSize
                canvas.drawRect(px, py, px + cellSize, py + cellSize, floorPaint)
                canvas.drawRect(px, py, px + cellSize, py + cellSize, gridPaint)
            }
        }

        // 墙
        val edge = (cellSize * 0.08f).coerceAtLeast(2f)
        for (key in s.walls) {
            val (x, y) = parseKey(key) ?: continue
            val px = offsetX + x * cellSize
            val py = offsetY + y * cellSize
            canvas.drawRect(px, py, px + cellSize, py + cellSize, wallPaint)
            canvas.drawRect(px, py, px + cellSize, py + edge, wallLightPaint)
            canvas.drawRect(px, py, px + edge, py + cellSize, wallLightPaint)
            canvas.drawRect(px, py + cellSize - edge, px + cellSize, py + cellSize, wallShadowPaint)
            canvas.drawRect(px + cellSize - edge, py, px + cellSize, py + cellSize, wallShadowPaint)
        }

        // 目标点
        val goalR = cellSize * 0.15f
        for (key in s.goals) {
            val (x, y) = parseKey(key) ?: continue
            val cx = offsetX + x * cellSize + cellSize / 2f
            val cy = offsetY + y * cellSize + cellSize / 2f
            canvas.drawCircle(cx, cy, goalR, goalPaint)
            canvas.drawCircle(cx, cy, goalR, goalStrokePaint)
        }

        // 箱子
        val inset = cellSize * 0.1f
        for (key in s.boxes) {
            val (x, y) = parseKey(key) ?: continue
            val onGoal = s.isGoal(x, y)
            boxPaint.color = if (onGoal) colorBoxOnGoal else colorBox
            boxStrokePaint.color = if (onGoal) colorBoxOnGoalStroke else colorBoxStroke
            boxLightPaint.color = if (onGoal) colorBoxOnGoalLight else colorBoxLight
            boxCrossPaint.color = if (onGoal) colorBoxOnGoalCross else colorBoxCross

            val px = offsetX + x * cellSize + inset
            val py = offsetY + y * cellSize + inset
            val size = cellSize - inset * 2
            tmpRect.set(px, py, px + size, py + size)
            canvas.drawRoundRect(tmpRect, 4f, 4f, boxPaint)
            canvas.drawRoundRect(tmpRect, 4f, 4f, boxStrokePaint)

            val hi = (size * 0.08f).coerceAtLeast(2f)
            canvas.drawRect(px + 2, py + 2, px + size - 2, py + 2 + hi, boxLightPaint)
            canvas.drawRect(px + 2, py + 2, px + 2 + hi, py + size - 2, boxLightPaint)

            val cx = px + size / 2f
            val cy = py + size / 2f
            val arm = size * 0.18f
            canvas.drawLine(cx - arm, cy, cx + arm, cy, boxCrossPaint)
            canvas.drawLine(cx, cy - arm, cx, cy + arm, boxCrossPaint)
        }

        // 玩家
        val p = s.player
        val cx = offsetX + p.x * cellSize + cellSize / 2f
        val cy = offsetY + p.y * cellSize + cellSize / 2f
        val r = cellSize * 0.35f
        canvas.drawCircle(cx, cy, r, playerPaint)
        canvas.drawCircle(cx, cy, r, playerStrokePaint)

        val eyeOffX = cellSize * 0.1f
        val eyeOffY = cellSize * 0.08f
        val eyeR = cellSize * 0.07f
        val pupilR = cellSize * 0.035f
        canvas.drawCircle(cx - eyeOffX, cy - eyeOffY, eyeR, eyeWhitePaint)
        canvas.drawCircle(cx + eyeOffX, cy - eyeOffY, eyeR, eyeWhitePaint)
        canvas.drawCircle(cx - eyeOffX, cy - eyeOffY, pupilR, eyeDarkPaint)
        canvas.drawCircle(cx + eyeOffX, cy - eyeOffY, pupilR, eyeDarkPaint)
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        if (event.action == MotionEvent.ACTION_UP) {
            val s = state ?: return true
            if (cellSize <= 0f) return true
            val gx = floor((event.x - offsetX) / cellSize).toInt()
            val gy = floor((event.y - offsetY) / cellSize).toInt()
            if (gx < 0 || gy < 0 || gx >= s.width || gy >= s.height) return true
            listener?.onCellTap(gx, gy)
            performClick()
        }
        return true
    }

    override fun performClick(): Boolean {
        super.performClick()
        return true
    }

    private fun parseKey(key: String): Pair<Int, Int>? {
        val parts = key.split(',')
        if (parts.size != 2) return null
        val x = parts[0].toIntOrNull() ?: return null
        val y = parts[1].toIntOrNull() ?: return null
        return x to y
    }
}
