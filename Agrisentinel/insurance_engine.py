"""
AgriSentinel Parametric Insurance Engine
========================================
Automated parametric breach evaluation, evidence package assembly, and
simulated claims workflow for Indian smallholder agriculture.

CLAIM WORKFLOW TRANSPARENCY:
1. Event Detection: Sensor breaches contractual policy parameter (e.g., soil drought or rainfall deluge).
2. Evidence Packaging: Binds cryptographically signed telemetry, independent weather corroboration, and device trust.
3. Eligibility Decision: Computes indemnity benefit under parametric micro-rider schedule.
4. Simulated Settlement: Generates an auditable Claim Intent Record and stores in SQLite.
"""

import time
import uuid
import json
from typing import Dict, List, Any, Optional

from farm_registry import FARM_PROFILES, get_farm_profile
from satellite_verifier import SatelliteVerifier
from database import db
from evidence_reconciliation import evidence_engine

class ParametricInsuranceEngine:
    def __init__(self):
        self.tamper_blocked_count: int = 0
        self.claims: List[Dict[str, Any]] = []
        self.audit_log: List[Dict[str, Any]] = []
        self.plot_telemetry: Dict[str, Dict[str, Any]] = {}
        self.policies: Dict[str, Dict[str, Any]] = {}

        self.initialize_state()

    def initialize_state(self):
        """Initializes authoritative policies and nominal telemetry baseline."""
        self.policies.clear()
        self.plot_telemetry.clear()

        # Seed farms and devices into database if empty
        with db.get_connection() as conn:
            for pid, profile in FARM_PROFILES.items():
                conn.execute(
                    """
                    INSERT OR IGNORE INTO farms 
                    (plot_id, farmer_name, phone, crop, state, district, region, lat, lon, language_code, language_name,
                     sum_insured_inr, moisture_drought_threshold, temp_heatwave_threshold, rainfall_flood_threshold_mm,
                     moisture_saturation_threshold, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (pid, profile["farmer_name"], profile["phone"], profile["crop"], profile["state"], profile["district"],
                     profile["region"], profile["lat"], profile["lon"], profile["language_code"], profile["language_name"],
                     profile["sum_insured_inr"], profile["moisture_drought_threshold"], profile["temp_heatwave_threshold"],
                     profile["rainfall_flood_threshold_mm"], profile["moisture_saturation_threshold"], time.time())
                )
                conn.execute(
                    """
                    INSERT OR IGNORE INTO devices
                    (device_id, plot_id, public_key_hex, hardware_model, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (profile["assigned_node_id"], pid, "65023d...", "AgriSentinel-Edge-ESP32-Rev2", "REGISTERED", time.time())
                )
                conn.execute(
                    """
                    INSERT OR IGNORE INTO device_state
                    (device_id, latest_sequence, latest_timestamp, battery_level, solar_charging, signal_strength, lifecycle_state, last_seen)
                    VALUES (?, 0, 0.0, 98.5, 1, -68, 'ONLINE', ?)
                    """,
                    (profile["assigned_node_id"], time.time())
                )
            conn.commit()

        # Load into memory cache for sub-millisecond API response
        for pid, profile in FARM_PROFILES.items():
            self.policies[pid] = {
                "plot_id": pid,
                "node_id": profile["assigned_node_id"],
                "farmer_name": profile["farmer_name"],
                "phone": profile["phone"],
                "crop": profile["crop"],
                "state": profile["state"],
                "district": profile["district"],
                "region": profile["region"],
                "language_code": profile["language_code"],
                "language_name": profile["language_name"],
                "sum_insured_inr": profile["sum_insured_inr"],
                "moisture_drought_threshold": profile["moisture_drought_threshold"],
                "temp_heatwave_threshold": profile["temp_heatwave_threshold"],
                "rainfall_flood_threshold_mm": profile["rainfall_flood_threshold_mm"],
                "moisture_saturation_threshold": profile["moisture_saturation_threshold"],
                "payout_ratio": 1.0,
                "active": True
            }

            self.plot_telemetry[pid] = {
                "plot_id": pid,
                "node_id": profile["assigned_node_id"],
                "soil_moisture": profile["baseline_moisture"],
                "temperature": profile["baseline_temp"],
                "humidity": 45.0,
                "pressure": 1012.0,
                "rainfall_mm": 0.0,
                "battery_level": 98.5,
                "status": "NORMAL",
                "crypto_status": "SECP256k1: PENDING",
                "weather_corroboration_status": "SYNCHRONIZED",
                "device_trust_score": 1.0,
                "reconciliation_outcome": "CONSISTENT",
                "last_updated": time.time(),
                "last_evidence_package": None
            }

    def reset_system(self):
        """Clean demonstration reset across in-memory cache and persistent SQLite."""
        self.tamper_blocked_count = 0
        self.claims.clear()
        self.audit_log.clear()

        # Record demo reset in tamper-evident audit trail
        db.record_audit_event(
            event_type="DEMO_RESET",
            plot_id=None,
            node_id=None,
            result="SUCCESS",
            details={"action": "Reset in-memory cache and reinitialized nominal telemetry baseline"}
        )

        self.initialize_state()
        return {"status": "success", "message": "Demo ledger and farm telemetry reset to nominal baseline"}

    def evaluate_telemetry(
        self,
        node_id: str,
        telemetry: Dict[str, Any],
        sig_valid: bool,
        crypto_metadata: Dict[str, Any],
        sig_notes: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluates incoming telemetry through the multi-stage parametric funnel:
        1. Cryptographic device check
        2. Weather corroboration check
        3. Adaptive device reliability evaluation
        4. Spatial-temporal evidence reconciliation
        5. Parametric policy trigger check
        6. Simulated Claim Intent generation & persistent logging
        """
        plot_id = telemetry.get("plot_id", "plot_1")
        policy = self.policies.get(plot_id)
        now = time.time()

        soil_moisture = float(telemetry.get("soil_moisture", 30.0))
        temperature = float(telemetry.get("temperature", 28.0))
        rainfall_mm = float(telemetry.get("rainfall_mm", 0.0))
        humidity = float(telemetry.get("humidity", 45.0))
        pressure = float(telemetry.get("pressure", 1012.0))
        battery = float(telemetry.get("battery_level", 98.0))
        sequence = int(telemetry.get("sequence", 0))

        # Check Step 1: Cryptographic Validity
        if not sig_valid:
            self.tamper_blocked_count += 1
            audit_entry = {
                "timestamp": now,
                "event": "TAMPER_ATTEMPT_BLOCKED",
                "plot_id": plot_id,
                "node_id": node_id,
                "reason": sig_notes,
                "result": "DROPPED_WITH_PREJUDICE"
            }
            self.audit_log.append(audit_entry)
            db.record_audit_event("SECURITY_TAMPER_BLOCKED", plot_id, node_id, "BLOCKED", {"reason": sig_notes})
            return {
                "triggered": False,
                "status": "TAMPER_BLOCKED",
                "message": f"Cryptographic integrity failed: {sig_notes}",
                "audit": audit_entry
            }

        # Check Step 2: Weather Corroboration
        weather_corrob = SatelliteVerifier.verify_telemetry(plot_id, telemetry)

        if not weather_corrob["is_corroborated"]:
            self.tamper_blocked_count += 1
            audit_entry = {
                "timestamp": now,
                "event": "METEOROLOGICAL_TAMPER_FLAGGED",
                "plot_id": plot_id,
                "node_id": node_id,
                "anomaly_type": weather_corrob["anomaly_type"],
                "notes": weather_corrob["audit_notes"],
                "result": "FLAGGED_FOR_EXPERT_REVIEW"
            }
            self.audit_log.append(audit_entry)
            db.record_audit_event("METEOROLOGICAL_ANOMALY", plot_id, node_id, "FLAGGED", weather_corrob)

            if self.plot_telemetry.get(plot_id):
                self.plot_telemetry[plot_id]["status"] = "TAMPER_FLAGGED"
                self.plot_telemetry[plot_id]["weather_corroboration_status"] = "ANOMALY_DETECTED"

            return {
                "triggered": False,
                "status": "METEOROLOGICAL_TAMPER_FLAGGED",
                "message": weather_corrob["audit_notes"],
                "weather_corroboration": weather_corrob,
                "audit": audit_entry
            }

        # Check Step 3: Adaptive Device Trust & Spatial-Temporal Evidence Reconciliation
        device_state = {"battery_level": battery}
        trust_score, health_status, trust_reasons = evidence_engine.calculate_device_trust_score(
            plot_id, telemetry, [], device_state
        )

        reconciliation = evidence_engine.reconcile_spatial_temporal_evidence(
            target_plot_id=plot_id,
            target_telemetry=telemetry,
            neighbor_telemetries=[],
            external_weather=weather_corrob.get("reference_data"),
            device_trust_score=trust_score
        )

        # Check Step 4: Parametric Policy Breach Evaluation
        drought_threshold = policy["moisture_drought_threshold"] if policy else 18.0
        heatwave_threshold = policy["temp_heatwave_threshold"] if policy else 41.5
        flood_threshold = policy["rainfall_flood_threshold_mm"] if policy else 70.0

        is_drought_breach = soil_moisture < drought_threshold
        is_heatwave_breach = temperature > heatwave_threshold
        is_flood_breach = rainfall_mm >= flood_threshold

        breach_detected = is_drought_breach or is_heatwave_breach or is_flood_breach

        # Assemble Evidence Package
        evidence_id = f"EVD-{uuid.uuid4().hex[:8].upper()}"
        evidence_package = {
            "evidence_id": evidence_id,
            "plot_id": plot_id,
            "node_id": node_id,
            "timestamp": now,
            "measurements": {
                "soil_moisture_pct": soil_moisture,
                "temperature_c": temperature,
                "humidity_pct": humidity,
                "pressure_hpa": pressure,
                "rainfall_mm": rainfall_mm,
                "battery_level": battery
            },
            "crypto_verification": {
                "algorithm": "ECDSA-SECP256k1",
                "registered_key": crypto_metadata.get("registered_public_key"),
                "status": "VERIFIED_AUTHENTIC",
                "sequence": sequence
            },
            "device_health": {
                "trust_score": trust_score,
                "health_status": health_status,
                "notes": trust_reasons
            },
            "reconciliation": reconciliation,
            "weather_corroboration": {
                "source": weather_corrob["reference_data"].get("source_name", "OpenWeatherMap"),
                "data_type": weather_corrob["reference_data"].get("data_type", "LIVE_API"),
                "status": weather_corrob["corroboration_status"]
            }
        }

        # Update in-memory telemetry state
        if plot_id in self.plot_telemetry:
            self.plot_telemetry[plot_id].update({
                "soil_moisture": soil_moisture,
                "temperature": temperature,
                "humidity": humidity,
                "pressure": pressure,
                "rainfall_mm": rainfall_mm,
                "battery_level": battery,
                "status": "PARAMETRIC_BREACH" if breach_detected else "NORMAL",
                "crypto_status": "SECP256k1: VERIFIED",
                "weather_corroboration_status": weather_corrob["badge"],
                "device_trust_score": trust_score,
                "reconciliation_outcome": reconciliation["reconciliation_outcome"],
                "last_updated": now,
                "last_evidence_package": evidence_package
            })

        # Save to SQLite telemetry archive
        try:
            with db.get_connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO telemetry_archive
                    (node_id, plot_id, sequence, timestamp, temperature, humidity, pressure, soil_moisture, rainfall_mm,
                     battery_level, signature_hex, digest_hex, reception_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (node_id, plot_id, sequence, now, temperature, humidity, pressure, soil_moisture, rainfall_mm,
                     battery, crypto_metadata.get("signature_hex", ""), crypto_metadata.get("digest_hex", uuid.uuid4().hex), now)
                )
                conn.execute(
                    """
                    INSERT OR REPLACE INTO evidence_packages
                    (evidence_id, plot_id, node_id, timestamp, telemetry_json, device_trust_score, device_health_status,
                     reconciliation_outcome, explanation, external_weather_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (evidence_id, plot_id, node_id, now, json.dumps(telemetry), trust_score, health_status,
                     reconciliation["reconciliation_outcome"], reconciliation["explanation"],
                     json.dumps(weather_corrob["reference_data"]), now)
                )
                conn.commit()
        except Exception as e:
            print(f"Database write error: {e}")

        # Check Step 5: Claim Intent Generation if parametric threshold breached
        if breach_detected:
            trigger_reason = ""
            claim_type = "DROUGHT"
            if is_drought_breach:
                trigger_reason = f"Severe Soil Drought Breach: {soil_moisture:.1f}% < Threshold {drought_threshold:.1f}%"
                claim_type = "DROUGHT"
            elif is_heatwave_breach:
                trigger_reason = f"Extreme Heatwave Event: {temperature:.1f}°C > Threshold {heatwave_threshold:.1f}°C"
                claim_type = "HEATWAVE"
            elif is_flood_breach:
                trigger_reason = f"Precipitation Deluge Breach: {rainfall_mm:.1f}mm >= Threshold {flood_threshold:.1f}mm"
                claim_type = "FLOOD"

            payout_amount = (policy["sum_insured_inr"] * policy.get("payout_ratio", 1.0)) if policy else 50000.0

            claim_id = f"CLM-{uuid.uuid4().hex[:8].upper()}"
            claim_record = {
                "claim_id": claim_id,
                "evidence_id": evidence_id,
                "plot_id": plot_id,
                "node_id": node_id,
                "farmer_name": policy["farmer_name"] if policy else "Farmer",
                "phone": policy["phone"] if policy else "+919876543210",
                "crop": policy["crop"] if policy else "Paddy",
                "state": policy["state"] if policy else "Tamil Nadu",
                "district": policy["district"] if policy else "Madurai",
                "region": policy["region"] if policy else "Vaigai Basin",
                "language_name": policy.get("language_name", "Tamil"),
                "language_code": policy.get("language_code", "ta-IN"),
                "payout_calculated_inr": payout_amount,
                "trigger_reason": trigger_reason,
                "claim_type": claim_type,
                "timestamp": now,
                "evidence_package": evidence_package,
                "assessment_status": "CLAIM_INTENT_APPROVED_SIMULATED",
                "settlement_status": "DISBURSEMENT_NOT_CONNECTED (DEMO_MODE)",
                "settlement_notice": "Claim intent validated under parametric micro-rider terms. Monetary disbursement requires underwriter core banking integration."
            }

            self.claims.insert(0, claim_record)

            # Persist claim intent to SQLite
            try:
                with db.get_connection() as conn:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO claims
                        (claim_id, evidence_id, plot_id, farmer_name, phone, crop, trigger_reason, claim_type,
                         payout_calculated_inr, assessment_status, settlement_status, settlement_notice, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (claim_id, evidence_id, plot_id, claim_record["farmer_name"], claim_record["phone"], claim_record["crop"],
                         trigger_reason, claim_type, payout_amount, claim_record["assessment_status"],
                         claim_record["settlement_status"], claim_record["settlement_notice"], now)
                    )
                    conn.commit()
            except Exception as e:
                print(f"Error persisting claim: {e}")

            audit_entry = {
                "timestamp": now,
                "event": "PARAMETRIC_BREACH_VERIFIED",
                "plot_id": plot_id,
                "node_id": node_id,
                "claim_id": claim_id,
                "payout_inr": payout_amount,
                "result": "CLAIM_INTENT_DISPATCHED",
                "reconciliation_outcome": reconciliation["reconciliation_outcome"]
            }
            self.audit_log.append(audit_entry)
            db.record_audit_event("PARAMETRIC_CLAIM_GENERATED", plot_id, node_id, "APPROVED_SIMULATED", audit_entry)

            return {
                "triggered": True,
                "status": "PARAMETRIC_BREACH_CLAIM_INTENT_GENERATED",
                "stage": "CLAIM_INTENT_DISPATCHED",
                "claim": claim_record,
                "farmer_phone": policy["phone"] if policy else "+919876543210",
                "payout_amount": payout_amount,
                "moisture": soil_moisture,
                "temperature": temperature,
                "crop": policy["crop"] if policy else "Crop",
                "state": policy["state"] if policy else "State",
                "language_code": policy.get("language_code", "ta-IN") if policy else "ta-IN",
                "weather_corroboration": weather_corrob,
                "evidence_package": evidence_package
            }

        # No trigger: nominal report
        return {
            "triggered": False,
            "status": "NORMAL_CONDITIONS_VERIFIED",
            "message": "Telemetry cryptographically authentic; all parameters within contractual bounds.",
            "weather_corroboration": weather_corrob,
            "evidence_package": evidence_package
        }

# Global insurance engine singleton
engine = ParametricInsuranceEngine()
