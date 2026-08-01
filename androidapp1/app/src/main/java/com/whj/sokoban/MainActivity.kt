package com.whj.sokoban

import android.content.Context
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.whj.sokoban.databinding.ActivityMainBinding
import com.whj.sokoban.game.Direction
import com.whj.sokoban.game.GameState
import com.whj.sokoban.game.LevelData
import com.whj.sokoban.game.LevelRepository
import com.whj.sokoban.game.Pathfinding
import com.whj.sokoban.ui.GameBoardView

/**
 * 安卓版推箱子主界面。
 * 功能对齐 html_app：关卡切换、撤销/重置、点击寻路、点箱推动、答案回放、通关下一关。
 * 额外提供虚拟方向键。
 */
class MainActivity : AppCompatActivity(), GameBoardView.Listener {

    private lateinit var binding: ActivityMainBinding
    private lateinit var levels: List<LevelData>
    private var state: GameState? = null

    private val handler = Handler(Looper.getMainLooper())
    private val animQueue = ArrayList<Direction>()
    private var animRunning = false
    private var answerActive = false
    private var inputLocked = false
    private var spinnerReady = false

    private val animRunnable = object : Runnable {
        override fun run() {
            if (animQueue.isEmpty()) {
                animRunning = false
                inputLocked = false
                if (answerActive) stopAnswer(finished = true)
                return
            }
            val dir = animQueue.removeAt(0)
            val s = state
            if (s != null) {
                s.tryMove(dir)
                binding.gameBoard.refresh()
                updateUi()
                if (s.won) {
                    animQueue.clear()
                    animRunning = false
                    inputLocked = false
                    if (answerActive) stopAnswer(finished = true)
                    showWin()
                    return
                }
            }
            handler.postDelayed(this, ANIM_INTERVAL_MS)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        levels = LevelRepository.load(this)
        binding.gameBoard.listener = this

        setupSpinner()
        setupButtons()

        val last = getLastLevel()
        loadLevel(last, updateSpinner = true)
    }

    override fun onDestroy() {
        clearAnim()
        super.onDestroy()
    }

    private fun setupSpinner() {
        val labels = levels.mapIndexed { i, lv ->
            getString(R.string.level_item, i + 1, lv.name)
        }
        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, labels)
        binding.levelSpinner.adapter = adapter
        binding.levelSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                if (!spinnerReady) return
                if (state?.levelIndex == position) return
                loadLevel(position, updateSpinner = false)
            }

            override fun onNothingSelected(parent: AdapterView<*>?) = Unit
        }
    }

    private fun setupButtons() {
        binding.undoBtn.setOnClickListener { undo() }
        binding.resetBtn.setOnClickListener { resetLevel() }
        binding.helpBtn.setOnClickListener { showHelp() }
        binding.viewAnswerBtn.setOnClickListener { toggleAnswer() }
        binding.nextLevelBtn.setOnClickListener { goNextLevel() }
        binding.prevLevelBtn.setOnClickListener { goPrevLevel() }
        binding.nextLevelBtnToolbar.setOnClickListener { goNextLevel() }

        // 点按一步 + 按住连发（对齐 html_app 键盘按住）
        setupDpad(binding.btnUp, Direction.UP)
        setupDpad(binding.btnDown, Direction.DOWN)
        setupDpad(binding.btnLeft, Direction.LEFT)
        setupDpad(binding.btnRight, Direction.RIGHT)
    }

    private fun setupDpad(button: View, dir: Direction) {
        var holdRunnable: Runnable? = null
        button.setOnTouchListener { v, event ->
            when (event.action) {
                android.view.MotionEvent.ACTION_DOWN -> {
                    v.isPressed = true
                    tryDirectionalMove(dir)
                    val repeat = object : Runnable {
                        override fun run() {
                            if (inputLocked || answerActive) return
                            tryDirectionalMove(dir)
                            handler.postDelayed(this, HOLD_INTERVAL_MS)
                        }
                    }
                    holdRunnable = repeat
                    handler.postDelayed(repeat, HOLD_DELAY_MS)
                    true
                }
                android.view.MotionEvent.ACTION_UP,
                android.view.MotionEvent.ACTION_CANCEL -> {
                    v.isPressed = false
                    holdRunnable?.let { handler.removeCallbacks(it) }
                    holdRunnable = null
                    true
                }
                else -> false
            }
        }
    }

    private fun loadLevel(index: Int, updateSpinner: Boolean) {
        if (levels.isEmpty()) return
        val i = index.coerceIn(0, levels.lastIndex)
        clearAnim()
        answerActive = false
        val level = levels[i]
        state = GameState.fromLevel(level, i)
        saveLastLevel(i)
        binding.gameBoard.setState(state)
        hideWin()
        if (updateSpinner) {
            spinnerReady = false
            binding.levelSpinner.setSelection(i, false)
            spinnerReady = true
        } else {
            spinnerReady = true
        }
        updateUi()
    }

    private fun resetLevel() {
        val idx = state?.levelIndex ?: return
        loadLevel(idx, updateSpinner = false)
    }

    private fun undo() {
        if (inputLocked || answerActive) return
        val s = state ?: return
        if (s.won) return
        s.undo()
        binding.gameBoard.refresh()
        updateUi()
    }

    private fun tryDirectionalMove(dir: Direction) {
        if (inputLocked || answerActive) return
        val s = state ?: return
        if (s.won) return
        if (s.tryMove(dir)) {
            binding.gameBoard.refresh()
            updateUi()
            if (s.won) showWin()
        }
    }

    override fun onCellTap(gridX: Int, gridY: Int) {
        if (inputLocked || answerActive) return
        val s = state ?: return
        if (s.won) return

        // 点击相邻箱子 → 推一格
        if (s.isBox(gridX, gridY)) {
            val dx = gridX - s.player.x
            val dy = gridY - s.player.y
            if (kotlin.math.abs(dx) + kotlin.math.abs(dy) == 1) {
                if (s.tryMove(dx, dy)) {
                    binding.gameBoard.refresh()
                    updateUi()
                    if (s.won) showWin()
                }
            }
            return
        }

        // 点击空地 → BFS 寻路，同步走完
        if (!s.isWall(gridX, gridY) && !s.isBox(gridX, gridY)) {
            val path = Pathfinding.findPath(s, gridX, gridY) ?: return
            if (path.isEmpty()) return
            for (dir in path) {
                s.tryMove(dir)
                if (s.won) break
            }
            binding.gameBoard.refresh()
            updateUi()
            if (s.won) showWin()
        }
    }

    private fun toggleAnswer() {
        if (answerActive) {
            stopAnswer(finished = false)
        } else {
            startAnswer()
        }
    }

    private fun startAnswer() {
        val s = state ?: return
        if (s.won) return
        val level = levels.getOrNull(s.levelIndex) ?: return
        if (!level.hasSolution()) {
            Toast.makeText(this, R.string.answer_unavailable, Toast.LENGTH_SHORT).show()
            updateUi()
            return
        }
        // 重置后回放
        loadLevel(s.levelIndex, updateSpinner = false)
        val solution = level.solution ?: return
        val queue = parseSolution(solution)
        if (queue.isEmpty()) {
            Toast.makeText(this, R.string.answer_unavailable, Toast.LENGTH_SHORT).show()
            return
        }
        answerActive = true
        startAnimQueue(queue)
        binding.aiStatusText.text = getString(R.string.answer_playing, queue.size)
        updateAnswerButton()
    }

    private fun stopAnswer(finished: Boolean) {
        answerActive = false
        clearAnim()
        if (!finished) {
            // 停止时保持当前盘面，仅解除锁定
        }
        updateUi()
    }

    private fun parseSolution(solution: String): List<Direction> {
        val list = ArrayList<Direction>()
        for (ch in solution) {
            Direction.fromCode(ch)?.let { list.add(it) }
        }
        return list
    }

    private fun startAnimQueue(queue: List<Direction>) {
        clearAnim()
        if (queue.isEmpty()) return
        animQueue.addAll(queue)
        animRunning = true
        inputLocked = true
        handler.post(animRunnable)
    }

    private fun clearAnim() {
        handler.removeCallbacks(animRunnable)
        animQueue.clear()
        animRunning = false
        inputLocked = false
    }

    private fun goNextLevel() {
        val s = state ?: return
        val next = s.levelIndex + 1
        if (next < levels.size) {
            loadLevel(next, updateSpinner = true)
        } else {
            hideWin()
            Toast.makeText(this, "已经是最后一关", Toast.LENGTH_SHORT).show()
        }
    }

    private fun goPrevLevel() {
        val s = state ?: return
        val prev = s.levelIndex - 1
        if (prev >= 0) {
            loadLevel(prev, updateSpinner = true)
        }
    }

    private fun showWin() {
        val s = state ?: return
        binding.winMovesText.text = getString(R.string.win_moves, s.moves)
        binding.winOverlay.visibility = View.VISIBLE
        updateUi()
    }

    private fun hideWin() {
        binding.winOverlay.visibility = View.GONE
    }

    private fun showHelp() {
        AlertDialog.Builder(this)
            .setTitle(R.string.help_title)
            .setMessage(R.string.help_body)
            .setPositiveButton(R.string.close, null)
            .show()
    }

    private fun updateUi() {
        val s = state
        if (s != null) {
            binding.moveCountText.text = getString(R.string.moves_format, s.moves)
            binding.moveCountText.contentDescription =
                getString(R.string.moves_content_desc, s.moves)
        }
        updateAnswerButton()
    }

    private fun updateAnswerButton() {
        val s = state
        if (s == null) {
            binding.viewAnswerBtn.isEnabled = false
            binding.viewAnswerBtn.setImageResource(R.drawable.ic_answer)
            binding.viewAnswerBtn.contentDescription = getString(R.string.view_answer)
            binding.aiStatusText.text = ""
            return
        }
        if (answerActive) {
            binding.viewAnswerBtn.isEnabled = true
            binding.viewAnswerBtn.setImageResource(R.drawable.ic_stop)
            binding.viewAnswerBtn.contentDescription = getString(R.string.stop_answer)
            return
        }
        val level = levels.getOrNull(s.levelIndex)
        val hasSol = level?.hasSolution() == true
        binding.viewAnswerBtn.isEnabled = hasSol && !s.won
        binding.viewAnswerBtn.alpha = if (hasSol && !s.won) 1f else 0.4f
        binding.viewAnswerBtn.setImageResource(R.drawable.ic_answer)
        binding.viewAnswerBtn.contentDescription = getString(R.string.view_answer)
        binding.aiStatusText.text = when {
            s.won -> getString(R.string.cleared)
            hasSol -> getString(R.string.answer_available)
            else -> getString(R.string.answer_unavailable)
        }
    }

    private fun prefs() = getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    private fun getLastLevel(): Int {
        val n = prefs().getInt(KEY_LAST_LEVEL, 0)
        return if (n in levels.indices) n else 0
    }

    private fun saveLastLevel(index: Int) {
        prefs().edit().putInt(KEY_LAST_LEVEL, index).apply()
    }

    companion object {
        private const val PREFS = "sokoban"
        private const val KEY_LAST_LEVEL = "last_level"
        private const val ANIM_INTERVAL_MS = 60L
        private const val HOLD_DELAY_MS = 180L
        private const val HOLD_INTERVAL_MS = 90L
    }
}
