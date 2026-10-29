"""
AgriSentinel Device Simulator
=============================
Standalone Python simulation client mimicking 9 on-farm IoT edge nodes.
Uses provisioned test private keys from farm_registry.py to generate valid
SECP256k1 signed telemetry packets, as well as deliberate tamper & replay packets.
"""

import time
import requests
from typing import Dict, Any, Tuple

from farm_registry import (
    FARM_PROFILES,
    DEVICE_REGISTRY,
    SIMULATOR_TEST_PRIVATE_KEYS,
    get_farm_profile
)
from crypto_engine import CryptoEngine

API_URL = "http://127.0.0.1:8000/api/telemetry"

class SimulatedSensorNode:
    def __init__(self, node_id: str, plot_id: str):
        self.node_id = node_id
        self.plot_id = plot_id
        self.private_key = SIMULATOR_TEST_PRIVATE_KEYS.get(node_id)
        if not self.private_key:
            raise ValueError(f"No test private key found for {node_id}")

    def transmit(
        self,
        soil_moisture: float,
        temperature: float,
        rainfall_mm: float = 0.0,
        humidity: float = 45.0,
        pressure: float = 1012.0,
        tamper_sig: bool = False,
        custom_timestamp: float = None
    ) -> Tuple[int, Dict[str, Any]]:
        telemetry_data = {
            "plot_id": self.plot_id,
            "timestamp": custom_timestamp if custom_timestamp is not None else time.time(),
            "temperature": float(temperature),
            "humidity": float(humidity),
            "pressure": float(pressure),
            "soil_moisture": float(soil_moisture),
            "rainfall_mm": float(rainfall_mm)
        }

        # Sign using local test key
        signature = CryptoEngine.sign_payload(self.private_key, telemetry_data)

        if tamper_sig:
            signature = signature[:-8] + "0000dead"

        payload = {
            "node_id": self.node_id,
            "plot_id": self.plot_id,
            "signature": signature,
            "telemetry": telemetry_data
        }

        try:
            res = requests.post(API_URL, json=payload, timeout=3.5)
            return res.status_code, res.json()
        except Exception as e:
            return 500, {"error": str(e)}

def run_simulation_cycle():
    print("Initializing AgriSentinel 9-Node Telemetry Ingestion Cycle...")
    nodes = [SimulatedSensorNode(f"node_{i}", f"plot_{i}") for i in range(1, 10)]

    for node in nodes:
        status, resp = node.transmit(soil_moisture=31.0, temperature=28.5, rainfall_mm=0.0)
        print(f"[{node.node_id} -> {node.plot_id}] Nominal: HTTP {status} | Status: {resp.get('status')}")

    # Test Drought Trigger on Plot 1
    drought_node = nodes[0]
    status, resp = drought_node.transmit(soil_moisture=11.5, temperature=42.0, rainfall_mm=0.0)
    print(f"\n[DROUGHT TEST: {drought_node.node_id}] HTTP {status} | {resp.get('status')} | Triggered: {resp.get('evaluation', {}).get('triggered')}")

    # Test Tampered Signature Rejection on Plot 2
    tamper_node = nodes[1]
    status_bad, resp_bad = tamper_node.transmit(soil_moisture=10.0, temperature=40.0, tamper_sig=True)
    print(f"\n[TAMPER TEST: {tamper_node.node_id}] HTTP {status_bad} | Expected 403 Forbidden | Response: {resp_bad}")

if __name__ == "__main__":
    run_simulation_cycle()
