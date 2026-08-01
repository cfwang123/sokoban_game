package com.whj.sokoban.game

data class LevelData(
    val id: Int,
    val name: String,
    val puzzle: List<String>,
    val solution: String?,
) {
    fun hasSolution(): Boolean = !solution.isNullOrBlank()
}
