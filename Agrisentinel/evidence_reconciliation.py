"""
AgriSentinel Adaptive Device Trust & Spatial-Temporal Evidence Reconciliation
=============================================================================
Core Differentiator: Transforms raw sensory data into high-integrity, uncertainty-aware evidence.
Evaluates:
- Statistical sensor sanity & historical consistency
- Thermodynamic plausibility (Vapor Pressure Deficit, thermal damping)
- Spatial autocorrelation against neighboring farm nodes
- Macro-meteorological corroboration vs external synthetic aperture radar / weather grids
- Produces deterministic, explainable confidence assessments:
  CONSISTENT | LOCALISED_EVENT_POSSIBLE | CONFLICTING_EVIDENCE | INSUFFICIENT_DATA | DEVICE_RELIABILITY_CONCERN
"""

import time
import math
from typing import Dict, List, Any, Optional, Tuple

from farm_registry import FARM_PROFILES, get_farm_profile
from database import db

class EvidenceReconciliationEngine:
    @staticmethod
    def calculate_device_trust_score(
        plot_id: str,
        current_telemetry: Dict[str, Any],
        historical_telemetry: List[Dict[str, Any]],
        device_state: Dict[str, Any]
    ) -> Tuple[float, str, List[str]]:
        """
        Calculates a deterministic reliability score (0.0 to 1.0) and human-readable explanation.
        Factors:
        - Active fault injection state or lifecycle state
        - Battery headroom (> 20% = healthy)
        - Historical frozen sensor detection (zero variance across last 3+ samples)
        - Sensor drift and sudden implausible telemetry jumps
        - Micro-climatic thermodynamic sanity
        """
        score = 1.0
        reasons = []

        moisture = float(current_telemetry.get("soil_moisture", 30.0))
        temp = float(current_telemetry.get("temperature", 28.0))
        humidity = float(current_telemetry.get("humidity", 45.0))
        battery = float(device_state.get("battery_level", 95.0))
        active_fault = device_state.get("active_fault", "NONE")
        lifecycle = device_state.get("lifecycle_state", "ONLINE")

        # 0. Active hardware transducer fault detected
        if active_fault in ("STUCK", "DISCONNECT"):
            score -= 0.55
            reasons.append(f"Hardware transducer fault active: {active_fault}")
        elif active_fault in ("DRIFT", "SPIKE"):
            score -= 0.45
            reasons.append(f"Sensor calibration anomaly active: {active_fault}")
        elif lifecycle == "SENSOR_FAULT":
            score -= 0.50
            reasons.append("Node in SENSOR_FAULT state")

        # 1. Battery power adequacy
        if battery < 15.0:
            score -= 0.35
            reasons.append(f"Low battery supply ({battery:.1f}%): sensor voltage rail instability risk")
        elif battery < 30.0:
            score -= 0.10
            reasons.append(f"Sub-optimal battery level ({battery:.1f}%)")

        # 2. Frozen sensor detection across recent history (historical telemetry from SQLite)
        if historical_telemetry and len(historical_telemetry) >= 3:
            recent_moistures = [float(p.get("soil_moisture", 0.0)) for p in historical_telemetry[:5]]
            recent_moistures.insert(0, moisture)
            # If 3 or more consecutive identical readings with 0 variance
            if len(recent_moistures) >= 3 and len(set(recent_moistures[:4])) == 1:
                score -= 0.45
                reasons.append("Transducer output frozen: zero variance over recent readings (ADC bridge latch or stuck sensor)")

            # Check for sudden physical step jumps (>35% moisture jump in single interval without rain)
            if len(historical_telemetry) >= 1:
                prev_m = float(historical_telemetry[0].get("soil_moisture", moisture))
                rain = float(current_telemetry.get("rainfall_mm", 0.0))
                if abs(moisture - prev_m) > 35.0 and rain < 5.0:
                    score -= 0.35
                    reasons.append(f"Physically impossible moisture jump ({prev_m:.1f}% -> {moisture:.1f}%) without precipitation")

        # 3. Micro-climatic Thermodynamic sanity
        if temp > 40.0 and humidity > 85.0:
            score -= 0.25
            reasons.append("Implausible atmospheric combination: extreme heat (>40°C) with tropical saturation (>85% RH)")

        score = max(0.0, min(1.0, score))
        status_label = "RELIABLE" if score >= 0.8 else "DEGRADED" if score >= 0.5 else "CRITICAL"
        return score, status_label, reasons

    @staticmethod
    def reconcile_spatial_temporal_evidence(
        target_plot_id: str,
        target_telemetry: Dict[str, Any],
        neighbor_telemetries: List[Dict[str, Any]],
        external_weather: Optional[Dict[str, Any]],
        device_trust_score: float
    ) -> Dict[str, Any]:
        """
        Compares fence-line plot telemetry against macro-weather and neighboring agricultural sectors.
        Recognizes hyper-local phenomena (e.g. cloudburst, micro-drought) without dismissing
        divergent sensor reports as malicious fraud.
        """
        plot_moisture = float(target_telemetry.get("soil_moisture", 30.0))
        plot_rain = float(target_telemetry.get("rainfall_mm", 0.0))
        plot_temp = float(target_telemetry.get("temperature", 28.0))

        profile = get_farm_profile(target_plot_id)
        drought_threshold = float(profile["moisture_drought_threshold"]) if profile else 18.0
        flood_threshold = float(profile["rainfall_flood_threshold_mm"]) if profile else 70.0

        supporting_evidence = []
        conflicting_evidence = []
        uncertainty_factors = []

        # Compare with external meteorological observation grid
        ext_rain = float(external_weather.get("rain_1h_mm", 0.0)) if external_weather else 0.0
        ext_temp = float(external_weather.get("temperature_c", 28.0)) if external_weather else 28.0

        # Scenario A: Localized Cloudburst / Deluge Detection
        if plot_rain >= flood_threshold:
            supporting_evidence.append(f"On-plot optical rain gauge registered deluge: {plot_rain:.1f} mm >= threshold {flood_threshold} mm")
            if ext_rain < 5.0:
                conflicting_evidence.append(f"District IMD station (15km radius) recorded minimal rain: {ext_rain:.1f} mm")
                uncertainty_factors.append("Spatial variance: isolated convective convective cell vs localized micro-storm")
                outcome = "LOCALISED_EVENT_POSSIBLE"
                explanation = "Severe localized convective cloudburst detected on farm perimeter. Station 15km away missed the localized precipitation cell."
            else:
                supporting_evidence.append(f"Regional IMD observation corroborates heavy precipitation: {ext_rain:.1f} mm")
                outcome = "CONSISTENT"
                explanation = "Regional deluge corroborated by both on-plot telemetry and external meteorological stations."

        # Scenario B: Severe Soil Moisture Drought Desiccation
        elif plot_moisture <= drought_threshold:
            supporting_evidence.append(f"Capacitive subsurface moisture depleted: {plot_moisture:.1f}% <= threshold {drought_threshold}%")
            if ext_temp >= 35.0 or ext_rain == 0.0:
                supporting_evidence.append(f"External weather grid confirms hot, dry atmospheric conditions: {ext_temp:.1f}°C, 0mm rain")
                outcome = "CONSISTENT"
                explanation = "Crop root-zone drought validated by persistent high ambient temperatures and absence of recent precipitation."
            else:
                conflicting_evidence.append(f"External weather shows mild temperatures ({ext_temp:.1f}°C) or recent rain ({ext_rain:.1f} mm)")
                uncertainty_factors.append("Soil drainage anomaly or local subsurface percolation differences")
                outcome = "LOCALISED_EVENT_POSSIBLE"
                explanation = "Localized soil water depletion observed despite moderate regional weather; potential high soil permeability or root uptake."

        # Scenario C: Nominal Conditions
        else:
            outcome = "CONSISTENT"
            explanation = "On-plot environmental telemetry is within contractual nominal agronomic operating parameters."

        # Incorporate Neighboring Farm Telemetry from SQLite
        if neighbor_telemetries:
            neighbor_rains = [float(n.get("rainfall_mm", 0.0)) for n in neighbor_telemetries]
            neighbor_moistures = [float(n.get("soil_moisture", 30.0)) for n in neighbor_telemetries]
            avg_neighbor_moisture = sum(neighbor_moistures) / len(neighbor_moistures)
            max_neighbor_rain = max(neighbor_rains) if neighbor_rains else 0.0

            if plot_rain >= flood_threshold and max_neighbor_rain < 5.0:
                uncertainty_factors.append(f"Neighboring farms ({len(neighbor_telemetries)} plots) received dry weather (max {max_neighbor_rain:.1f}mm); confirms hyper-local cloudburst")
            elif plot_moisture <= drought_threshold and avg_neighbor_moisture <= (drought_threshold + 5.0):
                supporting_evidence.append(f"Spatial autocorrelation: Neighboring plots also exhibit soil moisture depletion (avg {avg_neighbor_moisture:.1f}%)")

        # External weather transparency label
        if external_weather:
            ext_source = external_weather.get("source_name", "External Meteorological Source")
            ext_data_type = external_weather.get("data_type", "LIVE_API")
            if ext_data_type == "SYNTHETIC_BASELINE":
                uncertainty_factors.append(f"Weather reference is {ext_source} (offline simulation baseline, not live API)")

        # If device reliability is impaired, downgrade outcome
        if device_trust_score < 0.6:
            outcome = "DEVICE_RELIABILITY_CONCERN"
            explanation = f"Sensory readings compromised by low device trust score ({device_trust_score:.2f}). Technical inspection required before parametric settlement."

        return {
            "reconciliation_outcome": outcome,
            "explanation": explanation,
            "device_trust_score": round(device_trust_score, 2),
            "supporting_evidence": supporting_evidence,
            "conflicting_evidence": conflicting_evidence,
            "uncertainty_factors": uncertainty_factors,
            "evaluated_at": time.time()
        }

# Global reconciliation engine instance
evidence_engine = EvidenceReconciliationEngine()
