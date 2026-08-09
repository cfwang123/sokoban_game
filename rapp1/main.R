#!/usr/bin/env Rscript
# rapp1 — 推箱子终端版（教学）

args_cmd <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args_cmd, value = TRUE)
script_dir <- if (length(file_arg) == 1L) {
  dirname(normalizePath(sub("^--file=", "", file_arg)))
} else {
  getwd()
}
source(file.path(script_dir, "game.R"), local = FALSE)

LEVEL <- c(
  "#######",
  "#. . .#",
  "# $$$ #",
  "#.$@$.#",
  "# $$$ #",
  "#. . .#",
  "#######"
)

state <- from_rows(LEVEL, 0L)
cat("sokoban_r — wasd 移动, z 撤销, r 重置, q 退出\n")

repeat {
  cat("\n")
  cat(render_ascii(state))
  flag <- if (isTRUE(state$won)) " WIN!" else ""
  cat(sprintf("moves=%d%s\n> ", state$moves, flag))
  line <- tryCatch(readLines("stdin", n = 1L, warn = FALSE), error = function(e) character(0))
  if (length(line) == 0L) break
  line <- trimws(line)
  if (!nzchar(line)) next
  ch <- tolower(substr(line, 1L, 1L))
  if (ch == "w") state <- try_move(state, 0L, -1L)
  else if (ch == "s") state <- try_move(state, 0L, 1L)
  else if (ch == "a") state <- try_move(state, -1L, 0L)
  else if (ch == "d") state <- try_move(state, 1L, 0L)
  else if (ch == "z") state <- undo(state)
  else if (ch == "r") state <- from_rows(LEVEL, 0L)
  else if (ch == "q") break
  if (isTRUE(state$won)) cat("Level clear!\n")
}
