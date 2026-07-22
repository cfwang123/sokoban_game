<?php
$rows = [
  "#######",
  "#*.*.*#",
  "#.$$$.#",
  "#*$@$*#",
  "#.$$$.#",
  "#*.*.*#",
  "#######",
];
// reuse buildSolver from solver_opt - need to not run main
// extract by including after defining argv skip
$_SERVER['argv'] = ['x', '0', '1', 'bf'];
// simpler: paste call
function loadSolver() {
  $src = file_get_contents(__DIR__ . '/solver_opt.php');
  // strip main execution - the file always runs main. copy buildSolver only via require after patch
}
echo "use node result primarily\n";
