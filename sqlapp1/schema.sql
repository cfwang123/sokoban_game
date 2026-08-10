-- sqlapp1 — Sokoban state in SQLite（教学）
-- 地图格：kind in wall/goal/box/floor；玩家单独表

DROP TABLE IF EXISTS cell;
DROP TABLE IF EXISTS player;
DROP TABLE IF EXISTS meta;
DROP TABLE IF EXISTS hist;

CREATE TABLE cell (
  x INTEGER NOT NULL,
  y INTEGER NOT NULL,
  kind TEXT NOT NULL, -- wall | floor | goal | box | box_goal
  PRIMARY KEY (x, y)
);

CREATE TABLE player (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  x INTEGER NOT NULL,
  y INTEGER NOT NULL
);

CREATE TABLE meta (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  moves INTEGER NOT NULL DEFAULT 0,
  won INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE hist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  px INTEGER NOT NULL,
  py INTEGER NOT NULL,
  bfx INTEGER,
  bfy INTEGER,
  btx INTEGER,
  bty INTEGER,
  is_push INTEGER NOT NULL
);

INSERT INTO meta(id, moves, won) VALUES (1, 0, 0);
