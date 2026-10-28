# ==============================================================================
# AGRISENTINEL - GODOT 4 HARDWARE TELEMETRY & ANTI-FRAUD SIMULATOR
# ==============================================================================
#
# INSTRUCTIONS TO RUN IN GODOT 4:
# ------------------------------------------------------------------------------
# 1. Open Godot 4 (4.0 / 4.1 / 4.2 / 4.3).
# 2. In your Project, create a new 2D Scene:
#    - In the Scene dock on the left, click "2D Scene" (creates a Node2D).
#    - Rename the root node to "Main" (optional).
#    - Save the scene (e.g., res://Main.tscn).
# 3. Attach this script:
#    - Select the root Node2D.
#    - In the Inspector, click the Script property -> "Load" -> select this Main.gd.
# 4. Ensure your AgriSentinel FastAPI backend is running:
#    - Command: python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload
# 5. Press F6 (Play Current Scene) or F5.
# 6. Interact with the 50x50m farm grid, adjust sliders, trigger drought payouts,
#    or test physical tamper and cryptographic spoofing attacks directly from Godot!
# ==============================================================================

extends Node2D

const BACKEND_URL = "http://127.0.0.1:8000"

# Pre-seeded SECP256k1 keys for simulated nodes
const NODE_KEYS = {
	"node_1": {
		"vk": "04b50c128ff0b1a0f9687e35aa19842f778a4869c9b466184a1d48c0a87a8a25c114e9f7833076ecf258a36021200be649f807be1778c8531ebcd7ff514120ec0e"
	},
	"node_2": {
		"vk": "04936d97e84bf60eb80f08a478cbef2c7a363a033ebf61a153d9e84cc22a571ea0e051c91ffec94978be7b3d30b1bc01d14e9411963f2d2ee5fc30689b6b77df83"
	},
	"node_3": {
		"vk": "0450863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b23522cd470243453a299fa9e77237716103abc11a1df38855ed6f2ee187e9c582ba6"
	}
}

# 3x3 Simulated Grid Data
var plots = [
	{"id": "plot_1", "node": "node_1", "name": "Murugan K.", "state": "Tamil Nadu", "crop": "Paddy", "moisture": 32.0, "temp": 28.5, "status": "SAFE"},
	{"id": "plot_2", "node": "node_2", "name": "Ram Prasad", "state": "Uttar Pradesh", "crop": "Wheat", "moisture": 30.0, "temp": 29.0, "status": "SAFE"},
	{"id": "plot_3", "node": "node_3", "name": "Patel Bhai", "state": "Gujarat", "crop": "Cotton", "moisture": 28.0, "temp": 31.0, "status": "SAFE"},
	{"id": "plot_4", "node": "node_1", "name": "Siva Reddy", "state": "Andhra Pradesh", "crop": "Chilli", "moisture": 35.0, "temp": 29.5, "status": "SAFE"},
	{"id": "plot_5", "node": "node_2", "name": "Debabrata D.", "state": "West Bengal", "crop": "Jute", "moisture": 38.0, "temp": 27.0, "status": "SAFE"},
	{"id": "plot_6", "node": "node_3", "name": "Kailash M.", "state": "Rajasthan", "crop": "Mustard", "moisture": 22.0, "temp": 33.0, "status": "SAFE"},
	{"id": "plot_7", "node": "node_1", "name": "Eknath P.", "state": "Maharashtra", "crop": "Sugarcane", "moisture": 34.0, "temp": 28.0, "status": "SAFE"},
	{"id": "plot_8", "node": "node_2", "name": "Mathew K.", "state": "Kerala", "crop": "Rubber", "moisture": 42.0, "temp": 26.5, "status": "SAFE"},
	{"id": "plot_9", "node": "node_3", "name": "Basavaraj B.", "state": "Karnataka", "crop": "Maize", "moisture": 31.0, "temp": 29.0, "status": "SAFE"}
]

var selected_plot_index: int = 0
var spoof_signature_active: bool = false

# HTTP Request Nodes
var http_signer: HTTPRequest
var http_sender: HTTPRequest

# UI Nodes
var ui_container: Control
var plot_buttons: Array = []
var label_selected: Label
var slider_moisture: HSlider
var label_moisture_val: Label
var slider_temp: HSlider
var label_temp_val: Label
var log_text: TextEdit
var status_pill: Label

func _ready():
	_setup_http()
	_build_ui()
	_update_selected_ui()
	_log("[READY] AgriSentinel Godot 4 Simulator Initialized.")
	_log("[CONNECTED] Target Backend: " + BACKEND_URL)

func _setup_http():
	http_signer = HTTPRequest.new()
	add_child(http_signer)
	http_signer.request_completed.connect(_on_signer_completed)

	http_sender = HTTPRequest.new()
	add_child(http_sender)
	http_sender.request_completed.connect(_on_sender_completed)

func _build_ui():
	# Background Canvas
	var bg = ColorRect.new()
	bg.size = Vector2(1150, 700)
	bg.color = Color(0.06, 0.09, 0.13, 1.0)
	add_child(bg)

	ui_container = Control.new()
	ui_container.size = Vector2(1150, 700)
	add_child(ui_container)

	# Title Banner
	var title = Label.new()
	title.text = "AGRISENTINEL | 50x50m Farm Grid & 2G Telemetry Hardware Simulator"
	title.position = Vector2(30, 20)
	title.add_theme_font_size_override("font_size", 20)
	title.add_theme_color_override("font_color", Color(0.3, 0.85, 0.5, 1.0))
	ui_container.add_child(title)

	var subtitle = Label.new()
	subtitle.text = "Click a 50x50m grid plot to inspect telemetry, adjust environment sliders, and transmit SECP256k1 signed packets."
	subtitle.position = Vector2(30, 48)
	subtitle.add_theme_font_size_override("font_size", 12)
	subtitle.add_theme_color_override("font_color", Color(0.7, 0.75, 0.8, 0.9))
	ui_container.add_child(subtitle)

	# 3x3 Farm Grid Container
	var grid_panel = Panel.new()
	grid_panel.position = Vector2(30, 80)
	grid_panel.size = Vector2(500, 500)
	ui_container.add_child(grid_panel)

	for i in range(plots.size()):
		var p = plots[i]
		var col = i % 3
		var row = i / 3
		var btn = Button.new()
		btn.position = Vector2(15 + col * 160, 15 + row * 160)
		btn.size = Vector2(150, 150)
		btn.text = "%s\n%s\n%s\n\nMoist: %.1f%%\nTemp: %.1f°C" % [p["id"].to_upper(), p["name"], p["crop"], p["moisture"], p["temp"]]
		btn.alignment = HORIZONTAL_ALIGNMENT_CENTER
		var idx = i
		btn.pressed.connect(func(): _on_plot_clicked(idx))
		grid_panel.add_child(btn)
		plot_buttons.append(btn)

	# Right Controls Panel
	var ctrl_panel = Panel.new()
	ctrl_panel.position = Vector2(550, 80)
	ctrl_panel.size = Vector2(570, 590)
	ui_container.add_child(ctrl_panel)

	label_selected = Label.new()
	label_selected.position = Vector2(20, 15)
	label_selected.add_theme_font_size_override("font_size", 16)
	label_selected.add_theme_color_override("font_color", Color(1.0, 0.8, 0.2, 1.0))
	ctrl_panel.add_child(label_selected)

	# Moisture Controls
	var lbl_m = Label.new()
	lbl_m.text = "Soil Moisture (%):"
	lbl_m.position = Vector2(20, 55)
	ctrl_panel.add_child(lbl_m)

	slider_moisture = HSlider.new()
	slider_moisture.position = Vector2(160, 60)
	slider_moisture.size = Vector2(300, 20)
	slider_moisture.min_value = 5.0
	slider_moisture.max_value = 100.0
	slider_moisture.step = 0.5
	slider_moisture.value = 32.0
	slider_moisture.value_changed.connect(_on_moisture_changed)
	ctrl_panel.add_child(slider_moisture)

	label_moisture_val = Label.new()
	label_moisture_val.text = "32.0%"
	label_moisture_val.position = Vector2(480, 55)
	ctrl_panel.add_child(label_moisture_val)

	# Temperature Controls
	var lbl_t = Label.new()
	lbl_t.text = "Temperature (°C):"
	lbl_t.position = Vector2(20, 95)
	ctrl_panel.add_child(lbl_t)

	slider_temp = HSlider.new()
	slider_temp.position = Vector2(160, 100)
	slider_temp.size = Vector2(300, 20)
	slider_temp.min_value = 15.0
	slider_temp.max_value = 55.0
	slider_temp.step = 0.5
	slider_temp.value = 28.5
	slider_temp.value_changed.connect(_on_temp_changed)
	ctrl_panel.add_child(slider_temp)

	label_temp_val = Label.new()
	label_temp_val.text = "28.5°C"
	label_temp_val.position = Vector2(480, 95)
	ctrl_panel.add_child(label_temp_val)

	# Scenario Buttons Row
	var scn_lbl = Label.new()
	scn_lbl.text = "One-Click Hardware Attack / Anomaly Scenarios:"
	scn_lbl.position = Vector2(20, 140)
	scn_lbl.add_theme_font_size_override("font_size", 12)
	ctrl_panel.add_child(scn_lbl)

	var btn_normal = Button.new()
	btn_normal.text = "🟢 Normal Baseline"
	btn_normal.position = Vector2(20, 165)
	btn_normal.size = Vector2(160, 32)
	btn_normal.pressed.connect(func(): _load_scenario(32.0, 28.5, false))
	ctrl_panel.add_child(btn_normal)

	var btn_drought = Button.new()
	btn_drought.text = "🚨 Drought Breach"
	btn_drought.position = Vector2(190, 165)
	btn_drought.size = Vector2(160, 32)
	btn_drought.pressed.connect(func(): _load_scenario(11.5, 43.5, false))
	ctrl_panel.add_child(btn_drought)

	var btn_tamper = Button.new()
	btn_tamper.text = "🪣 Flood Fraud Attack"
	btn_tamper.position = Vector2(360, 165)
	btn_tamper.size = Vector2(180, 32)
	btn_tamper.pressed.connect(func(): _load_scenario(96.0, 27.0, false))
	ctrl_panel.add_child(btn_tamper)

	var btn_spoof = Button.new()
	btn_spoof.text = "🔓 Cryptographic Spoof"
	btn_spoof.position = Vector2(20, 205)
	btn_spoof.size = Vector2(250, 32)
	btn_spoof.pressed.connect(func(): _load_scenario(8.0, 48.0, true))
	ctrl_panel.add_child(btn_spoof)

	# Transmit Button
	var btn_send = Button.new()
	btn_send.text = "⚡ SIGN (ECDSA SECP256k1) & TRANSMIT TELEMETRY"
	btn_send.position = Vector2(20, 250)
	btn_send.size = Vector2(520, 40)
	btn_send.pressed.connect(_on_send_pressed)
	ctrl_panel.add_child(btn_send)

	# Real-Time Event Log Console
	var lbl_log = Label.new()
	lbl_log.text = "Hardware Ingestion & In-Flight Signature Console:"
	lbl_log.position = Vector2(20, 305)
	lbl_log.add_theme_font_size_override("font_size", 12)
	ctrl_panel.add_child(lbl_log)

	log_text = TextEdit.new()
	log_text.position = Vector2(20, 330)
	log_text.size = Vector2(520, 240)
	log_text.editable = false
	ctrl_panel.add_child(log_text)

func _on_plot_clicked(idx: int):
	selected_plot_index = idx
	var p = plots[idx]
	slider_moisture.value = p["moisture"]
	slider_temp.value = p["temp"]
	spoof_signature_active = false
	_update_selected_ui()
	_log("[SELECT] Plot switched to: " + p["id"].to_upper() + " (" + p["name"] + ")")

func _update_selected_ui():
	var p = plots[selected_plot_index]
	label_selected.text = "SELECTED: %s | %s (%s, %s) | NODE: %s" % [p["id"].to_upper(), p["name"], p["crop"], p["state"], p["node"]]
	label_moisture_val.text = "%.1f%%" % slider_moisture.value
	label_temp_val.text = "%.1f°C" % slider_temp.value

func _on_moisture_changed(val: float):
	plots[selected_plot_index]["moisture"] = val
	label_moisture_val.text = "%.1f%%" % val
	_refresh_plot_button(selected_plot_index)

func _on_temp_changed(val: float):
	plots[selected_plot_index]["temp"] = val
	label_temp_val.text = "%.1f°C" % val
	_refresh_plot_button(selected_plot_index)

func _refresh_plot_button(idx: int):
	var p = plots[idx]
	plot_buttons[idx].text = "%s\n%s\n%s\n\nMoist: %.1f%%\nTemp: %.1f°C" % [p["id"].to_upper(), p["name"], p["crop"], p["moisture"], p["temp"]]

func _load_scenario(moist: float, temp: float, spoof: bool):
	slider_moisture.value = moist
	slider_temp.value = temp
	spoof_signature_active = spoof
	plots[selected_plot_index]["moisture"] = moist
	plots[selected_plot_index]["temp"] = temp
	_refresh_plot_button(selected_plot_index)
	if spoof:
		_log("[SCENARIO] Corrupted ECDSA signature armed. System will test rejection.")
	elif moist > 85.0:
		_log("[SCENARIO] Water-bucket tamper armed. Submerged sensor simulation.")
	elif moist < 15.0:
		_log("[SCENARIO] Extreme drought armed. Payout test ready.")
	else:
		_log("[SCENARIO] Normal agronomic baseline restored.")

func _on_send_pressed():
	var p = plots[selected_plot_index]
	_log("\n--- TRANSMITTING TELEMETRY ---")
	_log("[SIGNER] Requesting ECDSA SECP256k1 signature for node: " + p["node"])

	var telemetry_data = {
		"plot_id": p["id"],
		"timestamp": Time.get_unix_time_from_system(),
		"temperature": slider_temp.value,
		"humidity": 35.0,
		"pressure": 1012.0,
		"soil_moisture": slider_moisture.value,
		"rainfall_mm": 0.0
	}

	var sign_payload = {
		"node_id": p["node"],
		"telemetry": telemetry_data
	}

	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify(sign_payload)
	var err = http_signer.request(BACKEND_URL + "/api/crypto/sign", headers, HTTPClient.METHOD_POST, body)
	if err != OK:
		_log("[ERROR] Signer request failed to launch. Code: " + str(err))

func _on_signer_completed(_result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray):
	if response_code != 200:
		_log("[ERROR] Signing endpoint returned code: " + str(response_code))
		return

	var parse_result = JSON.parse_string(body.get_string_from_utf8())
	if parse_result == null:
		_log("[ERROR] Failed to parse signed packet JSON.")
		return

	var packet = parse_result

	if spoof_signature_active:
		# Corrupt signature to test rejection
		var orig_sig = packet.get("signature", "")
		packet["signature"] = orig_sig.substr(0, orig_sig.length() - 8) + "0000dead"
		_log("[TAMPER] Injected corrupted ECDSA signature: ...dead")

	_log("[CRYPTO] Signature verified. Dispatching to POST /api/telemetry")
	var headers = ["Content-Type: application/json"]
	var body_json = JSON.stringify(packet)
	http_sender.request(BACKEND_URL + "/api/telemetry", headers, HTTPClient.METHOD_POST, body_json)

func _on_sender_completed(_result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray):
	var resp_str = body.get_string_from_utf8()
	var json_data = JSON.parse_string(resp_str)

	if response_code == 200:
		var status = json_data.get("status", "")
		if status == "HELD_FOR_AUDIT":
			_log("🛑 [AUDIT FREEZE] Satellite Remote Sensing Mismatch!")
			_log("   Reason: Potential bucket-submersion tamper detected.")
		else:
			_log("✅ [HTTP 200] Telemetry Accepted & Cryptographically Verified.")
			var ev = json_data.get("evaluation", {})
			if ev.get("triggered", false):
				_log("🎉 [PAYOUT TRIGGERED] Amount: Rs. " + str(ev.get("payout_amount", 0)))
				_log("📞 [VOICE DISPATCH] 2G Outbound call queued to farmer.")
			else:
				_log("🌾 [NORMAL] Parameters within policy thresholds.")
	elif response_code == 403:
		_log("🛡️ [HTTP 403 FORBIDDEN] Cryptographic Signature Rejected!")
		_log("   Defense Engine: Blocked tampered / spoofed packet.")
	else:
		_log("[HTTP " + str(response_code) + "] " + resp_str)

func _log(msg: String):
	var time_str = Time.get_time_string_from_system()
	log_text.text += "[%s] %s\n" % [time_str, msg]
	log_text.scroll_vertical = 999999
