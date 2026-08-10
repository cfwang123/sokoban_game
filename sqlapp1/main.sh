#!/usr/bin/env bash
# sqlapp1 — SQLite 推箱子（教学驱动）
# 状态存在 DB；玩法用 SQL 更新。需要 sqlite3。
set -euo pipefail
DIR=$(cd "$(dirname "$0")" && pwd)
DB=${SOKOBAN_DB:-"$DIR/sokoban.db"}
rm -f "$DB"
sqlite3 "$DB" < "$DIR/schema.sql"
# generate_series may need SQLite 3.39+; fallback init without it if needed
if ! sqlite3 "$DB" < "$DIR/init_level.sql" 2>/dev/null; then
  sqlite3 "$DB" < "$DIR/init_level_compat.sql"
fi

render() {
  sqlite3 -batch "$DB" <<'SQL'
.mode list
SELECT group_concat(line, char(10)) FROM (
  SELECT y,
    group_concat(
      CASE
        WHEN p.x = c.x AND p.y = c.y AND c.kind IN ('goal','box_goal') THEN '+'
        WHEN p.x = c.x AND p.y = c.y THEN '@'
        WHEN c.kind = 'wall' THEN '#'
        WHEN c.kind = 'box' THEN '$'
        WHEN c.kind = 'box_goal' THEN '*'
        WHEN c.kind = 'goal' THEN '.'
        ELSE ' '
      END, ''
    ) AS line
  FROM cell c
  CROSS JOIN player p
  GROUP BY y
  ORDER BY y
);
SELECT 'moves=' || moves || CASE WHEN won THEN ' WIN!' ELSE '' END FROM meta WHERE id=1;
SQL
}

try_move() {
  local dx=$1 dy=$2
  sqlite3 "$DB" "SELECT 1;" >/dev/null
  # use a SQL file with parameters via temp
  sqlite3 "$DB" <<SQL
BEGIN;
-- block if won
SELECT CASE WHEN won=1 THEN RAISE(ABORT,'won') END FROM meta WHERE id=1;
-- compute next
WITH p AS (SELECT x,y FROM player WHERE id=1),
n AS (SELECT p.x+($dx) AS nx, p.y+($dy) AS ny FROM p),
dst AS (SELECT c.kind FROM cell c, n WHERE c.x=n.nx AND c.y=n.ny)
SELECT CASE WHEN (SELECT kind FROM dst)='wall' THEN RAISE(ABORT,'wall') END;
-- if box
WITH p AS (SELECT x,y FROM player WHERE id=1),
n AS (SELECT p.x+($dx) AS nx, p.y+($dy) AS ny FROM p),
dst AS (SELECT c.x,c.y,c.kind FROM cell c, n WHERE c.x=n.nx AND c.y=n.ny)
SELECT CASE
  WHEN kind IN ('box','box_goal') THEN (
    WITH bto AS (SELECT n.nx+($dx) AS bx, n.ny+($dy) AS by FROM n),
    beyond AS (SELECT c.kind FROM cell c, bto WHERE c.x=bto.bx AND c.y=bto.by)
    SELECT CASE WHEN (SELECT kind FROM beyond) IN ('wall','box','box_goal') THEN RAISE(ABORT,'blocked') END
  )
END FROM dst;
-- perform
WITH p AS (SELECT x AS px, y AS py FROM player WHERE id=1),
n AS (SELECT px+($dx) AS nx, py+($dy) AS ny FROM p),
dst AS (SELECT * FROM cell, n WHERE x=nx AND y=ny)
-- record hist
INSERT INTO hist(px,py,bfx,bfy,btx,bty,is_push)
SELECT p.px, p.py,
  CASE WHEN dst.kind IN ('box','box_goal') THEN dst.x END,
  CASE WHEN dst.kind IN ('box','box_goal') THEN dst.y END,
  CASE WHEN dst.kind IN ('box','box_goal') THEN dst.x+($dx) END,
  CASE WHEN dst.kind IN ('box','box_goal') THEN dst.y+($dy) END,
  CASE WHEN dst.kind IN ('box','box_goal') THEN 1 ELSE 0 END
FROM p, dst;

-- move box if needed
UPDATE cell SET kind = CASE kind WHEN 'box_goal' THEN 'goal' ELSE 'floor' END
WHERE (x,y) IN (SELECT nx,ny FROM (SELECT px+($dx) nx, py+($dy) ny FROM player WHERE id=1) t)
  AND kind IN ('box','box_goal')
  AND EXISTS (
    SELECT 1 FROM cell c2
    WHERE c2.x = (SELECT px+($dx)*2 FROM player WHERE id=1)
      AND c2.y = (SELECT py+($dy)*2 FROM player WHERE id=1)
      AND c2.kind IN ('floor','goal')
  );

UPDATE cell SET kind = CASE kind WHEN 'goal' THEN 'box_goal' ELSE 'box' END
WHERE x = (SELECT px+($dx)*2 FROM player WHERE id=1)
  AND y = (SELECT py+($dy)*2 FROM player WHERE id=1)
  AND kind IN ('floor','goal')
  AND EXISTS (
    SELECT 1 FROM cell c0
    WHERE c0.x=(SELECT px+($dx) FROM player WHERE id=1)
      AND c0.y=(SELECT py+($dy) FROM player WHERE id=1)
      -- after previous update box already moved from here; check hist instead
  );

-- simpler approach: abort this complex SQL path — handled in main.py/sh helpers
ROLLBACK;
SQL
}

echo "sokoban_sql — wasd 移动, z 撤销, r 重置, q 退出"
echo "（完整移动逻辑见 main.py / move.sql；本 shell 仅演示渲染）"
echo
echo "推荐: python -X utf8 main.py"
render
