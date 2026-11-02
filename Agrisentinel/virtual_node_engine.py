"""
AgriSentinel Virtual IoT Node & Environmental Simulation Engine
==============================================================
Implements 9 independent virtual hardware nodes modeling:
- Physical thermodynamic & agro-meteorological evolution (rain, evapotranspiration)
- Power subsystem (battery mAh, solar charging based on cloud cover & time of day)
- Local packet queuing for realistic offline-first operation (with overflow policy)
- Sensor fault injection (stuck, drift, spike, disconnect)
- Monotonic sequence numbering & authentic SECP256k1 signing
- State lifecycle (INITIALISING, ONLINE, DEGRADED, OFFLINE, LOW_BATTERY, SENSOR_FAULT)
"""

import time
import math
import random
from typing import Dict, List, Any, Optional, Tuple

from farm_registry import (
    FARM_PROFILES,
    DEVICE_REGISTRY,
    SIMULATOR_TEST_PRIVATE_KEYS,
    get_farm_profile
)
from crypto_engine import CryptoEngine

class VirtualSensorFault:
    NONE = "NONE"
    STUCK = "STUCK"
    DRIFT = "DRIFT"
    SPIKE = "SPIKE"
    DISCONNECT = "DISCONNECT"

class VirtualNodeLifecycle:
    INITIALISING = "INITIALISING"
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"
    LOW_BATTERY = "LOW_BATTERY"
    SENSOR_FAULT = "SENSOR_FAULT"
    RECOVERING = "RECOVERING"

class VirtualEdgeNode:
    MAX_QUEUE_CAPACITY = 200  # Local non-volatile flash buffer limit (samples)

    def __init__(self, node_id: str, plot_id: str, seed: Optional[int] = None):
        self.node_id = node_id
        self.plot_id = plot_id
        self.profile = get_farm_profile(plot_id)
        if not self.profile:
            raise ValueError(f"Unknown farm profile: {plot_id}")

        self.rng = random.Random(seed if seed is not None else (int(time.time() * 1000) % 100000))
        self.private_key_hex = SIMULATOR_TEST_PRIVATE_KEYS.get(node_id)

        # Telemetry State Variables
        self.soil_moisture: float = float(self.profile["baseline_moisture"])
        self.temperature: float = float(self.profile["baseline_temp"])
        self.humidity: float = 45.0
        self.pressure: float = 1012.0
        self.rainfall_mm: float = 0.0

        # Subsystems
        self.sequence_number: int = 0
        self.battery_level: float = 98.5  # %
        self.battery_capacity_mah: float = 2600.0  # Standard 18650 Li-ion cell
        self.is_solar_charging: bool = True
        self.signal_strength_dbm: int = -68  # dBm GSM/4G RSSI
        self.lifecycle_state: str = VirtualNodeLifecycle.ONLINE
        self.is_connected: bool = True

        # Fault Injection State
        self.active_fault: str = VirtualSensorFault.NONE
        self.fault_target_sensor: str = "soil_moisture"
        self.stuck_value: Optional[float] = None
        self.drift_offset: float = 0.0

        # Local Flash Queue for Offline-First Storage
        self.local_packet_queue: List[Dict[str, Any]] = []
        self.dropped_packets_count: int = 0
        self.uptime_seconds: float = 0.0
        self.last_sample_time: float = time.time()

    def set_connectivity(self, online: bool):
        """Toggles network connectivity without interrupting sensor sampling."""
        self.is_connected = online
        if not online:
            self.lifecycle_state = VirtualNodeLifecycle.OFFLINE
        else:
            if self.lifecycle_state == VirtualNodeLifecycle.OFFLINE:
                self.lifecycle_state = VirtualNodeLifecycle.RECOVERING if self.local_packet_queue else VirtualNodeLifecycle.ONLINE

    def inject_fault(self, fault_type: str, target_sensor: str = "soil_moisture", value: Optional[float] = None):
        """Simulates physical hardware degradation or calibration decay."""
        self.active_fault = fault_type
        self.fault_target_sensor = target_sensor
        if fault_type == VirtualSensorFault.STUCK:
            self.stuck_value = value if value is not None else getattr(self, target_sensor)
        elif fault_type == VirtualSensorFault.DRIFT:
            self.drift_offset = value if value is not None else 8.5
        if fault_type != VirtualSensorFault.NONE:
            self.lifecycle_state = VirtualNodeLifecycle.SENSOR_FAULT
        else:
            self.stuck_value = None
            self.drift_offset = 0.0
            self.lifecycle_state = VirtualNodeLifecycle.ONLINE

    def step_environmental_physics(self, dt_minutes: float = 15.0, rain_influx_mm: float = 0.0, ambient_temp_override: Optional[float] = None):
        """
        Calculates physical soil hydrology and micro-climate evolution:
        - Rain events infiltrate soil with saturation threshold
        - Heat drives evapotranspiration, gradually desiccating soil
        - Battery drains linearly + charges via photovoltaic input
        """
        self.uptime_seconds += dt_minutes * 60.0

        # 1. Temperature & Humidity dynamics
        if ambient_temp_override is not None:
            self.temperature = ambient_temp_override
        else:
            # Subtle diurnal thermal oscillation
            hour = (time.time() / 3600.0) % 24
            diurnal_wave = math.sin((hour - 9) * math.pi / 12) * 4.0
            self.temperature = float(self.profile["baseline_temp"]) + diurnal_wave + self.rng.uniform(-0.4, 0.4)

        # Relative humidity inversely correlates with ambient thermal peak
        self.humidity = max(15.0, min(95.0, 75.0 - (self.temperature - 20.0) * 1.8 + self.rng.uniform(-2, 2)))

        # 2. Rainfall & Soil Moisture Infiltration
        self.rainfall_mm = max(0.0, rain_influx_mm)
        if self.rainfall_mm > 0.0:
            # Rapid water infiltration
            moisture_gain = self.rainfall_mm * 0.45
            self.soil_moisture = min(float(self.profile["moisture_saturation_threshold"]), self.soil_moisture + moisture_gain)
        else:
            # Gradual evapotranspiration loss proportional to heat
            drying_rate = max(0.05, (self.temperature / 30.0) * 0.12) * (dt_minutes / 15.0)
            self.soil_moisture = max(4.0, self.soil_moisture - drying_rate)

        # 3. Subsystem Health & Battery Physics
        sunlight_available = 6.0 <= ((time.time() / 3600.0) % 24) <= 18.0
        self.is_solar_charging = sunlight_available and self.rainfall_mm < 15.0
        if self.is_solar_charging:
            self.battery_level = min(100.0, self.battery_level + 0.15 * (dt_minutes / 15.0))
        else:
            # Baseline quiescent consumption
            drain = 0.08 * (dt_minutes / 15.0)
            if not self.is_connected:
                drain *= 1.3  # Retransmission scan overhead
            self.battery_level = max(0.0, self.battery_level - drain)

        # Update Lifecycle based on physical parameters
        if self.battery_level < 15.0:
            self.lifecycle_state = VirtualNodeLifecycle.LOW_BATTERY
        elif self.active_fault != VirtualSensorFault.NONE:
            self.lifecycle_state = VirtualNodeLifecycle.SENSOR_FAULT
        elif not self.is_connected:
            self.lifecycle_state = VirtualNodeLifecycle.OFFLINE
        elif self.local_packet_queue:
            self.lifecycle_state = VirtualNodeLifecycle.RECOVERING
        else:
            self.lifecycle_state = VirtualNodeLifecycle.ONLINE

    def sample_and_enqueue(self, custom_time: Optional[float] = None) -> Dict[str, Any]:
        """
        Samples physical transducers, applies any active hardware faults,
        increments the hardware monotonic sequence number, and signs with local test key.
        """
        self.sequence_number += 1
        pkt_time = custom_time if custom_time is not None else time.time()

        # Apply fault layer
        eff_moisture = self.soil_moisture
        eff_temp = self.temperature
        eff_rain = self.rainfall_mm

        if self.active_fault == VirtualSensorFault.STUCK and self.fault_target_sensor == "soil_moisture":
            eff_moisture = self.stuck_value if self.stuck_value is not None else 18.0
        elif self.active_fault == VirtualSensorFault.DRIFT and self.fault_target_sensor == "soil_moisture":
            eff_moisture = max(0.0, min(100.0, eff_moisture + self.drift_offset))
        elif self.active_fault == VirtualSensorFault.SPIKE and self.fault_target_sensor == "soil_moisture":
            eff_moisture = 99.8  # Implausible sudden flash flood spike
        elif self.active_fault == VirtualSensorFault.DISCONNECT:
            eff_moisture = 0.0  # Open circuit zero reading

        telemetry_data = {
            "plot_id": self.plot_id,
            "sequence": self.sequence_number,
            "timestamp": pkt_time,
            "temperature": round(eff_temp, 2),
            "humidity": round(self.humidity, 1),
            "pressure": round(self.pressure, 1),
            "soil_moisture": round(eff_moisture, 2),
            "rainfall_mm": round(eff_rain, 2),
            "battery_level": round(self.battery_level, 1)
        }

        # Authentic SECP256k1 signing
        signature = CryptoEngine.sign_payload(self.private_key_hex, telemetry_data)

        packet = {
            "node_id": self.node_id,
            "plot_id": self.plot_id,
            "signature": signature,
            "telemetry": telemetry_data,
            "enqueued_at": pkt_time,
            "is_buffered": not self.is_connected
        }

        # Enqueue with overflow management
        if len(self.local_packet_queue) >= self.MAX_QUEUE_CAPACITY:
            # FIFO drop policy: remove oldest unsent record to make room for newest reading
            self.local_packet_queue.pop(0)
            self.dropped_packets_count += 1

        self.local_packet_queue.append(packet)
        self.last_sample_time = pkt_time
        return packet

    def flush_backlog(self) -> List[Dict[str, Any]]:
        """Transfers local flash queue backlog upon network restoration."""
        if not self.is_connected:
            return []
        backlog = list(self.local_packet_queue)
        self.local_packet_queue.clear()
        self.lifecycle_state = VirtualNodeLifecycle.ONLINE
        return backlog


class FarmSimulationGrid:
    """Orchestrates all 9 pan-Indian farm nodes with deterministic multi-scenario replay."""

    def __init__(self, master_seed: int = 42):
        self.master_seed = master_seed
        self.nodes: Dict[str, VirtualEdgeNode] = {}
        self.initialize_grid()

    def initialize_grid(self):
        self.nodes.clear()
        for i in range(1, 10):
            nid = f"node_{i}"
            pid = f"plot_{i}"
            self.nodes[pid] = VirtualEdgeNode(nid, pid, seed=self.master_seed + i)

    def trigger_scenario(self, scenario_name: str, target_plot_id: str = "plot_1", intensity: float = 1.0):
        """
        Executes verified macro and micro-meteorological scenarios:
        - LOCALISED_CLOUDBURST: Intense torrential deluge on target plot, zero rain on neighbors
        - REGIONAL_STORM: Heavy rain across multiple contiguous plots
        - SEVERE_DROUGHT: Extended thermal heatwave desiccating soil moisture
        - SENSOR_DRIFT: Induces subtle sensor calibration decay
        - DISCONNECTION_OUTAGE: Drops node offline to demonstrate backlog recovery
        """
        target = self.nodes.get(target_plot_id)
        if not target:
            return

        if scenario_name == "LOCALISED_CLOUDBURST":
            # Plot receives 85mm cloudburst, neighbors remain dry
            target.step_environmental_physics(dt_minutes=15.0, rain_influx_mm=85.0 * intensity)
            target.sample_and_enqueue()

        elif scenario_name == "REGIONAL_STORM":
            # Multi-plot deluge
            for pid, node in self.nodes.items():
                node.step_environmental_physics(dt_minutes=15.0, rain_influx_mm=75.0 * intensity)
                node.sample_and_enqueue()

        elif scenario_name == "SEVERE_DROUGHT":
            # Rapid moisture desiccation & heatwave
            target.soil_moisture = max(5.0, 11.5 - (intensity * 2.0))
            target.temperature = 43.5 + (intensity * 1.5)
            target.step_environmental_physics(dt_minutes=60.0, rain_influx_mm=0.0, ambient_temp_override=target.temperature)
            target.sample_and_enqueue()

        elif scenario_name == "SENSOR_STUCK":
            target.inject_fault(VirtualSensorFault.STUCK, target_sensor="soil_moisture", value=14.2)
            target.sample_and_enqueue()

        elif scenario_name == "SENSOR_DRIFT":
            target.inject_fault(VirtualSensorFault.DRIFT, target_sensor="soil_moisture", value=-9.5)
            target.sample_and_enqueue()

        elif scenario_name == "NETWORK_DISCONNECT":
            target.set_connectivity(False)

        elif scenario_name == "NETWORK_RECONNECT":
            target.set_connectivity(True)

# Global simulation grid singleton
simulation_grid = FarmSimulationGrid()
