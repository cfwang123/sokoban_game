const std = @import("std");
const game = @import("game.zig");

const level = [_][]const u8{
    "###",
    "#@#",
    "#$#",
    "#.#",
    "###",
};

pub fn main() !void {
    var g: game.State = .{};
    g.load(&level);
    const stdout = std.io.getStdOut().writer();
    const stdin = std.io.getStdIn().reader();
    try stdout.writeAll("zig sokoban — wasd, z undo, r reset, q quit\n");
    var buf: [16]u8 = undefined;
    while (true) {
        try stdout.writeAll("\n");
        g.printAscii();
        try stdout.print("moves={d}{s}\n> ", .{ g.moves, if (g.won) " WIN" else "" });
        const n = try stdin.readUntilDelimiterOrEof(&buf, '\n');
        if (n == null) break;
        const line = std.mem.trim(u8, n.?, " \r\n");
        if (line.len == 0) continue;
        switch (line[0]) {
            'w', 'W' => _ = g.tryMove(0, -1),
            's', 'S' => _ = g.tryMove(0, 1),
            'a', 'A' => _ = g.tryMove(-1, 0),
            'd', 'D' => _ = g.tryMove(1, 0),
            'z', 'Z' => g.undo(),
            'r', 'R' => g.load(&level),
            'q', 'Q' => break,
            else => {},
        }
    }
}
