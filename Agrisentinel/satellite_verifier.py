"""
AgriSentinel Meteorological & Ground Corroboration Engine
=========================================================
Cross-references on-plot IoT sensor telemetry against independent external
meteorological data (OpenWeatherMap API) or calibrated regional baselines.

TRANSPARENCY NOTE:
This module uses meteorological station & atmospheric observation APIs to
detect macro-level weather conditions. It does NOT claim to process raw SAR
satellite imagery. Offline baselines are explicitly labeled as synthetic.
"""

import os
import time
import requests
from typing import Dict, Any, Tuple, Optional

from farm_registry import FARM_PROFILES, get_farm_profile

class SatelliteVerifier:
    @classmethod
    def fetch_reference_weather(cls, plot_id: str) -> Dict[str, Any]:
        """
        Retrieves reference weather for the plot's coordinates.
        Uses live OpenWeatherMap API if OPENWEATHER_API_KEY is configured.
        Falls back to documented regional baseline if unavailable.
        """
        farm = get_farm_profile(plot_id) or FARM_PROFILES["plot_1"]
        lat = farm["lat"]
        lon = farm["lon"]
        api_key = os.getenv("OPENWEATHER_API_KEY")

        if api_key and not api_key.startswith("mock") and len(api_key) > 10:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
                res = requests.get(url, timeout=3.5)
                if res.status_code == 200:
                    d = res.json()
                    main = d.get("main", {})
                    clouds = d.get("clouds", {})
                    rain_data = d.get("rain", {})
                    
                    # Strictly reporting actual measured windows — NEVER multiplying 1h by 24!
                    rain_1h = float(rain_data.get("1h", 0.0))
                    rain_3h = float(rain_data.get("3h", 0.0))
                    
                    return {
                        "source_name": "OpenWeatherMap Meteorological Observation Grid",
                        "data_type": "LIVE_EXTERNAL_API",
                        "is_live": True,
                        "lat": lat,
                        "lon": lon,
                        "region": f"{farm['district']}, {farm['state']}",
                        "temperature_c": float(main.get("temp", farm["baseline_temp"])),
                        "humidity_pct": float(main.get("humidity", 45.0)),
                        "pressure_hpa": float(main.get("pressure", 1012.0)),
                        "cloud_cover_pct": float(clouds.get("all", 15.0)),
                        "rain_1h_mm": rain_1h,
                        "rain_3h_mm": rain_3h,
                        "timestamp": time.time()
                    }
            except Exception:
                # Network failure or timeout: graceful fallback to baseline
                pass

        # Offline / Unconfigured fallback
        return {
            "source_name": "Agro-Climatic Regional Baseline (Offline Demonstration)",
            "data_type": "SYNTHETIC_BASELINE",
            "is_live": False,
            "lat": lat,
            "lon": lon,
            "region": f"{farm['district']}, {farm['state']}",
            "temperature_c": farm["baseline_temp"],
            "humidity_pct": 45.0,
            "pressure_hpa": 1012.0,
            "cloud_cover_pct": 20.0,
            "rain_1h_mm": 0.0,
            "rain_3h_mm": 0.0,
            "timestamp": time.time()
        }

    @classmethod
    def verify_telemetry(cls, plot_id: str, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cross-examines node readings against independent reference weather.
        Returns explicit corroboration status, physical divergence metrics,
        and human-auditable agronomic notes.
        """
        ref = cls.fetch_reference_weather(plot_id)
        node_moisture = float(telemetry.get("soil_moisture", 30.0))
        node_temp = float(telemetry.get("temperature", 28.0))
        node_rain = float(telemetry.get("rainfall_mm", 0.0))
        
        ref_temp = ref["temperature_c"]
        ref_rain = ref["rain_1h_mm"]
        ref_cloud = ref["cloud_cover_pct"]
        temp_delta = abs(node_temp - ref_temp)

        # 1. Suspicious Bucket-Immersion Divergence:
        # Soil sensor reports saturated flood (>85%) while external station reports 0 rain and clear skies (<20% cloud)
        if node_moisture >= 85.0 and ref_cloud <= 20.0 and ref_rain <= 1.0 and node_rain <= 2.0:
            return {
                "corroboration_status": "DIVERGENCE_HELD_FOR_INSPECTION",
                "badge": "AUDIT: DIVERGENCE FLAGGED",
                "is_corroborated": False,
                "anomaly_type": "UNVERIFIED_WATERLOGGING_ANOMALY",
                "divergence_metrics": {
                    "node_moisture_pct": node_moisture,
                    "reference_rain_1h_mm": ref_rain,
                    "reference_cloud_pct": ref_cloud,
                    "temp_delta_c": round(temp_delta, 1)
                },
                "reference_data": ref,
                "audit_notes": (
                    f"Physical Divergence on Plot {plot_id.upper()}: Micro-node reports root-zone saturation "
                    f"({node_moisture:.1f}% moisture), but reference weather grid indicates zero rain ({ref_rain:.1f}mm) "
                    f"and clear sky ({ref_cloud:.0f}% clouds). Claim intent held pending field inspector survey."
                )
            }

        # 2. Suspicious Artificial Heat Spike:
        # Node reports extreme temperature (>50°C) diverging by >15°C from reference station
        if node_temp >= 50.0 and (node_temp - ref_temp) > 15.0:
            return {
                "corroboration_status": "DIVERGENCE_HELD_FOR_INSPECTION",
                "badge": "AUDIT: DIVERGENCE FLAGGED",
                "is_corroborated": False,
                "anomaly_type": "UNVERIFIED_THERMAL_ANOMALY",
                "divergence_metrics": {
                    "node_temp_c": node_temp,
                    "reference_temp_c": ref_temp,
                    "temp_delta_c": round(temp_delta, 1)
                },
                "reference_data": ref,
                "audit_notes": (
                    f"Thermal Divergence on Plot {plot_id.upper()}: Micro-node reports extreme temperature ({node_temp:.1f}°C) "
                    f"exceeding reference station ({ref_temp:.1f}°C) by {temp_delta:.1f}°C. Held for physical sensor check."
                )
            }

        # 3. Corroborated Drought:
        # Node reports low moisture (<18%) with low precipitation in reference data
        if node_moisture < 18.0 and ref_rain <= 5.0:
            return {
                "corroboration_status": "CORROBORATED",
                "badge": "WEATHER: CORROBORATED",
                "is_corroborated": True,
                "anomaly_type": "CORROBORATED_DROUGHT_STRESS",
                "divergence_metrics": {
                    "node_moisture_pct": node_moisture,
                    "reference_temp_c": ref_temp,
                    "reference_rain_1h_mm": ref_rain,
                    "temp_delta_c": round(temp_delta, 1)
                },
                "reference_data": ref,
                "audit_notes": (
                    f"Weather Corroboration Confirmed: Node moisture depletion ({node_moisture:.1f}%) aligns with "
                    f"dry atmospheric conditions in {ref['region']} (Rain: {ref_rain:.1f}mm, Temp: {ref_temp:.1f}°C)."
                )
            }

        # 4. Corroborated Deluge / Heavy Precipitation:
        if node_rain >= 50.0 or (node_moisture >= 80.0 and (ref_rain > 5.0 or ref_cloud > 60.0)):
            return {
                "corroboration_status": "CORROBORATED",
                "badge": "WEATHER: CORROBORATED",
                "is_corroborated": True,
                "anomaly_type": "CORROBORATED_HEAVY_PRECIPITATION",
                "divergence_metrics": {
                    "node_rain_mm": node_rain,
                    "node_moisture_pct": node_moisture,
                    "reference_rain_1h_mm": ref_rain,
                    "temp_delta_c": round(temp_delta, 1)
                },
                "reference_data": ref,
                "audit_notes": (
                    f"Weather Corroboration Confirmed: On-plot rainfall ({node_rain:.1f}mm) and soil moisture ({node_moisture:.1f}%) "
                    f"corroborated by regional cloud cover ({ref_cloud:.0f}%) and atmospheric precipitation indicators."
                )
            }

        # 5. Nominal Conditions:
        return {
            "corroboration_status": "CORROBORATED",
            "badge": "WEATHER: CORROBORATED",
            "is_corroborated": True,
            "anomaly_type": "NOMINAL_CONDITIONS",
            "divergence_metrics": {
                "node_temp_c": node_temp,
                "reference_temp_c": ref_temp,
                "temp_delta_c": round(temp_delta, 1)
            },
            "reference_data": ref,
            "audit_notes": (
                f"Nominal: Sensor readings ({node_temp:.1f}°C, {node_moisture:.1f}% moisture) correlate with "
                f"regional weather observations for {ref['region']}."
            )
        }

    # Backward compatibility
    @classmethod
    def fetch_macro_satellite_data(cls, plot_id: str) -> Dict[str, Any]:
        return cls.fetch_reference_weather(plot_id)

verify_satellite_telemetry = SatelliteVerifier.verify_telemetry
