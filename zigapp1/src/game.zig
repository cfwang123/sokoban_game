//! 推箱子核心（Zig 教学）：固定容量，适合嵌入思维。
const std = @import("std");

pub const MAX_CELLS: usize = 512;
pub const MAX_HIST: usize = 256;

pub const State = struct {
    w: i32 = 0,
    h: i32 = 0,
    px: i32 = 0,
    py: i32 = 0,
    moves: i32 = 0,
    won: bool = false,
    walls: [MAX_CELLS]bool = [_]bool{false} ** MAX_CELLS,
    goals: [MAX_CELLS]bool = [_]bool{false} ** MAX_CELLS,
    boxes: [MAX_CELLS]bool = [_]bool{false} ** MAX_CELLS,
    hist: [MAX_HIST]i32 = undefined,
    hist_n: usize = 0,

    fn idx(self: State, x: i32, y: i32) usize {
        return @intCast(y * self.w + x);
    }

    fn inb(self: State, x: i32, y: i32) bool {
        return x >= 0 and y >= 0 and x < self.w and y < self.h;
    }

    pub fn load(self: *State, rows: []const []const u8) void {
        self.* = .{};
        var max_w: i32 = 0;
        for (rows) |r| {
            if (@as(i32, @intCast(r.len)) > max_w) max_w = @intCast(r.len);
        }
        self.w = max_w;
        self.h = @intCast(rows.len);
        for (rows, 0..) |row, y| {
            for (row, 0..) |ch, x| {
                const i = self.idx(@intCast(x), @intCast(y));
                switch (ch) {
                    '#' => self.walls[i] = true,
                    '.' => self.goals[i] = true,
                    '$' => self.boxes[i] = true,
                    '*' => {
                        self.boxes[i] = true;
                        self.goals[i] = true;
                    },
                    '@' => {
                        self.px = @intCast(x);
                        self.py = @intCast(y);
                    },
                    '+' => {
                        self.px = @intCast(x);
                        self.py = @intCast(y);
                        self.goals[i] = true;
                    },
                    else => {},
                }
            }
        }
    }

    fn push5(self: *State, a: i32, b: i32, c: i32, d: i32, e: i32) void {
        if (self.hist_n + 5 > MAX_HIST) return;
        self.hist[self.hist_n] = a;
        self.hist[self.hist_n + 1] = b;
        self.hist[self.hist_n + 2] = c;
        self.hist[self.hist_n + 3] = d;
        self.hist[self.hist_n + 4] = e;
        self.hist_n += 5;
    }

    pub fn tryMove(self: *State, dx: i32, dy: i32) bool {
        if (self.won) return false;
        const nx = self.px + dx;
        const ny = self.py + dy;
        if (!self.inb(nx, ny) or self.walls[self.idx(nx, ny)]) return false;
        const ni = self.idx(nx, ny);
        if (self.boxes[ni]) {
            const bx = nx + dx;
            const by = ny + dy;
            if (!self.inb(bx, by) or self.walls[self.idx(bx, by)] or self.boxes[self.idx(bx, by)])
                return false;
            const bi = self.idx(bx, by);
            self.push5(self.px, self.py, @intCast(ni), @intCast(bi), 1);
            self.boxes[ni] = false;
            self.boxes[bi] = true;
            self.px = nx;
            self.py = ny;
            self.moves += 1;
            self.checkWin();
            return true;
        }
        self.push5(self.px, self.py, -1, -1, 0);
        self.px = nx;
        self.py = ny;
        return true;
    }

    pub fn undo(self: *State) void {
        if (self.won or self.hist_n < 5) return;
        var is_push: i32 = 0;
        var from: i32 = -1;
        var to: i32 = -1;
        var px = self.px;
        var py = self.py;
        while (self.hist_n >= 5) {
            is_push = self.hist[self.hist_n - 1];
            to = self.hist[self.hist_n - 2];
            from = self.hist[self.hist_n - 3];
            py = self.hist[self.hist_n - 4];
            px = self.hist[self.hist_n - 5];
            self.hist_n -= 5;
            if (is_push == 1) break;
            self.px = px;
            self.py = py;
        }
        if (is_push != 1 or from < 0) return;
        self.px = px;
        self.py = py;
        self.boxes[@intCast(to)] = false;
        self.boxes[@intCast(from)] = true;
        if (self.moves > 0) self.moves -= 1;
        self.won = false;
    }

    fn checkWin(self: *State) void {
        const n: usize = @intCast(self.w * self.h);
        var i: usize = 0;
        while (i < n) : (i += 1) {
            if (self.boxes[i] and !self.goals[i]) {
                self.won = false;
                return;
            }
        }
        self.won = true;
    }

    pub fn printAscii(self: State) void {
        var y: i32 = 0;
        while (y < self.h) : (y += 1) {
            var x: i32 = 0;
            while (x < self.w) : (x += 1) {
                const i = self.idx(x, y);
                const ch: u8 = if (self.px == x and self.py == y)
                    if (self.goals[i]) @as(u8, '+') else @as(u8, '@')
                else if (self.boxes[i])
                    if (self.goals[i]) @as(u8, '*') else @as(u8, '$')
                else if (self.walls[i])
                    '#'
                else if (self.goals[i])
                    '.'
                else
                    ' ';
                std.io.getStdOut().writer().writeByte(ch) catch {};
            }
            std.io.getStdOut().writer().writeByte('\n') catch {};
        }
    }
};
