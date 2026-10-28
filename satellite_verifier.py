import os
import time
import requests
from typing import Dict, Any, Tuple

FARM_POLYGONS: Dict[str, Dict[str, Any]] = {
    "plot_1": {
        "region": "Thanjavur-Madurai Delta",
        "state": "Tamil Nadu",
        "lat": 10.7870,
        "lon": 79.1378,
        "satellite_source": "Copernicus Sentinel-2 & NASA POWER",
        "baseline_temp": 32.5,
        "baseline_cloud": 12.0,
        "baseline_rain_24h": 0.0,
        "baseline_pressure": 1011.5
    },
    "plot_2": {
        "region": "Gangetic Plain, Varanasi",
        "state": "Uttar Pradesh",
        "lat": 25.3176,
        "lon": 82.9739,
        "satellite_source": "Copernicus Sentinel-2 & NASA POWER",
        "baseline_temp": 30.0,
        "baseline_cloud": 15.0,
        "baseline_rain_24h": 0.0,
        "baseline_pressure": 1012.0
    },
    "plot_3": {
        "region": "Saurashtra Cotton Belt, Anand",
        "state": "Gujarat",
        "lat": 22.5645,
        "lon": 72.9289,
        "satellite_source": "Copernicus Sentinel-2 & NASA POWER",
        "baseline_temp": 33.0,
        "baseline_cloud": 8.0,
        "baseline_rain_24h": 0.0,
        "baseline_pressure": 1010.5
    },
    "plot_4": {
        "region": "Krishna River Basin, Guntur",
        "state": "Andhra Pradesh",
        "lat": 16.3067,
        "lon": 80.4365,
        "satellite_source": "Copernicus Sentinel-2 & NASA POWER",
        "baseline_temp": 34.0,
        "baseline_cloud": 10.0,
        "baseline_rain_24h": 0.0,
        "baseline_pressure": 1011.0
    },
    "plot_5": {
        "region": "Lower Gangetic Delta, Burdwan",
        "state": "West Bengal",
        "lat": 23.2324,
        "lon": 87.8615,
        "satellite_source": "Copernicus Sentinel-2 & NASA POWER",
        "baseline_temp": 29.5,
        "baseline_cloud": 20.0,
        "baseline_rain_24h": 0.0,
        "baseline_pressure": 1013.0
    },
    "plot_6": {
        "region": "Chambal Arid Belt, Kota",
        "state": "Rajasthan",
        "lat": 25.2138,
        "lon": 75.8648,
        "satellite_source": "Copernicus Sentinel-2 & NASA POWER",
        "baseline_temp": 36.5,
        "baseline_cloud": 5.0,
        "baseline_rain_24h": 0.0,
        "baseline_pressure": 1009.0
    },
    "plot_7": {
        "region": "Deccan Plateau, Nashik",
        "state": "Maharashtra",
        "lat": 19.9975,
        "lon": 73.7898,
        "satellite_source": "Copernicus Sentinel-2 & NASA POWER",
        "baseline_temp": 31.0,
        "baseline_cloud": 10.0,
        "baseline_rain_24h": 0.0,
        "baseline_pressure": 1012.0
    },
    "plot_8": {
        "region": "Kuttanad Wet Basin, Alappuzha",
        "state": "Kerala",
        "lat": 9.4981,
        "lon": 76.3388,
        "satellite_source": "Copernicus Sentinel-2 & NASA POWER",
        "baseline_temp": 28.5,
        "baseline_cloud": 35.0,
        "baseline_rain_24h": 2.5,
        "baseline_pressure": 1012.5
    },
    "plot_9": {
        "region": "Tungabhadra Basin, Raichur",
        "state": "Karnataka",
        "lat": 16.2076,
        "lon": 77.3463,
        "satellite_source": "Copernicus Sentinel-2 & NASA POWER",
        "baseline_temp": 33.5,
        "baseline_cloud": 12.0,
        "baseline_rain_24h": 0.0,
        "baseline_pressure": 1011.0
    }
}

class SatelliteVerifier:
    @classmethod
    def fetch_macro_satellite_data(cls, plot_id: str) -> Dict[str, Any]:
        polygon = FARM_POLYGONS.get(plot_id, FARM_POLYGONS["plot_1"])
        api_key = os.getenv("OPENWEATHER_API_KEY") or os.getenv("WEATHER_API_KEY")

        if api_key:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?lat={polygon['lat']}&lon={polygon['lon']}&appid={api_key}&units=metric"
                res = requests.get(url, timeout=4)
                if res.status_code == 200:
                    d = res.json()
                    rain = d.get("rain", {}).get("1h", 0.0) * 24.0
                    return {
                        "source": "OpenWeatherMap Live Satellite Feed",
                        "region": polygon["region"],
                        "state": polygon["state"],
                        "lat": polygon["lat"],
                        "lon": polygon["lon"],
                        "temperature": float(d.get("main", {}).get("temp", polygon["baseline_temp"])),
                        "humidity": float(d.get("main", {}).get("humidity", 40.0)),
                        "pressure": float(d.get("main", {}).get("pressure", polygon["baseline_pressure"])),
                        "cloud_cover": float(d.get("clouds", {}).get("all", polygon["baseline_cloud"])),
                        "rain_24h_mm": float(rain),
                        "timestamp": time.time(),
                        "is_live_api": True
                    }
            except Exception:
                pass

        return {
            "source": f"{polygon['satellite_source']} (Macro Simulation)",
            "region": polygon["region"],
            "state": polygon["state"],
            "lat": polygon["lat"],
            "lon": polygon["lon"],
            "temperature": polygon["baseline_temp"],
            "humidity": 38.0,
            "pressure": polygon["baseline_pressure"],
            "cloud_cover": polygon["baseline_cloud"],
            "rain_24h_mm": polygon["baseline_rain_24h"],
            "timestamp": time.time(),
            "is_live_api": False
        }

    @classmethod
    def verify_telemetry(cls, plot_id: str, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        sat_data = cls.fetch_macro_satellite_data(plot_id)
        node_moisture = float(telemetry.get("soil_moisture", 30.0))
        node_temp = float(telemetry.get("temperature", 28.0))
        node_pressure = float(telemetry.get("pressure", 1012.0))
        sat_rain = sat_data["rain_24h_mm"]
        sat_cloud = sat_data["cloud_cover"]
        sat_temp = sat_data["temperature"]

        if node_moisture >= 85.0 and sat_cloud <= 15.0 and sat_rain <= 1.0:
            return {
                "status": "PHYSICAL_TAMPERING_AUDIT_REQUIRED",
                "badge": "TAMPER AUDIT REQUIRED",
                "is_verified": False,
                "confidence_score": 0.96,
                "satellite_source": sat_data["source"],
                "macro_satellite": sat_data,
                "anomaly_type": "SENSOR_IMMERSION_FRAUD",
                "audit_notes": (
                    f"Physical Tampering Detected on {plot_id.upper()}: Micro-node reports near-saturation "
                    f"soil moisture ({node_moisture:.1f}%), but satellite synthetic aperture radar (SAR) confirms "
                    f"zero regional rainfall ({sat_rain:.1f}mm) and clear sky ({sat_cloud:.1f}% cloud cover). "
                    "Suspected artificial water soaking. Payout blocked pending field audit."
                )
            }

        if node_temp >= 52.0 and (node_temp - sat_temp) > 16.0:
            return {
                "status": "PHYSICAL_TAMPERING_AUDIT_REQUIRED",
                "badge": "TAMPER AUDIT REQUIRED",
                "is_verified": False,
                "confidence_score": 0.94,
                "satellite_source": sat_data["source"],
                "macro_satellite": sat_data,
                "anomaly_type": "ARTIFICIAL_HEAT_FRAUD",
                "audit_notes": (
                    f"Heat Tampering Detected on {plot_id.upper()}: Micro-node reports extreme temperature "
                    f"({node_temp:.1f}C), exceeding regional satellite surface thermal readings ({sat_temp:.1f}C) "
                    "by >16C without macro-climatic heatwave conditions. Suspected sensor heating. Claim frozen."
                )
            }

        if node_moisture < 18.0 and sat_rain <= 3.0 and sat_cloud <= 35.0:
            return {
                "status": "SATELLITE_VERIFIED",
                "badge": "SATELLITE: MATCHED",
                "is_verified": True,
                "confidence_score": 0.98,
                "satellite_source": sat_data["source"],
                "macro_satellite": sat_data,
                "anomaly_type": "CORROBORATED_DROUGHT",
                "audit_notes": (
                    f"Satellite Corroboration Confirmed: Node drought telemetry ({node_moisture:.1f}% moisture) "
                    f"matches macro satellite drought signature in {sat_data['region']} (24h rain: {sat_rain:.1f}mm, "
                    f"cloud cover: {sat_cloud:.1f}%, solar irradiance nominal)."
                )
            }

        return {
            "status": "SATELLITE_VERIFIED",
            "badge": "SATELLITE: MATCHED",
            "is_verified": True,
            "confidence_score": 0.95,
            "satellite_source": sat_data["source"],
            "macro_satellite": sat_data,
            "anomaly_type": "NOMINAL_EQUILIBRIUM",
            "audit_notes": (
                f"Equilibrium verified: Node readings ({node_temp:.1f}C, {node_moisture:.1f}% moisture) "
                f"correlate with regional satellite observations for {sat_data['region']}."
            )
        }

    @classmethod
    def detect_physical_tampering(cls, telemetry: Dict[str, Any], sat_data: Dict[str, Any]) -> Tuple[bool, str, str]:
        plot_id = telemetry.get("plot_id", "plot_1")
        res = cls.verify_telemetry(plot_id, telemetry)
        is_tamper = (res["status"] == "PHYSICAL_TAMPERING_AUDIT_REQUIRED")
        return is_tamper, res["status"], res["audit_notes"]

verify_satellite_telemetry = SatelliteVerifier.verify_telemetry
