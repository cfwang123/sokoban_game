## godotapp1 — Godot 4 推箱子桌面 demo
extends Node2D

const CELL := 40.0
const PAD := 20.0

var game: SokobanGame
var level: PackedStringArray = PackedStringArray([
	"#######",
	"#. . .#",
	"# $$$ #",
	"#.$@$.#",
	"# $$$ #",
	"#. . .#",
	"#######",
])

func _ready() -> void:
	game = SokobanGame.new()
	game.from_rows(level)
	queue_redraw()

func _draw() -> void:
	draw_rect(Rect2(0, 0, 480, 420), Color("1a1a2e"))
	for y in range(game.height):
		for x in range(game.width):
			var k := SokobanGame.key(x, y)
			var r := Rect2(PAD + x * CELL, PAD + y * CELL, CELL, CELL)
			if game.walls.has(k):
				draw_rect(r, Color("4a4a6a"))
			else:
				draw_rect(r, Color("3a3a55"))
				draw_rect(r, Color("444466"), false, 1.0)
			if game.goals.has(k):
				draw_circle(r.get_center(), 6.0, Color("e94560"))
			if game.boxes.has(k):
				var on := game.goals.has(k)
				draw_rect(r.grow(-4), Color("2ecc71") if on else Color("f39c12"))
			if game.player == Vector2i(x, y):
				draw_circle(r.get_center(), CELL * 0.35, Color("3498db"))
	var flag := " WIN" if game.won else ""
	draw_string(ThemeDB.fallback_font, Vector2(8, PAD * 2 + game.height * CELL + 8),
		"moves=%d%s  WASD Z R" % [game.moves, flag], HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.WHITE)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_W, KEY_UP:
				game.try_move(0, -1)
			KEY_S, KEY_DOWN:
				game.try_move(0, 1)
			KEY_A, KEY_LEFT:
				game.try_move(-1, 0)
			KEY_D, KEY_RIGHT:
				game.try_move(1, 0)
			KEY_Z:
				game.undo()
			KEY_R:
				game.from_rows(level)
			_:
				return
		queue_redraw()
