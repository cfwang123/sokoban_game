package com.whj.sokoban.game

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject

object LevelRepository {

    @Volatile
    private var cached: List<LevelData>? = null

    fun load(context: Context): List<LevelData> {
        cached?.let { return it }
        synchronized(this) {
            cached?.let { return it }
            val json = context.assets.open("levels.json").bufferedReader(Charsets.UTF_8).use { it.readText() }
            val arr = JSONArray(json)
            val list = ArrayList<LevelData>(arr.length())
            for (i in 0 until arr.length()) {
                val obj = arr.getJSONObject(i)
                list.add(parseLevel(obj, i))
            }
            cached = list
            return list
        }
    }

    private fun parseLevel(obj: JSONObject, fallbackId: Int): LevelData {
        val id = if (obj.has("id") && !obj.isNull("id")) obj.getInt("id") else fallbackId
        val name = obj.optString("name", "Level ${id + 1}")
        val puzzleArr = obj.getJSONArray("puzzle")
        val puzzle = ArrayList<String>(puzzleArr.length())
        for (r in 0 until puzzleArr.length()) {
            puzzle.add(puzzleArr.getString(r))
        }
        val solution = when {
            !obj.has("solution") || obj.isNull("solution") -> null
            else -> obj.optString("solution").ifBlank { null }
        }
        return LevelData(id = id, name = name, puzzle = puzzle, solution = solution)
    }
}
