const { buildSolver } = require('./solver_opt.js');
const rows = [
  '#######',
  '#*.*.*#',
  '#.$$$.#',
  '#*$@$*#',
  '#.$$$.#',
  '#*.*.*#',
  '#######',
];
console.log(rows.join('\n'));
const { solve } = buildSolver(rows);
for (const mode of ['bf', 'dfs', 'auto']) {
  const r = solve(60000, mode);
  if (r.ok) {
    console.log(`SOLVED mode=${mode} ${r.ms}ms pushes=${r.pushes}`);
    console.log(`path: ${r.path}`);
    process.exit(0);
  }
  console.log(`FAIL mode=${mode} ${r.ms}ms nodes=${r.nodes} visited=${r.visited}`);
}
process.exit(1);
