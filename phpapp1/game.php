<?php
/**
 * 推箱子核心逻辑（PHP 教学）。
 */

class GameState
{
    /** @var array<string,bool> */
    public $walls = [];
    /** @var array<string,bool> */
    public $goals = [];
    /** @var array<string,bool> */
    public $boxes = [];
    /** @var array{x:int,y:int} */
    public $player = ['x' => 0, 'y' => 0];
    public $moves = 0;
    public $won = false;
    public $width = 0;
    public $height = 0;
    public $levelIndex = 0;
    /** @var list<array{player:array{x:int,y:int},boxFrom:?string,boxTo:?string}> */
    private $hist = [];

    public static function fromRows(array $rows, int $index = 0): self
    {
        $s = new self();
        $s->levelIndex = $index;
        $maxX = 0;
        $maxY = 0;
        foreach ($rows as $y => $row) {
            $maxY = $y;
            $len = strlen($row);
            for ($x = 0; $x < $len; $x++) {
                $maxX = max($maxX, $x);
                $ch = $row[$x];
                $k = $x . ',' . $y;
                switch ($ch) {
                    case '#':
                        $s->walls[$k] = true;
                        break;
                    case '.':
                        $s->goals[$k] = true;
                        break;
                    case '$':
                        $s->boxes[$k] = true;
                        break;
                    case '*':
                        $s->boxes[$k] = true;
                        $s->goals[$k] = true;
                        break;
                    case '@':
                        $s->player = ['x' => $x, 'y' => $y];
                        break;
                    case '+':
                        $s->player = ['x' => $x, 'y' => $y];
                        $s->goals[$k] = true;
                        break;
                }
            }
        }
        $s->width = $maxX + 1;
        $s->height = $maxY + 1;
        return $s;
    }

    public function tryMove(int $dx, int $dy): bool
    {
        if ($this->won) {
            return false;
        }
        $nx = $this->player['x'] + $dx;
        $ny = $this->player['y'] + $dy;
        $nk = $nx . ',' . $ny;
        if (isset($this->walls[$nk])) {
            return false;
        }
        if (isset($this->boxes[$nk])) {
            $bx = $nx + $dx;
            $by = $ny + $dy;
            $bk = $bx . ',' . $by;
            if (isset($this->walls[$bk]) || isset($this->boxes[$bk])) {
                return false;
            }
            $this->hist[] = [
                'player' => $this->player,
                'boxFrom' => $nk,
                'boxTo' => $bk,
            ];
            unset($this->boxes[$nk]);
            $this->boxes[$bk] = true;
            $this->player = ['x' => $nx, 'y' => $ny];
            $this->moves++;
            $this->checkWin();
            return true;
        }
        $this->hist[] = [
            'player' => $this->player,
            'boxFrom' => null,
            'boxTo' => null,
        ];
        $this->player = ['x' => $nx, 'y' => $ny];
        return true;
    }

    public function undo(): bool
    {
        if ($this->won || count($this->hist) === 0) {
            return false;
        }
        $entry = null;
        while (count($this->hist) > 0) {
            $entry = array_pop($this->hist);
            if ($entry['boxFrom'] !== null) {
                break;
            }
            $this->player = $entry['player'];
        }
        if ($entry === null || $entry['boxFrom'] === null) {
            return true;
        }
        $this->player = $entry['player'];
        unset($this->boxes[$entry['boxTo']]);
        $this->boxes[$entry['boxFrom']] = true;
        if ($this->moves > 0) {
            $this->moves--;
        }
        $this->won = false;
        return true;
    }

    private function checkWin(): void
    {
        foreach ($this->boxes as $b => $_) {
            if (!isset($this->goals[$b])) {
                $this->won = false;
                return;
            }
        }
        $this->won = true;
    }

    public function renderAscii(): string
    {
        $out = '';
        for ($y = 0; $y < $this->height; $y++) {
            for ($x = 0; $x < $this->width; $x++) {
                $k = $x . ',' . $y;
                if ($this->player['x'] === $x && $this->player['y'] === $y) {
                    $out .= isset($this->goals[$k]) ? '+' : '@';
                } elseif (isset($this->boxes[$k])) {
                    $out .= isset($this->goals[$k]) ? '*' : '$';
                } elseif (isset($this->walls[$k])) {
                    $out .= '#';
                } elseif (isset($this->goals[$k])) {
                    $out .= '.';
                } else {
                    $out .= ' ';
                }
            }
            $out .= "\n";
        }
        return $out;
    }
}
