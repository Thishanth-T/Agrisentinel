import time
import requests
from crypto_service import generate_keypair, sign_payload

API_URL = "http://127.0.0.1:8000/api/telemetry"

class SensorNode:
    def __init__(self, node_id: str, plot_id: str):
        self.node_id = node_id
        self.plot_id = plot_id
        self.private_key, self.public_key = generate_keypair()

    def transmit(self, soil_moisture: float, temperature: float, rainfall_mm: float, tamper_sig: bool = False):
        telemetry_data = {
            "plot_id": self.plot_id,
            "soil_moisture": float(soil_moisture),
            "temperature": float(temperature),
            "rainfall_mm": float(rainfall_mm),
            "timestamp": time.time()
        }
        signature = sign_payload(self.private_key, telemetry_data)
        if tamper_sig:
            signature = signature[:-4] + "0000"
        payload = {
            "node_id": self.node_id,
            "public_key": self.public_key,
            "signature": signature,
            "telemetry": telemetry_data
        }
        try:
            res = requests.post(API_URL, json=payload, timeout=3)
            return res.status_code, res.json()
        except Exception as e:
            return 500, {"error": str(e)}

def run_simulation_cycle():
    nodes = [SensorNode(f"node_{i}", f"plot_{i}") for i in range(1, 10)]
    for node in nodes:
        status, resp = node.transmit(soil_moisture=31.0, temperature=28.0, rainfall_mm=4.0)
    drought_node = nodes[0]
    status, resp = drought_node.transmit(soil_moisture=12.5, temperature=39.5, rainfall_mm=0.0)
    tamper_node = nodes[1]
    status_bad, resp_bad = tamper_node.transmit(soil_moisture=10.0, temperature=40.0, rainfall_mm=0.0, tamper_sig=True)

if __name__ == "__main__":
    run_simulation_cycle()
