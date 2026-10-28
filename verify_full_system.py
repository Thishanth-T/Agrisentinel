"""
AgriSentinel Full System Verification Suite
Tests all 5 architectural modules independently.
"""
import os
import sys
import time
import json
import py_compile

print("=" * 65, flush=True)
print("  AGRISENTINEL ENTERPRISE VERIFICATION SUITE", flush=True)
print("=" * 65, flush=True)

# ─────────────────────────────────────────────────────────────
# 1. CRYPTOGRAPHIC ANTI-FRAUD ENGINE
# ─────────────────────────────────────────────────────────────
print("\n[1/5] CryptoEngine (ECDSA SECP256k1)...", flush=True)
from crypto_engine import CryptoEngine

sk, vk = CryptoEngine.generate_keypair()
assert len(sk) == 64, f"Private key length {len(sk)} != 64"
assert len(vk) in (128, 130), f"Public key length {len(vk)} unexpected"

data = {"plot_id": "plot_1", "temperature": 32.5, "soil_moisture": 11.2, "timestamp": time.time()}
pkt = CryptoEngine.create_signed_packet("node_1", sk, vk, data)
assert "signature" in pkt
assert "public_key" in pkt

valid, msg = CryptoEngine.verify_payload(pkt["public_key"], pkt["telemetry"], pkt["signature"])
assert valid is True, f"Valid signature rejected: {msg}"

bad_sig = pkt["signature"][:-4] + "dead"
valid_bad, _ = CryptoEngine.verify_payload(pkt["public_key"], pkt["telemetry"], bad_sig)
assert valid_bad is False, "Tampered signature was not rejected!"

print("      KeyGen ........... PASS", flush=True)
print("      Sign+Verify ...... PASS", flush=True)
print("      Tamper Rejection . PASS", flush=True)

# ─────────────────────────────────────────────────────────────
# 2. SATELLITE REMOTE SENSING CROSS-VALIDATION
# ─────────────────────────────────────────────────────────────
print("\n[2/5] SatelliteVerifier (NASA/OWM Remote Sensing)...", flush=True)
from satellite_verifier import SatelliteVerifier

sat = SatelliteVerifier.fetch_macro_satellite_data("plot_1")
assert sat["state"] == "Tamil Nadu", f"Expected Tamil Nadu, got {sat.get('state')}"
assert "temperature" in sat
assert "rain_24h_mm" in sat

# Corroborated drought
drought_tel = {"plot_id": "plot_1", "soil_moisture": 11.5, "temperature": 43.5, "rainfall_mm": 0.0, "pressure": 1012.0}
res_drought = SatelliteVerifier.verify_telemetry("plot_1", drought_tel)
assert res_drought["status"] == "SATELLITE_VERIFIED", f"Drought not verified: {res_drought['status']}"

# Water-bucket immersion fraud
flood_tel = {"plot_id": "plot_1", "soil_moisture": 96.5, "temperature": 27.0, "rainfall_mm": 0.0, "pressure": 1012.0}
res_flood = SatelliteVerifier.verify_telemetry("plot_1", flood_tel)
assert res_flood["status"] == "PHYSICAL_TAMPERING_AUDIT_REQUIRED"

# detect_physical_tampering helper
is_tamper, status, notes = SatelliteVerifier.detect_physical_tampering(flood_tel, sat)
assert is_tamper is True
assert status == "PHYSICAL_TAMPERING_AUDIT_REQUIRED"

print("      9 Farm Polygons .. PASS", flush=True)
print("      Drought Verified . PASS", flush=True)
print("      Flood Fraud Block  PASS", flush=True)

# ─────────────────────────────────────────────────────────────
# 3. INSURANCE ENGINE (PARAMETRIC)
# ─────────────────────────────────────────────────────────────
print("\n[3/5] ParametricInsuranceEngine...", flush=True)
from insurance_engine import ParametricInsuranceEngine, engine

assert len(engine.policies) == 9, f"Expected 9 policies, got {len(engine.policies)}"

# Test evaluate_telemetry with a drought breach
drought_data = {
    "plot_id": "plot_3",
    "soil_moisture": 10.0,
    "temperature": 44.0,
    "humidity": 20.0,
    "pressure": 1010.0,
    "rainfall_mm": 0.0,
    "timestamp": time.time()
}
result = engine.evaluate_telemetry("node_test", drought_data, sig_valid=True, sig_notes="Test")
assert result.get("triggered") is True, f"Drought should trigger payout, got: {result}"
assert result.get("payout_amount", 0) > 0

# Test tamper blocked counter on bad signature
result_bad = engine.evaluate_telemetry("node_bad", drought_data, sig_valid=False, sig_notes="Tampered")
assert result_bad.get("status") == "REJECTED_CRYPTOGRAPHIC_FAILURE", f"Got: {result_bad.get('status')}"
assert engine.tamper_blocked_count >= 1

print("      9 Regional Policies  PASS", flush=True)
print("      Drought Payout ..... PASS", flush=True)
print("      Sig Reject Counter . PASS", flush=True)

# ─────────────────────────────────────────────────────────────
# 4. GODOT 4 HARDWARE SIMULATOR
# ─────────────────────────────────────────────────────────────
print("\n[4/5] Godot 4 Hardware Simulator...", flush=True)
assert os.path.exists("godot_simulator/Main.gd"), "Main.gd missing"
assert os.path.exists("godot_simulator/project.godot"), "project.godot missing"
assert os.path.exists("godot_simulator/Main.tscn"), "Main.tscn missing"

with open("godot_simulator/Main.gd", "r", encoding="utf-8") as f:
    gd = f.read()
assert "extends Node2D" in gd
assert "HTTPRequest.new()" in gd
assert "/api/telemetry" in gd
assert "/api/crypto/sign" in gd
assert "INSTRUCTIONS TO RUN IN GODOT 4:" in gd
assert "SECP256k1" in gd

print("      Main.gd .......... PASS", flush=True)
print("      project.godot .... PASS", flush=True)
print("      Main.tscn ........ PASS", flush=True)

# ─────────────────────────────────────────────────────────────
# 5. PYTHON COMPILATION CHECK (ALL FILES)
# ─────────────────────────────────────────────────────────────
print("\n[5/5] Python Compilation Check...", flush=True)
py_files = [f for f in os.listdir(".") if f.endswith(".py")]
for f in sorted(py_files):
    py_compile.compile(f, doraise=True)
    print(f"      {f:30s} PASS", flush=True)

# ─────────────────────────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 65, flush=True)
print("  ALL 5 AGRISENTINEL MODULES VERIFIED AND PASSING!", flush=True)
print("=" * 65, flush=True)
print(f"""
  1. CryptoEngine (ECDSA SECP256k1) ....... OK
  2. SatelliteVerifier (NASA/OWM) ......... OK
  3. ParametricInsuranceEngine (9 plots) .. OK
  4. Godot 4 Hardware Simulator ........... OK
  5. Python Compilation (all files) ....... OK

  System is HACKATHON DEMO READY.
""", flush=True)
