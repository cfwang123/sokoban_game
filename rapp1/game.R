# 推箱子核心逻辑（R 教学）

key <- function(x, y) paste0(x, ",", y)

from_rows <- function(rows, index = 0L) {
  walls <- character(0)
  goals <- character(0)
  boxes <- character(0)
  player <- c(0L, 0L)
  max_x <- 0L
  max_y <- 0L
  for (y in seq_along(rows)) {
    yi <- as.integer(y - 1L)
    max_y <- yi
    row <- rows[[y]]
    chars <- strsplit(row, "", fixed = TRUE)[[1]]
    for (x in seq_along(chars)) {
      xi <- as.integer(x - 1L)
      if (xi > max_x) max_x <- xi
      ch <- chars[[x]]
      k <- key(xi, yi)
      if (ch == "#") walls <- c(walls, k)
      else if (ch == ".") goals <- c(goals, k)
      else if (ch == "$") boxes <- c(boxes, k)
      else if (ch == "*") {
        boxes <- c(boxes, k)
        goals <- c(goals, k)
      } else if (ch == "@") player <- c(xi, yi)
      else if (ch == "+") {
        player <- c(xi, yi)
        goals <- c(goals, k)
      }
    }
  }
  list(
    walls = unique(walls),
    goals = unique(goals),
    boxes = unique(boxes),
    player = player,
    moves = 0L,
    won = FALSE,
    width = max_x + 1L,
    height = max_y + 1L,
    level_index = as.integer(index),
    hist = list()
  )
}

check_win <- function(state) {
  all(state$boxes %in% state$goals)
}

try_move <- function(state, dx, dy) {
  if (isTRUE(state$won)) return(state)
  px <- state$player[1]
  py <- state$player[2]
  nx <- px + dx
  ny <- py + dy
  nk <- key(nx, ny)
  if (nk %in% state$walls) return(state)
  if (nk %in% state$boxes) {
    bx <- nx + dx
    by <- ny + dy
    bk <- key(bx, by)
    if (bk %in% state$walls || bk %in% state$boxes) return(state)
    state$hist[[length(state$hist) + 1L]] <- list(
      player = c(px, py), box_from = nk, box_to = bk
    )
    state$boxes <- setdiff(state$boxes, nk)
    state$boxes <- c(state$boxes, bk)
    state$player <- c(nx, ny)
    state$moves <- state$moves + 1L
    state$won <- check_win(state)
    return(state)
  }
  state$hist[[length(state$hist) + 1L]] <- list(
    player = c(px, py), box_from = NULL, box_to = NULL
  )
  state$player <- c(nx, ny)
  state
}

undo <- function(state) {
  if (isTRUE(state$won) || length(state$hist) == 0L) return(state)
  entry <- NULL
  while (length(state$hist) > 0L) {
    entry <- state$hist[[length(state$hist)]]
    state$hist <- state$hist[-length(state$hist)]
    if (!is.null(entry$box_from)) break
    state$player <- entry$player
  }
  if (is.null(entry) || is.null(entry$box_from)) return(state)
  state$player <- entry$player
  state$boxes <- setdiff(state$boxes, entry$box_to)
  state$boxes <- c(state$boxes, entry$box_from)
  if (state$moves > 0L) state$moves <- state$moves - 1L
  state$won <- FALSE
  state
}

render_ascii <- function(state) {
  lines <- character(state$height)
  for (y in seq_len(state$height) - 1L) {
    row <- character(state$width)
    for (x in seq_len(state$width) - 1L) {
      k <- key(x, y)
      if (state$player[1] == x && state$player[2] == y) {
        row[x + 1L] <- if (k %in% state$goals) "+" else "@"
      } else if (k %in% state$boxes) {
        row[x + 1L] <- if (k %in% state$goals) "*" else "$"
      } else if (k %in% state$walls) {
        row[x + 1L] <- "#"
      } else if (k %in% state$goals) {
        row[x + 1L] <- "."
      } else {
        row[x + 1L] <- " "
      }
    }
    lines[y + 1L] <- paste0(row, collapse = "")
  }
  paste0(paste(lines, collapse = "\n"), "\n")
}
