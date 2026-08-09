## 推箱子核心（Godot 4 GDScript 教学）
extends RefCounted
class_name SokobanGame

var walls: Dictionary = {}
var goals: Dictionary = {}
var boxes: Dictionary = {}
var player: Vector2i = Vector2i.ZERO
var moves: int = 0
var won: bool = false
var width: int = 0
var height: int = 0
var hist: Array = []

static func key(x: int, y: int) -> String:
	return "%d,%d" % [x, y]

func from_rows(rows: PackedStringArray) -> void:
	walls.clear()
	goals.clear()
	boxes.clear()
	hist.clear()
	moves = 0
	won = false
	player = Vector2i.ZERO
	width = 0
	height = rows.size()
	for y in range(rows.size()):
		var row := rows[y]
		if row.length() > width:
			width = row.length()
		for x in range(row.length()):
			var ch := row[x]
			var k := key(x, y)
			match ch:
				"#":
					walls[k] = true
				".":
					goals[k] = true
				"$":
					boxes[k] = true
				"*":
					boxes[k] = true
					goals[k] = true
				"@":
					player = Vector2i(x, y)
				"+":
					player = Vector2i(x, y)
					goals[k] = true

func try_move(dx: int, dy: int) -> bool:
	if won:
		return false
	var n := player + Vector2i(dx, dy)
	var nk := key(n.x, n.y)
	if walls.has(nk):
		return false
	if boxes.has(nk):
		var b := n + Vector2i(dx, dy)
		var bk := key(b.x, b.y)
		if walls.has(bk) or boxes.has(bk):
			return false
		hist.append({"player": player, "box_from": nk, "box_to": bk})
		boxes.erase(nk)
		boxes[bk] = true
		player = n
		moves += 1
		_check_win()
		return true
	hist.append({"player": player, "box_from": null, "box_to": null})
	player = n
	return true

func undo() -> void:
	if won or hist.is_empty():
		return
	var entry = null
	while not hist.is_empty():
		entry = hist.pop_back()
		if entry["box_from"] != null:
			break
		player = entry["player"]
	if entry == null or entry["box_from"] == null:
		return
	player = entry["player"]
	boxes.erase(entry["box_to"])
	boxes[entry["box_from"]] = true
	if moves > 0:
		moves -= 1
	won = false

func _check_win() -> void:
	for b in boxes.keys():
		if not goals.has(b):
			won = false
			return
	won = true
