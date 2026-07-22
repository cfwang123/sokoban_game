<?php
/**
 * Sokoban 求解器 PHP 8 + JIT
 * 用法: php -d opcache.enable_cli=1 -d opcache.jit=tracing -d opcache.jit_buffer_size=128M scripts/solver_opt.php [id] [ms] [mode]
 * mode: dfs|bf|auto
 */

declare(strict_types=1);

$levelId = isset($argv[1]) ? (int)$argv[1] : 128;
$timeLimit = isset($argv[2]) ? (int)$argv[2] : 5000;
$mode = isset($argv[3]) ? strtolower($argv[3]) : 'dfs';

$jsonPath = dirname(__DIR__) . DIRECTORY_SEPARATOR . 'levels.json';
$data = json_decode(file_get_contents($jsonPath), true);
$level = null;
foreach ($data as $L) {
    if ((int)$L['id'] === $levelId) { $level = $L; break; }
}
if (!$level) { fwrite(STDERR, "Level not found\n"); exit(1); }

echo "Level id={$level['id']} name={$level['name']} mode={$mode}\n";
foreach ($level['puzzle'] as $r) echo "  $r\n";

// JIT 状态
$jit = function_exists('opcache_get_status') ? opcache_get_status(false) : false;
$jitOn = is_array($jit) && !empty($jit['jit']['enabled']);
echo "PHP " . PHP_VERSION . " JIT=" . ($jitOn ? 'ON' : 'OFF') . "\n";

$solver = buildSolver($level['puzzle']);
echo "\nSolving (limit {$timeLimit}ms)...\n";
$r = $solver['solve']($timeLimit, $mode);

if (!empty($r['ok'])) {
    echo "SOLVED in {$r['ms']}ms  pushes={$r['pushes']}  nodes={$r['nodes']}  exp={$r['expansions']}  dir={$r['dir']}\n";
    echo "path: {$r['path']}\n";
} else {
    echo "FAILED in {$r['ms']}ms  nodes={$r['nodes']}  exp={$r['expansions']}  dir={$r['dir']}  visited={$r['visited']}\n";
}

// ----------------------------------------------------------------
function buildSolver(array $levelRows): array
{
    $H = count($levelRows);
    $WW = 0;
    foreach ($levelRows as $r) $WW = max($WW, strlen($r));
    $rows = [];
    foreach ($levelRows as $r) $rows[] = str_pad($r, $WW, '#');

    $cellX = []; $cellY = [];
    $wall = array_fill(0, $WW * $H, 0);
    $xyToId = array_fill(0, $WW * $H, -1);
    $sx = 0; $sy = 0;
    $startBoxList = []; $goalList = [];

    $flat = static function (int $x, int $y) use ($WW): int { return $y * $WW + $x; };

    for ($y = 0; $y < $H; $y++) {
        for ($x = 0; $x < $WW; $x++) {
            $c = $rows[$y][$x];
            if ($c === '#') { $wall[$flat($x, $y)] = 1; continue; }
            $id = count($cellX);
            $cellX[] = $x; $cellY[] = $y;
            $xyToId[$flat($x, $y)] = $id;
            if ($c === '.' || $c === '*' || $c === '+') $goalList[] = $id;
            if ($c === '$' || $c === '*') $startBoxList[] = $id;
            if ($c === '@' || $c === '+') { $sx = $x; $sy = $y; }
        }
    }

    $N = count($cellX);
    $NB = count($startBoxList);
    $isGoal = array_fill(0, $N, 0);
    foreach ($goalList as $g) $isGoal[$g] = 1;
    $startPlayer = $xyToId[$flat($sx, $sy)];

    $DX = [0, 0, -1, 1];
    $DY = [-1, 1, 0, 0];
    $DCH = ['u', 'd', 'l', 'r'];

    $neigh = array_fill(0, $N * 4, -1);
    $pushTo = array_fill(0, $N * 4, -1);
    $pushFrom = array_fill(0, $N * 4, -1);

    for ($i = 0; $i < $N; $i++) {
        $x = $cellX[$i]; $y = $cellY[$i];
        for ($d = 0; $d < 4; $d++) {
            $nx = $x + $DX[$d]; $ny = $y + $DY[$d];
            if ($nx < 0 || $ny < 0 || $nx >= $WW || $ny >= $H || $wall[$flat($nx, $ny)]) continue;
            $nid = $xyToId[$flat($nx, $ny)];
            if ($nid < 0) continue;
            $neigh[$i * 4 + $d] = $nid;
            $fx = $x - $DX[$d]; $fy = $y - $DY[$d];
            if ($fx < 0 || $fy < 0 || $fx >= $WW || $fy >= $H || $wall[$flat($fx, $fy)]) continue;
            $fid = $xyToId[$flat($fx, $fy)];
            if ($fid < 0) continue;
            $pushTo[$i * 4 + $d] = $nid;
            $pushFrom[$i * 4 + $d] = $fid;
        }
    }

    // reverse-BFS dead + goalDist
    $dead = array_fill(0, $N, 0);
    $goalDist = array_fill(0, $N, 32000);
    $q = [];
    foreach ($goalList as $g) {
        $goalDist[$g] = 0;
        $q[] = $g;
    }
    $qh = 0;
    while ($qh < count($q)) {
        $t = $q[$qh++];
        $x = $cellX[$t]; $y = $cellY[$t]; $bd = $goalDist[$t];
        for ($d = 0; $d < 4; $d++) {
            $Fx = $x - $DX[$d]; $Fy = $y - $DY[$d];
            $Px = $x - 2 * $DX[$d]; $Py = $y - 2 * $DY[$d];
            if ($Fx < 0 || $Fy < 0 || $Fx >= $WW || $Fy >= $H || $wall[$flat($Fx, $Fy)]) continue;
            if ($Px < 0 || $Py < 0 || $Px >= $WW || $Py >= $H || $wall[$flat($Px, $Py)]) continue;
            $fid = $xyToId[$flat($Fx, $Fy)];
            if ($fid < 0) continue;
            if ($goalDist[$fid] > $bd + 1) {
                $goalDist[$fid] = $bd + 1;
                $q[] = $fid;
            }
        }
    }
    for ($i = 0; $i < $N; $i++) {
        if ($isGoal[$i]) continue;
        if ($goalDist[$i] >= 32000) { $dead[$i] = 1; continue; }
        $x = $cellX[$i]; $y = $cellY[$i];
        $u = ($y === 0 || $wall[$flat($x, $y - 1)]);
        $dn = ($y === $H - 1 || $wall[$flat($x, $y + 1)]);
        $l = ($x === 0 || $wall[$flat($x - 1, $y)]);
        $r = ($x === $WW - 1 || $wall[$flat($x + 1, $y)]);
        if (($u && $l) || ($u && $r) || ($dn && $l) || ($dn && $r)) $dead[$i] = 1;
        elseif ($u && $dn && ($l || $r)) $dead[$i] = 1;
        elseif ($l && $r && ($u || $dn)) $dead[$i] = 1;
    }

    $degree = array_fill(0, $N, 0);
    for ($i = 0; $i < $N; $i++) {
        $deg = 0;
        for ($d = 0; $d < 4; $d++) if ($neigh[$i * 4 + $d] >= 0) $deg++;
        $degree[$i] = $deg;
    }

    // 箱子集合：排序后的 int 数组，状态键用 pack
    // 用 bitmask：N<=63 时 PHP 64-bit int 可用（bit 0..62）
    if ($N > 62) {
        throw new RuntimeException("N=$N too large for int bitmask");
    }

    $startMask = 0;
    foreach ($startBoxList as $b) $startMask |= (1 << $b);

    // reach buffers
    $visitGen = array_fill(0, $N, 0);
    $bfsQ = array_fill(0, $N, 0);
    $gen = 1;

    $computeReach = function (int $player, int $mask) use (
        &$visitGen, &$bfsQ, &$gen, $N, $neigh
    ): int {
        $gen++;
        if ($gen >= 0x7f000000) {
            $visitGen = array_fill(0, $N, 0);
            $gen = 1;
        }
        $qh = 0; $qt = 0; $minR = $player;
        $bfsQ[$qt++] = $player;
        $visitGen[$player] = $gen;
        $g = $gen;
        while ($qh < $qt) {
            $c = $bfsQ[$qh++];
            if ($c < $minR) $minR = $c;
            $base = $c << 2; // *4
            for ($d = 0; $d < 4; $d++) {
                $n = $neigh[$base + $d];
                if ($n < 0 || $visitGen[$n] === $g) continue;
                if (($mask & (1 << $n)) !== 0) continue;
                $visitGen[$n] = $g;
                $bfsQ[$qt++] = $n;
            }
        }
        return $minR;
    };

    $canReach = function (int $c) use (&$visitGen, &$gen): bool {
        return $visitGen[$c] === $gen;
    };

    $hFwd = function (int $mask) use ($N, $goalDist): int {
        $h = 0;
        for ($i = 0; $i < $N; $i++) {
            if (($mask & (1 << $i)) !== 0) {
                $d = $goalDist[$i];
                if ($d >= 32000) return 999999;
                $h += $d;
            }
        }
        return $h;
    };

    $isWin = function (int $mask) use ($N, $isGoal): bool {
        for ($i = 0; $i < $N; $i++) {
            if (($mask & (1 << $i)) !== 0 && !$isGoal[$i]) return false;
        }
        return true;
    };

    $is2x2 = function (int $mask, int $movedTo) use ($cellX, $cellY, $WW, $H, $wall, $xyToId, $isGoal, $flat): bool {
        $x = $cellX[$movedTo]; $y = $cellY[$movedTo];
        for ($ox = -1; $ox <= 0; $ox++) {
            for ($oy = -1; $oy <= 0; $oy++) {
                $all = true; $anyG = false;
                for ($dx = 0; $dx <= 1 && $all; $dx++) {
                    for ($dy = 0; $dy <= 1; $dy++) {
                        $cx = $x + $ox + $dx; $cy = $y + $oy + $dy;
                        if ($cx < 0 || $cy < 0 || $cx >= $WW || $cy >= $H || $wall[$flat($cx, $cy)]) {
                            $all = false; break;
                        }
                        $id = $xyToId[$flat($cx, $cy)];
                        if ($id < 0 || ($mask & (1 << $id)) === 0) { $all = false; break; }
                        if ($isGoal[$id]) $anyG = true;
                    }
                }
                if ($all && !$anyG) return true;
            }
        }
        return false;
    };

    // 生成后继：返回 list of [newMask, player, pathStr, h, pushes, fromBox]
    $genPushes = function (int $player, int $mask, int $lastBox) use (
        $computeReach, $canReach, $N, $pushTo, $pushFrom, $dead, $degree,
        $isGoal, $is2x2, $hFwd, $DCH
    ): array {
        $computeReach($player, $mask);
        $moves = [];
        for ($b = 0; $b < $N; $b++) {
            if (($mask & (1 << $b)) === 0) continue;
            $base = $b << 2;
            for ($d = 0; $d < 4; $d++) {
                $to = $pushTo[$base + $d];
                if ($to < 0) continue;
                if (($mask & (1 << $to)) !== 0) continue;
                $from = $pushFrom[$base + $d];
                if (!$canReach($from)) continue;
                if ($dead[$to]) continue;

                $nm = $mask ^ (1 << $b) ^ (1 << $to);
                $fTo = $to; $fPl = $b; $pc = 1; $ch = $DCH[$d];
                while ($degree[$fTo] === 2 && !$isGoal[$fTo]) {
                    $nx = $pushTo[($fTo << 2) + $d];
                    if ($nx < 0 || ($nm & (1 << $nx)) !== 0 || $dead[$nx]) break;
                    $nm ^= (1 << $fTo) ^ (1 << $nx);
                    $fPl = $fTo; $fTo = $nx; $pc++; $ch .= $DCH[$d];
                    if ($pc > 12) break;
                }
                if ($is2x2($nm, $fTo)) continue;
                $nh = $hFwd($nm);
                if ($nh >= 999999) continue;
                $score = $nh;
                if ($b === $lastBox) $score -= 1; // 惯性（整数分）
                if ($isGoal[$fTo] && !$isGoal[$b]) $score -= 1;
                if ($isGoal[$b] && !$isGoal[$fTo]) $score += 2;
                $moves[] = [$nm, $fPl, $ch, $nh, $pc, $b, $score];
            }
        }
        usort($moves, static function ($a, $b) { return $a[6] <=> $b[6]; });
        return $moves;
    };

    $solveDFS = function (int $tl) use (
        $startMask, $startPlayer, $computeReach, $genPushes, $isWin
    ): array {
        $T0 = hrtime(true);
        $tlNs = $tl * 1000000;
        $visited = [];
        $nodes = 0; $expansions = 0;
        $solution = null;

        $dfs = function (int $mask, int $player, int $g, string $path, int $lastBox) use (
            &$dfs, &$solution, &$visited, &$nodes, &$expansions, $T0, $tlNs,
            $genPushes, $computeReach, $isWin
        ): bool {
            if ($solution !== null) return true;
            if (($expansions & 1023) === 0 && (hrtime(true) - $T0) > $tlNs) return false;
            $expansions++;

            if ($isWin($mask)) {
                $solution = ['path' => $path, 'g' => $g];
                return true;
            }

            $moves = $genPushes($player, $mask, $lastBox);
            foreach ($moves as $m) {
                $nodes++;
                $nm = $m[0]; $npl = $m[1]; $ch = $m[2]; $pc = $m[4]; $fb = $m[5];
                $minR = $computeReach($npl, $nm);
                // key: mask 与 minR 拼成字符串（mask 作十进制）
                $k = $nm . '|' . $minR;
                $ng = $g + $pc;
                if (isset($visited[$k]) && $visited[$k] <= $ng) continue;
                $visited[$k] = $ng;
                if ($dfs($nm, $npl, $ng, $path . $ch, $fb)) return true;
            }
            return false;
        };

        $min0 = $computeReach($startPlayer, $startMask);
        $visited[$startMask . '|' . $min0] = 0;
        $dfs($startMask, $startPlayer, 0, '', -1);

        $ms = (int)((hrtime(true) - $T0) / 1000000);
        if ($solution) {
            return [
                'ok' => true, 'path' => $solution['path'], 'pushes' => $solution['g'],
                'nodes' => $nodes, 'expansions' => $expansions, 'ms' => $ms,
                'dir' => 'dfs', 'visited' => count($visited),
            ];
        }
        return [
            'ok' => false, 'nodes' => $nodes, 'expansions' => $expansions,
            'ms' => $ms, 'dir' => 'dfs', 'visited' => count($visited),
        ];
    };

    $solveBF = function (int $tl) use (
        $startMask, $startPlayer, $computeReach, $genPushes, $isWin, $hFwd
    ): array {
        $T0 = hrtime(true);
        $tlNs = $tl * 1000000;
        $h0 = $hFwd($startMask);
        if ($h0 >= 999999) {
            return ['ok' => false, 'nodes' => 0, 'expansions' => 0, 'ms' => 0, 'dir' => 'bf', 'visited' => 0];
        }

        // 二叉堆：元素 [f, mask, player, g, path, lastBox]
        $heap = [];
        $heapSize = 0;
        $heapPush = function ($f, $mask, $player, $g, $path, $lastBox) use (&$heap, &$heapSize) {
            $heap[$heapSize] = [$f, $mask, $player, $g, $path, $lastBox];
            $i = $heapSize++;
            while ($i > 0) {
                $p = ($i - 1) >> 1;
                if ($heap[$p][0] <= $heap[$i][0]) break;
                $t = $heap[$p]; $heap[$p] = $heap[$i]; $heap[$i] = $t;
                $i = $p;
            }
        };
        $heapPop = function () use (&$heap, &$heapSize) {
            $top = $heap[0];
            $heapSize--;
            if ($heapSize <= 0) {
                $heapSize = 0;
                return $top;
            }
            $heap[0] = $heap[$heapSize];
            // 不 unset，避免稀疏数组；用 heapSize 截断逻辑长度
            $i = 0;
            while (true) {
                $s = $i; $l = $i * 2 + 1; $r = $i * 2 + 2;
                if ($l < $heapSize && $heap[$l][0] < $heap[$s][0]) $s = $l;
                if ($r < $heapSize && $heap[$r][0] < $heap[$s][0]) $s = $r;
                if ($s === $i) break;
                $t = $heap[$i]; $heap[$i] = $heap[$s]; $heap[$s] = $t;
                $i = $s;
            }
            return $top;
        };

        $min0 = $computeReach($startPlayer, $startMask);
        $visited = [$startMask . '|' . $min0 => 0];
        $heapPush($h0, $startMask, $startPlayer, 0, '', -1);
        $nodes = 0; $expansions = 0;

        while ($heapSize > 0) {
            if (($expansions & 511) === 0 && (hrtime(true) - $T0) > $tlNs) {
                $ms = (int)((hrtime(true) - $T0) / 1000000);
                return [
                    'ok' => false, 'nodes' => $nodes, 'expansions' => $expansions,
                    'ms' => $ms, 'dir' => 'bf', 'visited' => count($visited),
                ];
            }
            $cur = $heapPop();
            $expansions++;
            $mask = $cur[1]; $player = $cur[2]; $g = $cur[3]; $path = $cur[4]; $lastBox = $cur[5];

            if ($isWin($mask)) {
                $ms = (int)((hrtime(true) - $T0) / 1000000);
                return [
                    'ok' => true, 'path' => $path, 'pushes' => $g,
                    'nodes' => $nodes, 'expansions' => $expansions,
                    'ms' => $ms, 'dir' => 'bf', 'visited' => count($visited),
                ];
            }

            $moves = $genPushes($player, $mask, $lastBox);
            foreach ($moves as $m) {
                $nodes++;
                $nm = $m[0]; $npl = $m[1]; $ch = $m[2]; $nh = $m[3]; $pc = $m[4]; $fb = $m[5];
                $minR = $computeReach($npl, $nm);
                $k = $nm . '|' . $minR;
                $ng = $g + $pc;
                if (isset($visited[$k]) && $visited[$k] <= $ng) continue;
                $visited[$k] = $ng;
                $heapPush($nh, $nm, $npl, $ng, $path . $ch, $fb);
            }
        }
        $ms = (int)((hrtime(true) - $T0) / 1000000);
        return [
            'ok' => false, 'nodes' => $nodes, 'expansions' => $expansions,
            'ms' => $ms, 'dir' => 'bf', 'visited' => count($visited),
        ];
    };

    $solve = function (int $tl, string $mode) use ($solveDFS, $solveBF): array {
        if ($mode === 'bf' || $mode === 'greedy' || $mode === 'fwd') return $solveBF($tl);
        if ($mode === 'auto') {
            $T0 = hrtime(true);
            $r = $solveDFS((int)($tl * 0.5));
            if (!empty($r['ok'])) {
                $r['ms'] = (int)((hrtime(true) - $T0) / 1000000);
                return $r;
            }
            $remain = $tl - (int)((hrtime(true) - $T0) / 1000000);
            if ($remain < 50) return $r;
            $r2 = $solveBF($remain);
            if (!empty($r2['ok'])) {
                $r2['ms'] = (int)((hrtime(true) - $T0) / 1000000);
                $r2['nodes'] += $r['nodes'];
                return $r2;
            }
            $r2['ms'] = (int)((hrtime(true) - $T0) / 1000000);
            $r2['nodes'] += $r['nodes'];
            return $r2;
        }
        return $solveDFS($tl);
    };

    return ['solve' => $solve, 'N' => $N, 'NB' => $NB];
}
