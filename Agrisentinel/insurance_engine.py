"""
AgriSentinel Parametric Insurance Engine
========================================
Automated parametric breach evaluation, evidence package assembly, and
simulated claims workflow for Indian smallholder agriculture.

CLAIM WORKFLOW TRANSPARENCY:
1. Event Detection: Sensor breaches contractual policy parameter (e.g., soil drought or rainfall deluge).
2. Evidence Packaging: Binds cryptographically signed telemetry and independent weather corroboration.
3. Eligibility Decision: Computes indemnity benefit under parametric micro-rider schedule.
4. Simulated Settlement: Generates an auditable Claim Intent Record. Actual monetary disbursement
   requires insurer core banking / PMFBY DBT portal integration.
"""

import time
import uuid
from typing import Dict, List, Any, Optional

from farm_registry import FARM_PROFILES, get_farm_profile
from satellite_verifier import SatelliteVerifier

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
                "status": "NORMAL",
                "crypto_status": "SECP256k1: PENDING",
                "weather_corroboration_status": "SYNCHRONIZED",
                "last_updated": time.time(),
                "last_evidence_package": None
            }

    def reset_system(self):
        """Clean demonstration reset."""
        self.tamper_blocked_count = 0
        self.claims.clear()
        self.audit_log.clear()
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
        3. Parametric policy trigger check
        4. Simulated Claim Intent generation
        """
        plot_id = telemetry.get("plot_id", "plot_1")
        policy = self.policies.get(plot_id)
        now = time.time()

        soil_moisture = float(telemetry.get("soil_moisture", 30.0))
        temperature = float(telemetry.get("temperature", 28.0))
        humidity = float(telemetry.get("humidity", 45.0))
        pressure = float(telemetry.get("pressure", 1012.0))
        rainfall_mm = float(telemetry.get("rainfall_mm", 0.0))

        # Perform meteorological corroboration
        weather_check = SatelliteVerifier.verify_telemetry(plot_id, telemetry)
        is_corroborated = weather_check.get("is_corroborated", True)

        # Update telemetry state record
        current_status = "NORMAL"
        crypto_badge = "SECP256k1: VALID" if sig_valid else "SECP256k1: REJECTED"
        weather_badge = weather_check.get("badge", "WEATHER: CORROBORATED")

        # Create audit log entry
        log_entry = {
            "log_id": f"AUD-{str(uuid.uuid4())[:8].upper()}",
            "timestamp": now,
            "node_id": node_id,
            "plot_id": plot_id,
            "sig_valid": sig_valid,
            "crypto_status": crypto_badge,
            "weather_status": weather_badge,
            "soil_moisture": soil_moisture,
            "temperature": temperature,
            "rainfall_mm": rainfall_mm,
            "notes": sig_notes or weather_check.get("audit_notes", "")
        }
        self.audit_log.insert(0, log_entry)
        if len(self.audit_log) > 250:
            self.audit_log.pop()

        # STAGE 1: Cryptographic Failure Gate
        if not sig_valid:
            self.tamper_blocked_count += 1
            current_status = "SECURITY_REJECTED"
            self.plot_telemetry[plot_id]["status"] = current_status
            self.plot_telemetry[plot_id]["crypto_status"] = crypto_badge
            return {
                "triggered": False,
                "status": "REJECTED_CRYPTOGRAPHIC_FAILURE",
                "stage": "SECURITY_GATEWAY",
                "reason": sig_notes,
                "crypto_metadata": crypto_metadata,
                "weather_corroboration": weather_check
            }

        # STAGE 2: Physical / Meteorological Divergence Gate
        if not is_corroborated:
            self.tamper_blocked_count += 1
            current_status = "HELD_FOR_INSPECTION"
            self.plot_telemetry[plot_id]["status"] = current_status
            self.plot_telemetry[plot_id]["weather_corroboration_status"] = weather_badge
            return {
                "triggered": False,
                "status": "HELD_PHYSICAL_DIVERGENCE_AUDIT",
                "stage": "METEOROLOGICAL_CROSS_CHECK",
                "reason": weather_check.get("audit_notes"),
                "anomaly_type": weather_check.get("anomaly_type"),
                "weather_corroboration": weather_check
            }

        # STAGE 3: Policy Eligibility Check
        if not policy or not policy["active"]:
            return {
                "triggered": False,
                "status": "POLICY_INACTIVE_OR_EXHAUSTED",
                "stage": "CONTRACT_UNDERWRITING",
                "reason": "Policy is currently exhausted or inactive for this plot",
                "weather_corroboration": weather_check
            }

        # STAGE 4: Parametric Trigger Evaluation
        is_drought = soil_moisture < policy["moisture_drought_threshold"]
        is_heatwave = temperature > policy["temp_heatwave_threshold"]
        is_deluge = rainfall_mm >= policy["rainfall_flood_threshold_mm"]

        if is_drought or is_heatwave or is_deluge:
            payout_amount = policy["sum_insured_inr"] * policy["payout_ratio"]

            if is_drought:
                trigger_reason = f"Severe Soil Drought Breach: {soil_moisture:.1f}% < Threshold {policy['moisture_drought_threshold']:.1f}%"
                claim_type = "DROUGHT"
            elif is_heatwave:
                trigger_reason = f"Extreme Heatwave Thermal Breach: {temperature:.1f}°C > Threshold {policy['temp_heatwave_threshold']:.1f}°C"
                claim_type = "HEATWAVE"
            else:
                trigger_reason = f"Excessive Precipitation Breach: {rainfall_mm:.1f}mm >= Threshold {policy['rainfall_flood_threshold_mm']:.1f}mm"
                claim_type = "EXCESS_RAINFALL"

            # Assemble Tamper-Evident Evidence Package
            evidence_package = {
                "plot_id": plot_id,
                "node_id": node_id,
                "timestamp": now,
                "measurements": {
                    "soil_moisture_pct": soil_moisture,
                    "temperature_c": temperature,
                    "humidity_pct": humidity,
                    "pressure_hpa": pressure,
                    "rainfall_mm": rainfall_mm
                },
                "crypto_verification": {
                    "algorithm": "ECDSA-SECP256k1",
                    "registered_key": crypto_metadata.get("registered_key_used"),
                    "status": "VERIFIED_AUTHENTIC"
                },
                "weather_corroboration": {
                    "source": weather_check.get("reference_data", {}).get("source_name"),
                    "data_type": weather_check.get("reference_data", {}).get("data_type"),
                    "status": "CORROBORATED"
                }
            }

            # Generate Simulated Claim Intent
            claim_record = {
                "claim_id": f"CLM-{str(uuid.uuid4())[:8].upper()}",
                "plot_id": plot_id,
                "node_id": node_id,
                "farmer_name": policy["farmer_name"],
                "phone": policy["phone"],
                "crop": policy["crop"],
                "state": policy["state"],
                "district": policy["district"],
                "region": policy["region"],
                "language_name": policy["language_name"],
                "language_code": policy["language_code"],
                "payout_calculated_inr": payout_amount,
                "trigger_reason": trigger_reason,
                "claim_type": claim_type,
                "timestamp": now,
                "evidence_package": evidence_package,
                # Explicit claim state machine:
                "assessment_status": "CLAIM_INTENT_APPROVED_SIMULATED",
                "settlement_status": "DISBURSEMENT_NOT_CONNECTED (DEMO_MODE)",
                "settlement_notice": "Claim intent validated under parametric micro-rider terms. Monetary disbursement requires underwriter core banking integration."
            }

            self.claims.insert(0, claim_record)
            current_status = "PARAMETRIC_BREACH"
            policy["active"] = False

            self.plot_telemetry[plot_id].update({
                "soil_moisture": soil_moisture,
                "temperature": temperature,
                "humidity": humidity,
                "pressure": pressure,
                "rainfall_mm": rainfall_mm,
                "status": current_status,
                "crypto_status": crypto_badge,
                "weather_corroboration_status": weather_badge,
                "last_updated": now,
                "last_evidence_package": evidence_package
            })

            return {
                "triggered": True,
                "status": "PARAMETRIC_BREACH_CLAIM_INTENT_GENERATED",
                "stage": "CLAIM_INTENT_DISPATCHED",
                "claim": claim_record,
                "farmer_phone": policy["phone"],
                "payout_amount": payout_amount,
                "moisture": soil_moisture,
                "temperature": temperature,
                "crop": policy["crop"],
                "state": policy["state"],
                "language_code": policy["language_code"],
                "weather_corroboration": weather_check
            }

        # Parameters nominal
        self.plot_telemetry[plot_id].update({
            "soil_moisture": soil_moisture,
            "temperature": temperature,
            "humidity": humidity,
            "pressure": pressure,
            "rainfall_mm": rainfall_mm,
            "status": "NORMAL",
            "crypto_status": crypto_badge,
            "weather_corroboration_status": weather_badge,
            "last_updated": now
        })

        return {
            "triggered": False,
            "status": "PARAMETERS_WITHIN_SAFETY_BOUNDARY",
            "stage": "NOMINAL_MONITORING",
            "reason": f"Sensor readings within safe limits (Moisture: {soil_moisture:.1f}%, Temp: {temperature:.1f}°C, Rain: {rainfall_mm:.1f}mm)",
            "weather_corroboration": weather_check
        }

engine = ParametricInsuranceEngine()
InsuranceEngine = ParametricInsuranceEngine
