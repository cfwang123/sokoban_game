-- 迷你关卡加载
DELETE FROM cell;
DELETE FROM player;
DELETE FROM hist;
UPDATE meta SET moves = 0, won = 0 WHERE id = 1;

-- #######
-- #. . .#
-- # $$$ #
-- #.$@$.#
-- # $$$ #
-- #. . .#
-- #######
WITH raw(y, row) AS (
  VALUES
    (0, '#######'),
    (1, '#. . .#'),
    (2, '# $$$ #'),
    (3, '#.$@$.#'),
    (4, '# $$$ #'),
    (5, '#. . .#'),
    (6, '#######')
),
chars AS (
  SELECT y,
         value - 1 AS x,
         substr(row, value, 1) AS ch
  FROM raw
  JOIN generate_series(1, length(row))
)
INSERT INTO cell(x, y, kind)
SELECT x, y,
  CASE ch
    WHEN '#' THEN 'wall'
    WHEN '.' THEN 'goal'
    WHEN '$' THEN 'box'
    WHEN '*' THEN 'box_goal'
    WHEN '@' THEN 'floor'
    WHEN '+' THEN 'goal'
    ELSE 'floor'
  END
FROM chars
WHERE ch != ' ';

INSERT INTO player(id, x, y)
SELECT 1, value - 1, y
FROM (
  SELECT y, row FROM (VALUES
    (0, '#######'),
    (1, '#. . .#'),
    (2, '# $$$ #'),
    (3, '#.$@$.#'),
    (4, '# $$$ #'),
    (5, '#. . .#'),
    (6, '#######')
  ) AS t(y, row)
)
JOIN generate_series(1, length(row))
WHERE substr(row, value, 1) IN ('@', '+')
LIMIT 1;
