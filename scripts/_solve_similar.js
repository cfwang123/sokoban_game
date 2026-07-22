// 相似的经典布局（空地版 / 6箱）—— 你记的可能是这个
const { buildSolver } = require('./solver_opt.js');

const variants = [
  {
    name: '你写的版本（16箱，*与$填满）',
    rows: [
      '#######',
      '#*.*.*#',
      '#.$$$.#',
      '#*$@$*#',
      '#.$$$.#',
      '#*.*.*#',
      '#######',
    ],
  },
  {
    name: '空地版6箱（. . . 与 $$$）',
    rows: [
      '#######',
      '#. . .#',
      '# $$$ #',
      '#.$@$.#',
      '# $$$ #',
      '#. . .#',
      '#######',
    ],
  },
  {
    name: '目标在四角星位、中间空',
    rows: [
      '#######',
      '#*.*.*#',
      '# $$$ #',
      '# $@$ #',
      '# $$$ #',
      '#*.*.*#',
      '#######',
    ],
  },
  {
    name: '全部.作目标、中间$与@',
    rows: [
      '#######',
      '#.....#',
      '#.$$$.#',
      '#.$@$.#',
      '#.$$$.#',
      '#.....#',
      '#######',
    ],
  },
];

for (const v of variants) {
  console.log('\n========', v.name, '========');
  v.rows.forEach(r => console.log(r));
  let boxes = 0, goals = 0;
  for (const row of v.rows)
    for (const c of row) {
      if (c === '$' || c === '*') boxes++;
      if (c === '.' || c === '*' || c === '+') goals++;
    }
  console.log('boxes', boxes, 'goals', goals);

  try {
    const { solve } = buildSolver(v.rows);
    const r = solve(15000, 'bf');
    if (r.ok) {
      console.log(`SOLVED ${r.ms}ms pushes=${r.pushes}`);
      console.log('path (LURD pushes):', r.path);
    } else {
      console.log(`FAIL ${r.ms}ms nodes=${r.nodes}`);
    }
  } catch (e) {
    console.log('ERR', e.message);
  }
}
