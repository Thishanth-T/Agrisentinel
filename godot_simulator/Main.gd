# ==============================================================================
# AGRISENTINEL - GODOT 4 HARDWARE TELEMETRY & ANTI-FRAUD SIMULATOR
# ==============================================================================
#
# INSTRUCTIONS TO RUN IN GODOT 4:
# ------------------------------------------------------------------------------
# 1. Open Godot 4.
# 2. Open project in d:/agri sentinels/godot_simulator (or root project).
# 3. Press F5 or F6 to run Main.tscn.
# 4. Interact with the 9 regional farm profiles across India.
# 5. Test valid telemetry, physical divergence holds, and cryptographic rejection.
# ==============================================================================

extends Node2D

const BACKEND_URL = "http://127.0.0.1:8000"

# 9 Authoritative Regional Farm Profiles matching the Python backend registry
var plots = [
	{"id": "plot_1", "node": "node_1", "name": "Murugan K.", "state": "Tamil Nadu", "crop": "Paddy", "moisture": 32.0, "temp": 28.5, "status": "SAFE"},
	{"id": "plot_2", "node": "node_2", "name": "Ram Prasad", "state": "Uttar Pradesh", "crop": "Wheat", "moisture": 30.0, "temp": 29.0, "status": "SAFE"},
	{"id": "plot_3", "node": "node_3", "name": "Patel Bhai", "state": "Gujarat", "crop": "Cotton", "moisture": 28.0, "temp": 31.0, "status": "SAFE"},
	{"id": "plot_4", "node": "node_4", "name": "Siva Reddy", "state": "Andhra Pradesh", "crop": "Chilli", "moisture": 35.0, "temp": 29.5, "status": "SAFE"},
	{"id": "plot_5", "node": "node_5", "name": "Debabrata D.", "state": "West Bengal", "crop": "Jute", "moisture": 38.0, "temp": 27.0, "status": "SAFE"},
	{"id": "plot_6", "node": "node_6", "name": "Kailash M.", "state": "Rajasthan", "crop": "Mustard", "moisture": 22.0, "temp": 33.0, "status": "SAFE"},
	{"id": "plot_7", "node": "node_7", "name": "Eknath P.", "state": "Maharashtra", "crop": "Sugarcane", "moisture": 34.0, "temp": 28.0, "status": "SAFE"},
	{"id": "plot_8", "node": "node_8", "name": "Mathew K.", "state": "Kerala", "crop": "Rubber", "moisture": 42.0, "temp": 26.5, "status": "SAFE"},
	{"id": "plot_9", "node": "node_9", "name": "Basavaraj B.", "state": "Karnataka", "crop": "Maize", "moisture": 31.0, "temp": 29.0, "status": "SAFE"}
]

var selected_plot_index: int = 0
var spoof_signature_active: bool = false

# HTTP Request Nodes
var http_signer: HTTPRequest
var http_sender: HTTPRequest
var sync_timer: Timer

# UI Elements
var plot_buttons: Array = []
var label_selected: Label
var slider_moisture: HSlider
var label_moisture_val: Label
var slider_temp: HSlider
var label_temp_val: Label
var slider_rain: HSlider
var label_rain_val: Label
var log_text: TextEdit

func _ready():
	_setup_http()
	_build_ui()
	_update_selected_ui()
	_log("[READY] AgriSentinel Godot 4 Hardware Telemetry Simulator Initialized.")
	_log("[CONNECTED] Target Ingestion Backend: " + BACKEND_URL)

func _setup_http():
	http_signer = HTTPRequest.new()
	add_child(http_signer)
	http_signer.request_completed.connect(_on_signer_completed)

	http_sender = HTTPRequest.new()
	add_child(http_sender)
	http_sender.request_completed.connect(_on_sender_completed)

	sync_timer = Timer.new()
	sync_timer.wait_time = 3.0
	sync_timer.autostart = true
	add_child(sync_timer)
	sync_timer.timeout.connect(_on_sync_timer)

func _build_ui():
	var bg = ColorRect.new()
	bg.size = Vector2(1150, 720)
	bg.color = Color(0.06, 0.09, 0.13, 1.0)
	add_child(bg)

	var title = Label.new()
	title.text = "AGRISENTINEL | 9 Regional Farm Profiles & Telemetry Hardware Simulator"
	title.position = Vector2(30, 16)
	title.add_theme_font_size_override("font_size", 18)
	title.add_theme_color_override("font_color", Color(0.3, 0.85, 0.5, 1.0))
	add_child(title)

	var subtitle = Label.new()
	subtitle.text = "Simulating 9 distinct regional micro-climate profiles across India. Click a farm card to adjust telemetry & transmit signed packets."
	subtitle.position = Vector2(30, 42)
	subtitle.add_theme_font_size_override("font_size", 12)
	subtitle.add_theme_color_override("font_color", Color(0.7, 0.75, 0.8, 1.0))
	add_child(subtitle)

	# 3x3 Grid of Farm Profile Buttons
	for i in range(plots.size()):
		var col = i % 3
		var row = int(i / 3)
		var btn = Button.new()
		btn.size = Vector2(170, 115)
		btn.position = Vector2(30 + col * 185, 80 + row * 125)
		btn.pressed.connect(_on_plot_clicked.bind(i))
		add_child(btn)
		plot_buttons.append(btn)
		_refresh_plot_button(i)

	# Right-hand Control Panel
	var ctrl_panel = Panel.new()
	ctrl_panel.position = Vector2(595, 80)
	ctrl_panel.size = Vector2(525, 600)
	add_child(ctrl_panel)

	label_selected = Label.new()
	label_selected.position = Vector2(15, 12)
	label_selected.add_theme_font_size_override("font_size", 13)
	label_selected.add_theme_color_override("font_color", Color(0.9, 0.8, 0.2, 1.0))
	ctrl_panel.add_child(label_selected)

	# Moisture Slider
	var l_moist = Label.new()
	l_moist.text = "Soil Moisture (%)"
	l_moist.position = Vector2(15, 45)
	ctrl_panel.add_child(l_moist)

	slider_moisture = HSlider.new()
	slider_moisture.position = Vector2(160, 45)
	slider_moisture.size = Vector2(260, 20)
	slider_moisture.min_value = 0.0
	slider_moisture.max_value = 100.0
	slider_moisture.value = 32.0
	slider_moisture.value_changed.connect(_on_moisture_changed)
	ctrl_panel.add_child(slider_moisture)

	label_moisture_val = Label.new()
	label_moisture_val.position = Vector2(435, 45)
	label_moisture_val.text = "32.0%"
	ctrl_panel.add_child(label_moisture_val)

	# Temperature Slider
	var l_temp = Label.new()
	l_temp.text = "Ambient Temp (°C)"
	l_temp.position = Vector2(15, 80)
	ctrl_panel.add_child(l_temp)

	slider_temp = HSlider.new()
	slider_temp.position = Vector2(160, 80)
	slider_temp.size = Vector2(260, 20)
	slider_temp.min_value = 10.0
	slider_temp.max_value = 55.0
	slider_temp.value = 28.5
	slider_temp.value_changed.connect(_on_temp_changed)
	ctrl_panel.add_child(slider_temp)

	label_temp_val = Label.new()
	label_temp_val.position = Vector2(435, 80)
	label_temp_val.text = "28.5°C"
	ctrl_panel.add_child(label_temp_val)

	# Rainfall Slider
	var l_rain = Label.new()
	l_rain.text = "Rainfall (mm)"
	l_rain.position = Vector2(15, 115)
	ctrl_panel.add_child(l_rain)

	slider_rain = HSlider.new()
	slider_rain.position = Vector2(160, 115)
	slider_rain.size = Vector2(260, 20)
	slider_rain.min_value = 0.0
	slider_rain.max_value = 150.0
	slider_rain.value = 0.0
	slider_rain.value_changed.connect(_on_rain_changed)
	ctrl_panel.add_child(slider_rain)

	label_rain_val = Label.new()
	label_rain_val.position = Vector2(435, 115)
	label_rain_val.text = "0.0 mm"
	ctrl_panel.add_child(label_rain_val)

	# Preset Test Scenario Buttons
	var btn_normal = Button.new()
	btn_normal.text = "1. Normal Baseline"
	btn_normal.position = Vector2(15, 155)
	btn_normal.size = Vector2(155, 30)
	btn_normal.pressed.connect(_load_scenario.bind(32.0, 28.5, 0.0, false))
	ctrl_panel.add_child(btn_normal)

	var btn_drought = Button.new()
	btn_drought.text = "2. Drought Breach"
	btn_drought.position = Vector2(180, 155)
	btn_drought.size = Vector2(155, 30)
	btn_drought.pressed.connect(_load_scenario.bind(12.0, 42.0, 0.0, false))
	ctrl_panel.add_child(btn_drought)

	var btn_deluge = Button.new()
	btn_deluge.text = "3. Rainfall Deluge"
	btn_deluge.position = Vector2(345, 155)
	btn_deluge.size = Vector2(160, 30)
	btn_deluge.pressed.connect(_load_scenario.bind(85.0, 24.0, 85.0, false))
	ctrl_panel.add_child(btn_deluge)

	var btn_tamper_crypto = Button.new()
	btn_tamper_crypto.text = "4. Spoof Crypto Sig"
	btn_tamper_crypto.position = Vector2(15, 195)
	btn_tamper_crypto.size = Vector2(155, 30)
	btn_tamper_crypto.pressed.connect(_load_scenario.bind(11.5, 41.0, 0.0, true))
	ctrl_panel.add_child(btn_tamper_crypto)

	var btn_tamper_bucket = Button.new()
	btn_tamper_bucket.text = "5. Bucket Fraud (Held)"
	btn_tamper_bucket.position = Vector2(180, 195)
	btn_tamper_bucket.size = Vector2(155, 30)
	btn_tamper_bucket.pressed.connect(_load_scenario.bind(92.0, 31.0, 0.0, false))
	ctrl_panel.add_child(btn_tamper_bucket)

	var btn_reset_demo = Button.new()
	btn_reset_demo.text = "6. Reset All State"
	btn_reset_demo.position = Vector2(345, 195)
	btn_reset_demo.size = Vector2(160, 30)
	btn_reset_demo.pressed.connect(_on_reset_pressed)
	ctrl_panel.add_child(btn_reset_demo)

	# Transmit Button
	var btn_send = Button.new()
	btn_send.text = "🚀 Transmit Signed Telemetry Packet to Backend"
	btn_send.position = Vector2(15, 235)
	btn_send.size = Vector2(490, 40)
	btn_send.pressed.connect(_on_send_pressed)
	ctrl_panel.add_child(btn_send)

	# Live Execution Console
	log_text = TextEdit.new()
	log_text.position = Vector2(15, 285)
	log_text.size = Vector2(490, 300)
	log_text.editable = false
	ctrl_panel.add_child(log_text)

func _on_plot_clicked(idx: int):
	selected_plot_index = idx
	var p = plots[idx]
	slider_moisture.value = p["moisture"]
	slider_temp.value = p["temp"]
	slider_rain.value = 0.0
	spoof_signature_active = false
	_update_selected_ui()
	_log("[SELECT] Switched to: " + p["id"].to_upper() + " (" + p["name"] + ", " + p["crop"] + ")")

func _update_selected_ui():
	var p = plots[selected_plot_index]
	label_selected.text = "PROFILE: %s | %s (%s, %s) | NODE: %s" % [p["id"].to_upper(), p["name"], p["crop"], p["state"], p["node"]]
	label_moisture_val.text = "%.1f%%" % slider_moisture.value
	label_temp_val.text = "%.1f°C" % slider_temp.value
	label_rain_val.text = "%.1f mm" % slider_rain.value

func _on_moisture_changed(val: float):
	plots[selected_plot_index]["moisture"] = val
	label_moisture_val.text = "%.1f%%" % val
	_refresh_plot_button(selected_plot_index)

func _on_temp_changed(val: float):
	plots[selected_plot_index]["temp"] = val
	label_temp_val.text = "%.1f°C" % val
	_refresh_plot_button(selected_plot_index)

func _on_rain_changed(val: float):
	label_rain_val.text = "%.1f mm" % val

func _refresh_plot_button(idx: int):
	var p = plots[idx]
	plot_buttons[idx].text = "%s [%s]\n%s (%s)\n%s\nM: %.1f%% | T: %.1f°C\nState: %s" % [
		p["id"].to_upper(), p["node"], p["name"], p["crop"], p["state"], p["moisture"], p["temp"], p["status"]
	]

func _load_scenario(moist: float, temp: float, rain: float, spoof: bool):
	slider_moisture.value = moist
	slider_temp.value = temp
	slider_rain.value = rain
	spoof_signature_active = spoof
	plots[selected_plot_index]["moisture"] = moist
	plots[selected_plot_index]["temp"] = temp
	_refresh_plot_button(selected_plot_index)
	if spoof:
		_log("[ARMED] Corrupted ECDSA signature payload armed. Test HTTP 403 defense.")
	elif rain >= 70.0:
		_log("[ARMED] Heavy precipitation deluge breach scenario armed.")
	elif moist > 85.0:
		_log("[ARMED] Bucket immersion anomaly armed. Expect meteorological hold.")
	elif moist < 15.0:
		_log("[ARMED] Soil drought parametric breach scenario armed.")
	else:
		_log("[ARMED] Nominal agronomic baseline armed.")

	_on_send_pressed()

func _on_reset_pressed():
	_log("[RESET] Requesting full backend state reset...")
	var http_reset = HTTPRequest.new()
	add_child(http_reset)
	http_reset.request_completed.connect(func(_res, code, _h, _b):
		if code == 200:
			_log("✅ Backend demo ledger and replay cache successfully reset.")
			for p in plots:
				p["status"] = "SAFE"
				p["moisture"] = 32.0
				p["temp"] = 28.5
			slider_moisture.value = 32.0
			slider_temp.value = 28.5
			slider_rain.value = 0.0
			spoof_signature_active = false
			for i in range(plots.size()):
				_refresh_plot_button(i)
		http_reset.queue_free()
	)
	var headers = ["Content-Type: application/json"]
	http_reset.request(BACKEND_URL + "/api/policies/reset", headers, HTTPClient.METHOD_POST, "{}")

func _on_send_pressed():
	var p = plots[selected_plot_index]
	_log("\n--- TRANSMITTING TELEMETRY ---")
	_log("[STEP 1] Generating telemetry for " + p["id"] + " (" + p["node"] + ")")

	var telemetry_data = {
		"plot_id": p["id"],
		"timestamp": Time.get_unix_time_from_system(),
		"temperature": slider_temp.value,
		"humidity": 45.0,
		"pressure": 1012.0,
		"soil_moisture": slider_moisture.value,
		"rainfall_mm": slider_rain.value
	}

	var sign_payload = {
		"node_id": p["node"],
		"telemetry": telemetry_data
	}

	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify(sign_payload)
	http_signer.request(BACKEND_URL + "/api/simulator/sign", headers, HTTPClient.METHOD_POST, body)

func _on_signer_completed(_result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray):
	if response_code != 200:
		_log("[ERROR] Signing endpoint returned: " + str(response_code))
		return

	var packet = JSON.parse_string(body.get_string_from_utf8())
	if packet == null:
		_log("[ERROR] Could not parse signer response.")
		return

	if spoof_signature_active:
		var orig_sig = packet.get("signature", "")
		packet["signature"] = orig_sig.substr(0, orig_sig.length() - 8) + "0000dead"
		_log("[TAMPER] Injected corrupted ECDSA SECP256k1 signature bytes.")

	_log("[STEP 2] Dispatching to Ingestion Gateway: POST /api/telemetry")
	var headers = ["Content-Type: application/json"]
	var body_json = JSON.stringify(packet)
	http_sender.request(BACKEND_URL + "/api/telemetry", headers, HTTPClient.METHOD_POST, body_json)

func _on_sender_completed(_result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray):
	var resp_str = body.get_string_from_utf8()
	var json_data = JSON.parse_string(resp_str)

	if response_code == 200:
		var status = json_data.get("status", "")
		if status == "HELD_FOR_FIELD_INSPECTION":
			_log("🛑 [AUDIT FLAGGED] Physical Divergence Detected!")
			_log("   Notice: On-plot reading diverges from reference station. Held for field inspection.")
			plots[selected_plot_index]["status"] = "HELD"
		else:
			_log("✅ [HTTP 200] Telemetry Accepted & SECP256k1 Signature Verified.")
			var ev = json_data.get("evaluation", {})
			if ev.get("triggered", false):
				_log("🎉 [PARAMETRIC BREACH] Claim Intent Generated: Rs. " + str(ev.get("payout_amount", 0)))
				_log("   Settlement Status: SIMULATED (Underwriter Banking Gateway Not Connected)")
				plots[selected_plot_index]["status"] = "BREACH"
			else:
				_log("🌾 [NOMINAL] Measurements within policy safety thresholds.")
				plots[selected_plot_index]["status"] = "SAFE"
		_refresh_plot_button(selected_plot_index)
	elif response_code == 403:
		_log("🛡️ [HTTP 403 FORBIDDEN] Security Gateway Blocked Packet!")
		if json_data != null and json_data.has("detail"):
			var detail = json_data["detail"]
			_log("   Reason: " + str(detail.get("message", "Cryptographic signature validation failure")))
		plots[selected_plot_index]["status"] = "REJECTED"
		_refresh_plot_button(selected_plot_index)
	else:
		_log("[HTTP " + str(response_code) + "] " + resp_str)

func _on_sync_timer():
	var http_sync = HTTPRequest.new()
	add_child(http_sync)
	http_sync.request_completed.connect(func(_res, code, _h, body):
		if code == 200:
			var data = JSON.parse_string(body.get_string_from_utf8())
			if data != null and data.has("grid"):
				for item in data["grid"]:
					for p in plots:
						if p["id"] == item.get("plot_id"):
							p["status"] = item.get("status", p["status"])
							_refresh_plot_button(plots.find(p))
		http_sync.queue_free()
	)
	var headers = ["Accept: application/json"]
	http_sync.request(BACKEND_URL + "/api/grid", headers, HTTPClient.METHOD_GET)

func _log(msg: String):
	var time_str = Time.get_time_string_from_system()
	log_text.text += "[%s] %s\n" % [time_str, msg]
	log_text.scroll_vertical = 999999
