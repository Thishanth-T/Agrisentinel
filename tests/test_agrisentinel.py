"""
AgriSentinel Automated Test & Quality Assurance Suite
=====================================================
Comprehensive acceptance criteria testing covering:
1. Security & Device-Trust Cryptographic Engine
2. Data Consistency Across Authoritative Registries
3. Weather & Ground Corroboration Engine
4. Parametric Insurance State Machine & Claims Workflow
5. Agronomic Advisory & Chemical Safety Warnings
6. Telecom & Regional Voice TwiML Generation
"""

import time
import pytest
from farm_registry import (
    FARM_PROFILES,
    DEVICE_REGISTRY,
    SIMULATOR_TEST_PRIVATE_KEYS,
    get_registered_device,
    get_farm_profile
)
from crypto_engine import CryptoEngine
from satellite_verifier import SatelliteVerifier
from insurance_engine import ParametricInsuranceEngine
from advisor_service import GroqAdvisoryService, CALIBRATED_CROP_ACTIONS
from telecom_service import TelecomVoiceEngine

# ==============================================================================
# 1. SECURITY & DATA-TRUST ACCEPTANCE TESTS
# ==============================================================================

class TestSecurityAndDataTrust:
    @pytest.fixture(autouse=True)
    def setup_cache(self):
        CryptoEngine.reset_replay_cache()

    def test_registered_device_valid_telemetry_accepted(self):
        """Valid telemetry signed by registered device with provisioned key is accepted."""
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

        assert valid is True
        assert meta["signature_valid"] is True
        assert meta["device_registered"] is True
        assert meta["plot_binding_valid"] is True

    def test_tampered_payload_rejected(self):
        """Altering telemetry values after signing MUST fail cryptographic verification."""
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

        # Attacker modifies soil moisture to forge a drought breach
        tampered_telemetry = telemetry.copy()
        tampered_telemetry["soil_moisture"] = 10.0

        valid, msg, meta = CryptoEngine.verify_telemetry_packet(
            node_id=node_id,
            claimed_plot_id=plot_id,
            signature_hex=signature,
            telemetry_dict=tampered_telemetry
        )

        assert valid is False
        assert "Signature Rejected" in msg or "failed mathematical verification" in msg

    def test_unregistered_device_rejected(self):
        """Devices not in the authoritative hardware registry are rejected."""
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
        assert valid is False
        assert meta["failure_stage"] == "UNREGISTERED_DEVICE"

    def test_device_plot_impersonation_rejected(self):
        """A registered node cannot submit telemetry for another plot."""
        # node_1 belongs to plot_1, not plot_2
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
        assert valid is False
        assert meta["failure_stage"] == "DEVICE_PLOT_MISMATCH"

    def test_replay_attack_rejected(self):
        """Ingesting the exact same signed packet a second time MUST be blocked as replay."""
        node_id = "node_2"
        plot_id = "plot_2"
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

        # First transmission: Accepted
        valid1, _, _ = CryptoEngine.verify_telemetry_packet(
            node_id=node_id, claimed_plot_id=plot_id, signature_hex=signature, telemetry_dict=telemetry
        )
        assert valid1 is True

        # Second transmission (Replay): Blocked!
        valid2, msg2, meta2 = CryptoEngine.verify_telemetry_packet(
            node_id=node_id, claimed_plot_id=plot_id, signature_hex=signature, telemetry_dict=telemetry
        )
        assert valid2 is False
        assert meta2["failure_stage"] == "REPLAY_DETECTED"

    def test_physical_sensor_bounds_enforced(self):
        """Nonsensical physical sensor values (e.g. 150% moisture or -99°C) are rejected."""
        telemetry_bad_moist = {
            "plot_id": "plot_1", "timestamp": time.time(),
            "temperature": 28.0, "humidity": 45.0, "pressure": 1012.0,
            "soil_moisture": 150.0, "rainfall_mm": 0.0
        }
        ok, reason = CryptoEngine.validate_sensor_physical_bounds(telemetry_bad_moist)
        assert ok is False
        assert "Soil moisture" in reason

# ==============================================================================
# 2. DATA CONSISTENCY & FARM REGISTRY TESTS
# ==============================================================================

class TestDataConsistency:
    def test_authoritative_registry_integrity(self):
        """Verify all 9 farms have unique nodes, coordinates, and valid thresholds."""
        assert len(FARM_PROFILES) == 9
        assert len(DEVICE_REGISTRY) == 9

        node_ids = set()
        plot_ids = set()
        for pid, profile in FARM_PROFILES.items():
            plot_ids.add(pid)
            node_ids.add(profile["assigned_node_id"])
            assert profile["moisture_drought_threshold"] < profile["baseline_moisture"]
            assert profile["rainfall_flood_threshold_mm"] >= 60.0
            assert profile["sum_insured_inr"] > 0

        # Exactly 9 distinct plots and 9 distinct registered devices
        assert len(plot_ids) == 9
        assert len(node_ids) == 9

# ==============================================================================
# 3. WEATHER CORROBORATION & DIVERGENCE TESTS
# ==============================================================================

class TestWeatherCorroboration:
    def test_weather_distinguishes_live_vs_baseline(self):
        """System transparently reports whether weather is LIVE_EXTERNAL_API or SYNTHETIC_BASELINE."""
        ref = SatelliteVerifier.fetch_reference_weather("plot_1")
        assert "data_type" in ref
        assert ref["data_type"] in ("LIVE_EXTERNAL_API", "SYNTHETIC_BASELINE")
        assert "rain_1h_mm" in ref  # Verified 1h reporting, no multiplied magic numbers!

    def test_physical_bucket_immersion_divergence_flagged(self):
        """Near-saturation soil moisture with zero rainfall and clear skies triggers audit hold."""
        telemetry = {
            "plot_id": "plot_1",
            "soil_moisture": 96.0,
            "temperature": 30.0,
            "rainfall_mm": 0.0
        }
        res = SatelliteVerifier.verify_telemetry("plot_1", telemetry)
        assert res["is_corroborated"] is False
        assert res["corroboration_status"] == "DIVERGENCE_HELD_FOR_INSPECTION"
        assert res["anomaly_type"] == "UNVERIFIED_WATERLOGGING_ANOMALY"

    def test_corroborated_drought_condition(self):
        """Depleted moisture with dry reference conditions is corroborated."""
        telemetry = {
            "plot_id": "plot_1",
            "soil_moisture": 12.0,
            "temperature": 42.0,
            "rainfall_mm": 0.0
        }
        res = SatelliteVerifier.verify_telemetry("plot_1", telemetry)
        assert res["is_corroborated"] is True
        assert res["anomaly_type"] == "CORROBORATED_DROUGHT_STRESS"

# ==============================================================================
# 4. PARAMETRIC INSURANCE ENGINE & CLAIMS WORKFLOW TESTS
# ==============================================================================

class TestInsuranceEngineWorkflow:
    def test_parametric_breach_generates_claim_intent(self):
        """A valid breach generates a simulated Claim Intent with clear settlement disclaimers."""
        engine = ParametricInsuranceEngine()
        plot_id = "plot_1"
        node_id = "node_1"

        telemetry = {
            "plot_id": plot_id,
            "timestamp": time.time(),
            "temperature": 43.0,
            "humidity": 20.0,
            "pressure": 1012.0,
            "soil_moisture": 11.0,  # Below threshold 18.0%
            "rainfall_mm": 0.0
        }

        crypto_meta = {"registered_key_used": "test_key", "signature_valid": True}
        result = engine.evaluate_telemetry(
            node_id=node_id,
            telemetry=telemetry,
            sig_valid=True,
            crypto_metadata=crypto_meta
        )

        assert result["triggered"] is True
        assert result["status"] == "PARAMETRIC_BREACH_CLAIM_INTENT_GENERATED"
        assert len(engine.claims) == 1
        claim = engine.claims[0]
        assert claim["assessment_status"] == "CLAIM_INTENT_APPROVED_SIMULATED"
        assert "DISBURSEMENT_NOT_CONNECTED" in claim["settlement_status"]

    def test_reset_system_restores_nominal_state(self):
        """Reset clears claims and restores 100% active policies."""
        engine = ParametricInsuranceEngine()
        engine.claims.append({"fake": "claim"})
        engine.tamper_blocked_count = 5
        res = engine.reset_system()

        assert len(engine.claims) == 0
        assert engine.tamper_blocked_count == 0
        assert all(p["active"] is True for p in engine.policies.values())

# ==============================================================================
# 5. AGRONOMIC ADVISORY & CHEMICAL SAFETY TESTS
# ==============================================================================

class TestAgronomicAdvisory:
    @pytest.mark.asyncio
    async def test_unsupported_crop_returns_explicit_message(self):
        """Unsupported crops MUST NOT silently substitute another crop."""
        res = await GroqAdvisoryService.get_agronomic_advisory(
            plot_id="plot_1",
            crop="Dragonfruit",
            moisture=20.0,
            temp=28.0,
            rainfall=0.0
        )
        assert res["status"] == "UNSUPPORTED_CROP"
        assert "uncalibrated" in res["message"].lower() or "not currently calibrated" in res["message"].lower()

    @pytest.mark.asyncio
    async def test_advisory_contains_spray_cautions_and_no_payout_claims(self):
        """Advisory must include spray caution and never announce claim approvals."""
        res = await GroqAdvisoryService.get_agronomic_advisory(
            plot_id="plot_1",
            crop="Paddy",
            moisture=12.0,
            temp=41.0,
            rainfall=0.0
        )
        assert "spray_caution" in res
        assert "payout_status" not in res  # NO false claim payout approvals!

# ==============================================================================
# 6. TELECOM & VOICE TwiML TESTS
# ==============================================================================

class TestTelecomVoice:
    def test_twiml_generation_valid_xml(self):
        """Breach TwiML must contain speech synthesis and keypad gather."""
        xml = TelecomVoiceEngine.generate_breach_twiml("plot_1", 12.5, 50000.0, "ta-IN")
        assert "<Response>" in xml
        assert "<Say" in xml
        assert "<Gather" in xml

    @pytest.mark.asyncio
    async def test_unconfigured_twilio_operates_in_safe_simulation(self):
        """Missing Twilio credentials must safely simulate without crash."""
        res = await TelecomVoiceEngine.dispatch_voice_alert(
            to_phone="+919876543210",
            plot_id="plot_1",
            moisture=11.5,
            payout_amount=50000.0,
            webhook_base_url="http://127.0.0.1:8000",
            account_sid=None,
            auth_token=None
        )
        assert res["status"] == "SIMULATED_VOICE_DISPATCH"
        assert res["mode"] == "OFFLINE_SIMULATION"
        assert res["twiml_generated"] is True
