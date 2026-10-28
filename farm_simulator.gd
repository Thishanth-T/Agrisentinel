extends Node2D

var grid_cols: int = 3
var grid_rows: int = 3
var cell_size: Vector2 = Vector2(160, 140)
var grid_origin: Vector2 = Vector2(50, 50)
var plots: Array = []
var http_node: HTTPRequest
var sync_timer: Timer

func _ready() -> void:
	http_node = HTTPRequest.new()
	add_child(http_node)
	http_node.request_completed.connect(_on_request_completed)
	for r in range(grid_rows):
		for c in range(grid_cols):
			var idx: int = r * grid_cols + c + 1
			plots.append({
				"plot_id": "plot_" + str(idx),
				"grid_x": c,
				"grid_y": r,
				"soil_moisture": 30.0,
				"temperature": 27.0,
				"status": "NORMAL"
			})
	sync_timer = Timer.new()
	sync_timer.wait_time = 2.0
	sync_timer.autostart = true
	add_child(sync_timer)
	sync_timer.timeout.connect(_on_timer_timeout)
	queue_redraw()

func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var pos: Vector2 = event.position - grid_origin
		if pos.x >= 0 and pos.y >= 0:
			var cx: int = int(pos.x / cell_size.x)
			var cy: int = int(pos.y / cell_size.y)
			if cx < grid_cols and cy < grid_rows:
				var idx: int = cy * grid_cols + cx
				trigger_plot_drought(idx)

func trigger_plot_drought(index: int) -> void:
	if index >= 0 and index < plots.size():
		plots[index]["soil_moisture"] = 11.5
		plots[index]["temperature"] = 41.0
		plots[index]["status"] = "PARAMETRIC_BREACH"
		queue_redraw()
		send_plot_telemetry(plots[index])

func send_plot_telemetry(plot: Dictionary) -> void:
	var headers: PackedStringArray = ["Content-Type: application/json"]
	http_node.request("http://127.0.0.1:8000/api/manual-trigger", headers, HTTPClient.METHOD_POST, JSON.stringify({
		"plot_id": plot["plot_id"],
		"soil_moisture": float(plot["soil_moisture"]),
		"temperature": float(plot["temperature"]),
		"rainfall_mm": 0.0
	}))

func _on_timer_timeout() -> void:
	var headers: PackedStringArray = ["Accept: application/json"]
	http_node.request("http://127.0.0.1:8000/api/grid", headers, HTTPClient.METHOD_GET)

func _on_request_completed(_result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	if response_code == 200:
		var json: Variant = JSON.parse_string(body.get_string_from_utf8())
		if typeof(json) == TYPE_DICTIONARY and json.has("grid"):
			var server_grid: Array = json["grid"]
			for item in server_grid:
				for p in plots:
					if p["plot_id"] == item.get("plot_id"):
						p["soil_moisture"] = item.get("soil_moisture", p["soil_moisture"])
						p["temperature"] = item.get("temperature", p["temperature"])
						p["status"] = item.get("status", p["status"])
			queue_redraw()

func _draw() -> void:
	draw_string(ThemeDB.fallback_font, Vector2(50, 35), "AgriSentinel Farm Sensor Grid (Click Tile to Trigger Drought Breach)", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.WHITE)
	for p in plots:
		var r: Rect2 = Rect2(grid_origin.x + p["grid_x"] * cell_size.x, grid_origin.y + p["grid_y"] * cell_size.y, cell_size.x - 10, cell_size.y - 10)
		var fill_color: Color = Color(0.15, 0.6, 0.25)
		if p["status"] == "PARAMETRIC_BREACH":
			fill_color = Color(0.85, 0.15, 0.15)
		elif p["soil_moisture"] < 20.0:
			fill_color = Color(0.85, 0.65, 0.15)
		draw_rect(r, fill_color, true)
		draw_rect(r, Color.WHITE, false, 2.0)
		var text_pos: Vector2 = r.position + Vector2(10, 25)
		draw_string(ThemeDB.fallback_font, text_pos, str(p["plot_id"]).to_upper(), HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color.WHITE)
		draw_string(ThemeDB.fallback_font, text_pos + Vector2(0, 25), "Moisture: " + str(snappedf(p["soil_moisture"], 0.1)) + "%", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color.WHITE)
		draw_string(ThemeDB.fallback_font, text_pos + Vector2(0, 45), "Temp: " + str(snappedf(p["temperature"], 0.1)) + "C", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color.WHITE)
		draw_string(ThemeDB.fallback_font, text_pos + Vector2(0, 65), "State: " + str(p["status"]), HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color.YELLOW if p["status"] == "PARAMETRIC_BREACH" else Color.WHITE)
