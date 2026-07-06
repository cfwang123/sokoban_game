// AI 求解器：状态空间 BFS + 角落死锁剪枝

// 检测箱子是否处于死锁位置（非目标的角落）
function isDeadlocked(boxKey, walls, goals) {
  if (goals.has(boxKey)) return false;
  const [x, y] = boxKey.split(',').map(Number);

  // 检查四个方向的墙相邻情况
  const up = walls.has(x + ',' + (y - 1));
  const down = walls.has(x + ',' + (y + 1));
  const left = walls.has((x - 1) + ',' + y);
  const right = walls.has((x + 1) + ',' + y);

  // 角落：两面相邻墙
  if (up && left) return true;
  if (up && right) return true;
  if (down && left) return true;
  if (down && right) return true;

  return false;
}

// 检查状态中是否有死锁箱子
function hasDeadlock(boxes, walls, goals) {
  for (const b of boxes) {
    if (isDeadlocked(b, walls, goals)) return true;
  }
  return false;
}

// 状态序列化
function stateKey(player, boxes) {
  const sorted = Array.from(boxes).sort();
  return player.x + ',' + player.y + '|' + sorted.join(';');
}

// AI 求解主函数
// 返回方向数组，或 null（未找到解）
function aiSolve(state) {
  const walls = state.walls;
  const goals = state.goals;
  const maxNodes = 50000;

  const dirs = [
    { dx: 0, dy: -1, name: 'up' },
    { dx: 0, dy: 1, name: 'down' },
    { dx: -1, dy: 0, name: 'left' },
    { dx: 1, dy: 0, name: 'right' }
  ];

  // 初始状态
  const startBoxes = new Set(state.boxes);
  const startPlayer = { x: state.player.x, y: state.player.y };

  const queue = [{
    player: startPlayer,
    boxes: startBoxes,
    path: []
  }];
  let queueIdx = 0;

  const visited = new Set();
  visited.add(stateKey(startPlayer, startBoxes));

  let nodeCount = 0;

  while (queueIdx < queue.length && nodeCount < maxNodes) {
    const cur = queue[queueIdx++];
    nodeCount++;

    // 检查是否胜利
    let won = true;
    for (const b of cur.boxes) {
      if (!goals.has(b)) { won = false; break; }
    }
    if (won) return cur.path;

    for (const d of dirs) {
      const nx = cur.player.x + d.dx;
      const ny = cur.player.y + d.dy;
      const nKey = nx + ',' + ny;

      // 撞墙
      if (walls.has(nKey)) continue;

      const newBoxes = new Set(cur.boxes);

      // 推箱子
      if (cur.boxes.has(nKey)) {
        const bx = nx + d.dx;
        const by = ny + d.dy;
        const bKey = bx + ',' + by;

        // 箱子后方有障碍
        if (walls.has(bKey) || cur.boxes.has(bKey)) continue;

        newBoxes.delete(nKey);
        newBoxes.add(bKey);

        // 死锁剪枝
        if (isDeadlocked(bKey, walls, goals)) continue;
      }

      const newPlayer = { x: nx, y: ny };
      const sk = stateKey(newPlayer, newBoxes);
      if (visited.has(sk)) continue;
      visited.add(sk);

      queue.push({
        player: newPlayer,
        boxes: newBoxes,
        path: cur.path.concat([d.name])
      });
    }
  }

  return null; // 未找到解
}
