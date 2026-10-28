import time
import uuid
from typing import Dict, List, Any, Optional
from satellite_verifier import SatelliteVerifier

class ParametricInsuranceEngine:
    def __init__(self):
        self.tamper_blocked_count: int = 0
        self.policies: Dict[str, dict] = {
            "plot_1": {
                "plot_id": "plot_1",
                "grid_x": 0, "grid_y": 0,
                "farmer_name": "Arjun Patel",
                "phone": "+15550101",
                "crop": "Wheat",
                "state": "Tamil Nadu",
                "region": "Thanjavur Delta",
                "language_code": "ta-IN",
                "language_name": "Tamil",
                "sum_insured": 50000.0,
                "moisture_threshold": 18.0,
                "temp_threshold": 42.0,
                "flood_moisture_threshold": 88.0,
                "payout_ratio": 1.0,
                "active": True
            },
            "plot_2": {
                "plot_id": "plot_2",
                "grid_x": 1, "grid_y": 0,
                "farmer_name": "Priya Sharma",
                "phone": "+15550102",
                "crop": "Soybean",
                "state": "Uttar Pradesh",
                "region": "Varanasi Gangetic Plain",
                "language_code": "hi-IN",
                "language_name": "Hindi",
                "sum_insured": 65000.0,
                "moisture_threshold": 20.0,
                "temp_threshold": 40.0,
                "flood_moisture_threshold": 90.0,
                "payout_ratio": 1.0,
                "active": True
            },
            "plot_3": {
                "plot_id": "plot_3",
                "grid_x": 2, "grid_y": 0,
                "farmer_name": "Ramesh Gupta",
                "phone": "+15550103",
                "crop": "Cotton",
                "state": "Gujarat",
                "region": "Saurashtra Arid Basin",
                "language_code": "gu-IN",
                "language_name": "Gujarati",
                "sum_insured": 75000.0,
                "moisture_threshold": 16.0,
                "temp_threshold": 44.0,
                "flood_moisture_threshold": 88.0,
                "payout_ratio": 1.0,
                "active": True
            },
            "plot_4": {
                "plot_id": "plot_4",
                "grid_x": 0, "grid_y": 1,
                "farmer_name": "Sunita Verma",
                "phone": "+15550104",
                "crop": "Maize",
                "state": "Andhra Pradesh",
                "region": "Krishna River Delta",
                "language_code": "te-IN",
                "language_name": "Telugu",
                "sum_insured": 45000.0,
                "moisture_threshold": 19.0,
                "temp_threshold": 41.0,
                "flood_moisture_threshold": 89.0,
                "payout_ratio": 1.0,
                "active": True
            },
            "plot_5": {
                "plot_id": "plot_5",
                "grid_x": 1, "grid_y": 1,
                "farmer_name": "Devendra Rao",
                "phone": "+15550105",
                "crop": "Rice",
                "state": "West Bengal",
                "region": "Burdwan Paddy Plain",
                "language_code": "bn-IN",
                "language_name": "Bengali",
                "sum_insured": 80000.0,
                "moisture_threshold": 25.0,
                "temp_threshold": 39.0,
                "flood_moisture_threshold": 95.0,
                "payout_ratio": 1.0,
                "active": True
            },
            "plot_6": {
                "plot_id": "plot_6",
                "grid_x": 2, "grid_y": 1,
                "farmer_name": "Ananya Nair",
                "phone": "+15550106",
                "crop": "Millet",
                "state": "Rajasthan",
                "region": "Kota Arid Corridor",
                "language_code": "hi-IN",
                "language_name": "Hindi",
                "sum_insured": 40000.0,
                "moisture_threshold": 14.0,
                "temp_threshold": 45.0,
                "flood_moisture_threshold": 87.0,
                "payout_ratio": 1.0,
                "active": True
            },
            "plot_7": {
                "plot_id": "plot_7",
                "grid_x": 0, "grid_y": 2,
                "farmer_name": "Vijay Joshi",
                "phone": "+15550107",
                "crop": "Mustard",
                "state": "Maharashtra",
                "region": "Nashik Deccan Plateau",
                "language_code": "mr-IN",
                "language_name": "Marathi",
                "sum_insured": 55000.0,
                "moisture_threshold": 17.0,
                "temp_threshold": 42.0,
                "flood_moisture_threshold": 88.0,
                "payout_ratio": 1.0,
                "active": True
            },
            "plot_8": {
                "plot_id": "plot_8",
                "grid_x": 1, "grid_y": 2,
                "farmer_name": "Meera Sen",
                "phone": "+15550108",
                "crop": "Groundnut",
                "state": "Kerala",
                "region": "Alappuzha Lowland",
                "language_code": "ml-IN",
                "language_name": "Malayalam",
                "sum_insured": 60000.0,
                "moisture_threshold": 18.0,
                "temp_threshold": 43.0,
                "flood_moisture_threshold": 92.0,
                "payout_ratio": 1.0,
                "active": True
            },
            "plot_9": {
                "plot_id": "plot_9",
                "grid_x": 2, "grid_y": 2,
                "farmer_name": "Kiran Deshmukh",
                "phone": "+15550109",
                "crop": "Sorghum",
                "state": "Karnataka",
                "region": "Raichur Semi-Arid",
                "language_code": "kn-IN",
                "language_name": "Kannada",
                "sum_insured": 48000.0,
                "moisture_threshold": 15.0,
                "temp_threshold": 44.0,
                "flood_moisture_threshold": 88.0,
                "payout_ratio": 1.0,
                "active": True
            }
        }
        self.plot_telemetry: Dict[str, dict] = {}
        self.claims: List[dict] = []
        self.audit_log: List[dict] = []
        self.registered_nodes: Dict[str, str] = {}

        for pid, pol in self.policies.items():
            self.plot_telemetry[pid] = {
                "plot_id": pid,
                "soil_moisture": 32.0,
                "temperature": 28.5,
                "humidity": 45.0,
                "pressure": 1012.0,
                "rainfall_mm": 0.0,
                "status": "NORMAL",
                "crypto_status": "SECP256k1: PENDING",
                "satellite_status": "SATELLITE: SYNCHRONIZED",
                "last_updated": time.time()
            }

    def register_node(self, node_id: str, public_key_hex: str):
        self.registered_nodes[node_id] = public_key_hex

    def evaluate_telemetry(
        self,
        node_id: str,
        telemetry: Dict[str, Any],
        sig_valid: bool,
        sig_notes: str = ""
    ) -> Dict[str, Any]:
        plot_id = telemetry.get("plot_id", "plot_1")
        soil_moisture = float(telemetry.get("soil_moisture", 30.0))
        temperature = float(telemetry.get("temperature", 25.0))
        humidity = float(telemetry.get("humidity", 40.0))
        pressure = float(telemetry.get("pressure", 1012.0))
        rainfall_mm = float(telemetry.get("rainfall_mm", 0.0))
        now = time.time()

        sat_check = SatelliteVerifier.verify_telemetry(plot_id, telemetry)
        is_satellite_verified = sat_check.get("is_verified", True)

        self.plot_telemetry[plot_id] = {
            "plot_id": plot_id,
            "soil_moisture": soil_moisture,
            "temperature": temperature,
            "humidity": humidity,
            "pressure": pressure,
            "rainfall_mm": rainfall_mm,
            "status": "NORMAL",
            "crypto_status": "SECP256k1: VALID" if sig_valid else "SECP256k1: REJECTED",
            "satellite_status": sat_check.get("badge", "SATELLITE: MATCHED"),
            "satellite_data": sat_check.get("macro_satellite", {}),
            "last_updated": now
        }

        log_entry = {
            "log_id": str(uuid.uuid4())[:8],
            "timestamp": now,
            "node_id": node_id,
            "plot_id": plot_id,
            "sig_valid": sig_valid,
            "crypto_status": "SECP256k1: VALID" if sig_valid else "SECP256k1: REJECTED",
            "satellite_status": sat_check.get("status", "SATELLITE_VERIFIED"),
            "moisture": soil_moisture,
            "temperature": temperature,
            "notes": sig_notes or sat_check.get("audit_notes", "")
        }
        self.audit_log.insert(0, log_entry)
        if len(self.audit_log) > 250:
            self.audit_log.pop()

        if not sig_valid:
            self.tamper_blocked_count += 1
            self.plot_telemetry[plot_id]["status"] = "SIG_REJECTED"
            return {
                "triggered": False,
                "status": "REJECTED_CRYPTOGRAPHIC_FAILURE",
                "reason": "Cryptographic signature validation failure on SECP256k1 curve. Spoofed transmission blocked.",
                "satellite_verification": sat_check
            }

        if not is_satellite_verified:
            self.tamper_blocked_count += 1
            self.plot_telemetry[plot_id]["status"] = "PHYSICAL_TAMPER_HOLD"
            return {
                "triggered": False,
                "status": "HELD_PHYSICAL_TAMPERING_AUDIT",
                "reason": sat_check.get("audit_notes"),
                "anomaly_type": sat_check.get("anomaly_type"),
                "satellite_verification": sat_check
            }

        policy = self.policies.get(plot_id)
        if not policy or not policy["active"]:
            return {
                "triggered": False,
                "status": "POLICY_INACTIVE_OR_EXHAUSTED",
                "reason": "No active underwritten policy found for this plot.",
                "satellite_verification": sat_check
            }

        is_drought = soil_moisture < policy["moisture_threshold"]
        is_heatwave = temperature > policy["temp_threshold"]
        is_flood = soil_moisture >= policy.get("flood_moisture_threshold", 88.0) and sat_check.get("macro_satellite", {}).get("rain_24h_mm", 0.0) >= 50.0

        if is_drought or is_heatwave or is_flood:
            payout_amount = policy["sum_insured"] * policy["payout_ratio"]

            if is_drought:
                trigger_reason = f"Severe Drought Breach: {soil_moisture:.1f}% < Threshold {policy['moisture_threshold']:.1f}%"
                claim_type = "DROUGHT"
            elif is_heatwave:
                trigger_reason = f"Extreme Heatwave Breach: {temperature:.1f}C > Threshold {policy['temp_threshold']:.1f}C"
                claim_type = "HEATWAVE"
            else:
                trigger_reason = f"Macro Flood Breach: {soil_moisture:.1f}% with regional rainfall confirmation"
                claim_type = "FLOOD"

            claim = {
                "claim_id": f"CLM-{str(uuid.uuid4())[:8].upper()}",
                "plot_id": plot_id,
                "farmer_name": policy["farmer_name"],
                "phone": policy["phone"],
                "crop": policy["crop"],
                "state": policy["state"],
                "region": policy.get("region", ""),
                "language_name": policy["language_name"],
                "language_code": policy["language_code"],
                "payout_amount": payout_amount,
                "trigger_reason": trigger_reason,
                "claim_type": claim_type,
                "timestamp": now,
                "crypto_proof": "ECDSA-SECP256k1 Signed & Verified",
                "satellite_proof": sat_check.get("status", "SATELLITE_VERIFIED"),
                "status": "PAYOUT_EXECUTED"
            }
            self.claims.insert(0, claim)
            self.plot_telemetry[plot_id]["status"] = "PARAMETRIC_BREACH"
            policy["active"] = False

            return {
                "triggered": True,
                "status": "PARAMETRIC_BREACH_EXECUTED",
                "claim": claim,
                "farmer_phone": policy["phone"],
                "payout_amount": payout_amount,
                "moisture": soil_moisture,
                "temperature": temperature,
                "crop": policy["crop"],
                "state": policy["state"],
                "language_code": policy["language_code"],
                "satellite_verification": sat_check
            }

        return {
            "triggered": False,
            "status": "PARAMETERS_WITHIN_SAFETY_BOUNDARY",
            "reason": f"Sensor readings within nominal boundary (Moisture: {soil_moisture:.1f}%, Temp: {temperature:.1f}C)",
            "satellite_verification": sat_check
        }

engine = ParametricInsuranceEngine()
InsuranceEngine = ParametricInsuranceEngine

