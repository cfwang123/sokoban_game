// BFS 寻路：从玩家位置到目标格子，避开墙和箱子
// 返回方向数组 ['up','down','left','right'] 或 null

function findPath(state, targetX, targetY) {
  const startKey = state.player.x + ',' + state.player.y;
  const targetKey = targetX + ',' + targetY;

  if (startKey === targetKey) return [];

  // 障碍物：墙 + 箱子
  const blocked = new Set(state.walls);
  for (const b of state.boxes) blocked.add(b);

  const queue = [{ x: state.player.x, y: state.player.y }];
  const visited = new Set([startKey]);
  const parent = new Map(); // "x,y" -> { from: "x,y", dir: string }

  const dirs = [
    { dx: 0, dy: -1, name: 'up' },
    { dx: 0, dy: 1, name: 'down' },
    { dx: -1, dy: 0, name: 'left' },
    { dx: 1, dy: 0, name: 'right' }
  ];

  while (queue.length > 0) {
    const cur = queue.shift();
    const curKey = cur.x + ',' + cur.y;

    for (const d of dirs) {
      const nx = cur.x + d.dx;
      const ny = cur.y + d.dy;
      const nKey = nx + ',' + ny;

      if (blocked.has(nKey) || visited.has(nKey)) continue;
      visited.add(nKey);
      parent.set(nKey, { from: curKey, dir: d.name });

      if (nKey === targetKey) {
        // 回溯路径
        const path = [];
        let p = nKey;
        while (p !== startKey) {
          const info = parent.get(p);
          path.unshift(info.dir);
          p = info.from;
        }
        return path;
      }

      queue.push({ x: nx, y: ny });
    }
  }

  return null; // 无路径
}
