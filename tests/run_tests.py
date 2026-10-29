"""
AgriSentinel Standard Test Runner (Zero-Dependency & Fully Mocked)
==================================================================
Runs acceptance tests using Python standard library (unittest).
Mocks external network calls (requests.get, twilio, groq) so the entire
suite executes in <0.5 seconds completely offline and deterministically.
"""

import sys
import os
import time
import asyncio
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from farm_registry import (
    FARM_PROFILES,
    DEVICE_REGISTRY,
    SIMULATOR_TEST_PRIVATE_KEYS
)
from crypto_engine import CryptoEngine
from satellite_verifier import SatelliteVerifier
from insurance_engine import ParametricInsuranceEngine
from advisor_service import GroqAdvisoryService
from telecom_service import TelecomVoiceEngine

class TestAgriSentinelSuite(unittest.TestCase):
    def setUp(self):
        CryptoEngine.reset_replay_cache()

    # --- 1. SECURITY & DEVICE-TRUST TESTS ---
    def test_01_valid_registered_device_telemetry_accepted(self):
        node_id = "node_1"
        plot_id = "plot_1"
        sk_hex = SIMULATOR_TEST_PRIVATE_KEYS[node_id]

        telemetry = {
            "plot_id": plot_id,
            "timestamp": time.time(),
            "temperature": 29.0,
            "humidity": 45.0,
            "pressure": 1012.0,
            "soil_moisture": 32.0,
            "rainfall_mm": 0.0
        }
        signature = CryptoEngine.sign_payload(sk_hex, telemetry)
        valid, msg, meta = CryptoEngine.verify_telemetry_packet(
            node_id=node_id,
            claimed_plot_id=plot_id,
            signature_hex=signature,
            telemetry_dict=telemetry
        )
        self.assertTrue(valid, f"Expected valid, got: {msg}")
        self.assertTrue(meta["signature_valid"])
        self.assertTrue(meta["device_registered"])
        self.assertTrue(meta["plot_binding_valid"])

    def test_02_tampered_payload_rejected(self):
        node_id = "node_1"
        plot_id = "plot_1"
        sk_hex = SIMULATOR_TEST_PRIVATE_KEYS[node_id]

        telemetry = {
            "plot_id": plot_id,
            "timestamp": time.time(),
            "temperature": 29.0,
            "humidity": 45.0,
            "pressure": 1012.0,
            "soil_moisture": 32.0,
            "rainfall_mm": 0.0
        }
        signature = CryptoEngine.sign_payload(sk_hex, telemetry)

        tampered = telemetry.copy()
        tampered["soil_moisture"] = 10.0  # Modified after signing

        valid, msg, meta = CryptoEngine.verify_telemetry_packet(
            node_id=node_id,
            claimed_plot_id=plot_id,
            signature_hex=signature,
            telemetry_dict=tampered
        )
        self.assertFalse(valid)

    def test_03_unregistered_device_rejected(self):
        telemetry = {
            "plot_id": "plot_1",
            "timestamp": time.time(),
            "temperature": 28.0,
            "humidity": 45.0,
            "pressure": 1012.0,
            "soil_moisture": 30.0,
            "rainfall_mm": 0.0
        }
        valid, msg, meta = CryptoEngine.verify_telemetry_packet(
            node_id="unknown_rogue_node",
            claimed_plot_id="plot_1",
            signature_hex="aabbccdd" * 8,
            telemetry_dict=telemetry
        )
        self.assertFalse(valid)
        self.assertEqual(meta["failure_stage"], "UNREGISTERED_DEVICE")

    def test_04_device_plot_impersonation_rejected(self):
        node_id = "node_1"
        claimed_plot = "plot_2"
        sk_hex = SIMULATOR_TEST_PRIVATE_KEYS[node_id]

        telemetry = {
            "plot_id": claimed_plot,
            "timestamp": time.time(),
            "temperature": 28.0,
            "humidity": 45.0,
            "pressure": 1012.0,
            "soil_moisture": 30.0,
            "rainfall_mm": 0.0
        }
        signature = CryptoEngine.sign_payload(sk_hex, telemetry)

        valid, msg, meta = CryptoEngine.verify_telemetry_packet(
            node_id=node_id,
            claimed_plot_id=claimed_plot,
            signature_hex=signature,
            telemetry_dict=telemetry
        )
        self.assertFalse(valid)
        self.assertEqual(meta["failure_stage"], "DEVICE_PLOT_MISMATCH")

    def test_05_replay_attack_blocked(self):
        node_id = "node_3"
        plot_id = "plot_3"
        sk_hex = SIMULATOR_TEST_PRIVATE_KEYS[node_id]

        telemetry = {
            "plot_id": plot_id,
            "timestamp": time.time(),
            "temperature": 28.0,
            "humidity": 45.0,
            "pressure": 1012.0,
            "soil_moisture": 30.0,
            "rainfall_mm": 0.0
        }
        signature = CryptoEngine.sign_payload(sk_hex, telemetry)

        v1, _, _ = CryptoEngine.verify_telemetry_packet(node_id, plot_id, signature, telemetry)
        self.assertTrue(v1)

        v2, msg2, meta2 = CryptoEngine.verify_telemetry_packet(node_id, plot_id, signature, telemetry)
        self.assertFalse(v2)
        self.assertEqual(meta2["failure_stage"], "REPLAY_DETECTED")

    def test_06_physical_sensor_bounds_enforced(self):
        telemetry_bad = {
            "soil_moisture": 140.0,
            "temperature": 28.0,
            "humidity": 45.0,
            "pressure": 1012.0,
            "rainfall_mm": 0.0
        }
        ok, reason = CryptoEngine.validate_sensor_physical_bounds(telemetry_bad)
        self.assertFalse(ok)
        self.assertIn("Soil moisture", reason)

    # --- 2. DATA CONSISTENCY TESTS ---
    def test_07_nine_farm_profiles_consistent(self):
        self.assertEqual(len(FARM_PROFILES), 9)
        self.assertEqual(len(DEVICE_REGISTRY), 9)
        nodes = set()
        for pid, p in FARM_PROFILES.items():
            nodes.add(p["assigned_node_id"])
            self.assertGreater(p["sum_insured_inr"], 0)
        self.assertEqual(len(nodes), 9)

    # --- 3. WEATHER CORROBORATION TESTS (OFFLINE MOCKED) ---
    @patch("requests.get")
    def test_08_weather_transparency(self, mock_get):
        mock_get.side_effect = Exception("Offline test")
        ref = SatelliteVerifier.fetch_reference_weather("plot_1")
        self.assertEqual(ref["data_type"], "SYNTHETIC_BASELINE")
        self.assertIn("rain_1h_mm", ref)

    @patch("requests.get")
    def test_09_bucket_immersion_flagged(self, mock_get):
        mock_get.side_effect = Exception("Offline test")
        telemetry = {"plot_id": "plot_1", "soil_moisture": 96.0, "temperature": 30.0, "rainfall_mm": 0.0}
        res = SatelliteVerifier.verify_telemetry("plot_1", telemetry)
        self.assertFalse(res["is_corroborated"])
        self.assertEqual(res["corroboration_status"], "DIVERGENCE_HELD_FOR_INSPECTION")

    # --- 4. PARAMETRIC INSURANCE ENGINE TESTS (OFFLINE MOCKED) ---
    @patch("requests.get")
    def test_10_parametric_breach_claim_intent(self, mock_get):
        mock_get.side_effect = Exception("Offline test")
        eng = ParametricInsuranceEngine()
        telemetry = {
            "plot_id": "plot_1",
            "timestamp": time.time(),
            "temperature": 43.0,
            "humidity": 20.0,
            "pressure": 1012.0,
            "soil_moisture": 11.0,
            "rainfall_mm": 0.0
        }
        crypto_meta = {"registered_key_used": "key", "signature_valid": True}
        res = eng.evaluate_telemetry("node_1", telemetry, True, crypto_meta)
        self.assertTrue(res["triggered"])
        self.assertEqual(res["status"], "PARAMETRIC_BREACH_CLAIM_INTENT_GENERATED")
        self.assertEqual(len(eng.claims), 1)
        self.assertEqual(eng.claims[0]["assessment_status"], "CLAIM_INTENT_APPROVED_SIMULATED")

    def test_11_reset_restores_clean_baseline(self):
        eng = ParametricInsuranceEngine()
        eng.claims.append({"fake": 1})
        eng.tamper_blocked_count = 10
        eng.reset_system()
        self.assertEqual(len(eng.claims), 0)
        self.assertEqual(eng.tamper_blocked_count, 0)
        self.assertTrue(all(p["active"] for p in eng.policies.values()))

    # --- 5. AGRONOMIC ADVISORY TESTS (DETERMINISTIC) ---
    def test_12_unsupported_crop_not_substituted(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            res = asyncio.run(
                GroqAdvisoryService.get_agronomic_advisory("plot_1", "Avocado", 20.0, 28.0, 0.0)
            )
        self.assertEqual(res["status"], "UNSUPPORTED_CROP")
        self.assertNotIn("payout_status", res)

    def test_13_spray_caution_present(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            res = asyncio.run(
                GroqAdvisoryService.get_agronomic_advisory("plot_1", "Paddy", 12.0, 42.0, 0.0)
            )
        self.assertIn("spray_caution", res)
        self.assertNotIn("payout_status", res)

    # --- 6. TELECOM VOICE TESTS (DETERMINISTIC) ---
    def test_14_twiml_generation(self):
        xml = TelecomVoiceEngine.generate_breach_twiml("plot_1", 12.0, 50000.0, "ta-IN")
        self.assertIn("<Response>", xml)
        self.assertIn("<Say", xml)
        self.assertIn("<Gather", xml)

    def test_15_unconfigured_voice_dispatch_simulation(self):
        with patch.dict(os.environ, {"TWILIO_ACCOUNT_SID": "", "TWILIO_AUTH_TOKEN": ""}):
            res = asyncio.run(
                TelecomVoiceEngine.dispatch_voice_alert(
                    to_phone="+919876543210",
                    plot_id="plot_1",
                    moisture=12.0,
                    payout_amount=50000.0,
                    webhook_base_url="http://127.0.0.1:8000"
                )
            )
        self.assertEqual(res["status"], "SIMULATED_VOICE_DISPATCH")
        self.assertTrue(res["twiml_generated"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
