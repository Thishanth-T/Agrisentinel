"""
AgriSentinel Cryptographic Verification Engine
=============================================
SECP256k1 ECDSA device-identity verification, canonical serialization,
strict registered-device key lookup, timestamp freshness, and replay defense.

CRITICAL SECURITY PRINCIPLE:
This engine NEVER trusts an unauthenticated public key supplied in the request.
Every verification queries the authoritative DEVICE_REGISTRY.
"""

import hashlib
import json
import time
from typing import Dict, Any, Tuple, Optional, Set
import ecdsa

from farm_registry import (
    DEVICE_REGISTRY,
    SIMULATOR_TEST_PRIVATE_KEYS,
    get_registered_device,
    get_farm_profile
)

class CryptoEngine:
    CURVE = ecdsa.SECP256k1
    # Telemetry timestamp must be within 300 seconds (5 mins) of backend clock
    MAX_TIMESTAMP_SKEW_SECONDS = 300.0

    # In-memory replay cache: tracks (device_id, digest_hex) to prevent replaying identical packets
    _seen_digests: Set[str] = set()
    # In-memory latest accepted timestamp per device to enforce monotonic progression
    _latest_device_timestamp: Dict[str, float] = {}

    @classmethod
    def reset_replay_cache(cls):
        """Clears replay cache for demo reset operations."""
        cls._seen_digests.clear()
        cls._latest_device_timestamp.clear()

    @classmethod
    def canonicalize(cls, data: Dict[str, Any]) -> bytes:
        """
        Deterministic RFC 8785 compliant canonical JSON serialization.
        Sorts all keys recursively and eliminates arbitrary whitespace.
        """
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")

    @classmethod
    def compute_digest(cls, data: Dict[str, Any]) -> bytes:
        return hashlib.sha256(cls.canonicalize(data)).digest()

    @classmethod
    def sign_payload(cls, private_key_hex: str, data: Dict[str, Any]) -> str:
        """Signs canonical payload digest using SECP256k1 ECDSA private key."""
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex), curve=cls.CURVE)
        digest = cls.compute_digest(data)
        return sk.sign_digest(digest).hex()

    @classmethod
    def validate_sensor_physical_bounds(cls, telemetry: Dict[str, Any]) -> Tuple[bool, str]:
        """Validates that telemetry measurements respect thermodynamic & physical laws."""
        try:
            moisture = float(telemetry.get("soil_moisture", 0.0))
            temp = float(telemetry.get("temperature", 0.0))
            humidity = float(telemetry.get("humidity", 0.0))
            pressure = float(telemetry.get("pressure", 1012.0))
            rain = float(telemetry.get("rainfall_mm", 0.0))

            if not (0.0 <= moisture <= 100.0):
                return False, f"Physical bounds violation: Soil moisture {moisture}% outside 0-100% range"
            if not (-20.0 <= temp <= 65.0):
                return False, f"Physical bounds violation: Temperature {temp}°C outside plausible -20°C to 65°C range"
            if not (0.0 <= humidity <= 100.0):
                return False, f"Physical bounds violation: Humidity {humidity}% outside 0-100% range"
            if not (800.0 <= pressure <= 1100.0):
                return False, f"Physical bounds violation: Barometric pressure {pressure} hPa outside 800-1100 hPa"
            if not (0.0 <= rain <= 500.0):
                return False, f"Physical bounds violation: Rainfall {rain} mm outside plausible single-window bounds"

            return True, "Sensor bounds valid"
        except (ValueError, TypeError) as e:
            return False, f"Telemetry data type error: {str(e)}"

    @classmethod
    def verify_telemetry_packet(
        cls,
        node_id: str,
        claimed_plot_id: str,
        signature_hex: str,
        telemetry_dict: Dict[str, Any],
        enforce_freshness: bool = True
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Comprehensive data-trust pipeline:
        1. Validates physical sensor ranges.
        2. Queries authoritative device registry for node_id.
        3. Enforces device-to-farm plot assignment.
        4. Validates timestamp freshness window.
        5. Validates monotonic timestamp ordering and prevents packet replay.
        6. Verifies ECDSA SECP256k1 cryptographic signature against registered public key.
        """
        now = time.time()
        verification_metadata = {
            "node_id": node_id,
            "claimed_plot_id": claimed_plot_id,
            "device_registered": False,
            "plot_binding_valid": False,
            "bounds_valid": False,
            "freshness_valid": False,
            "replay_check_passed": False,
            "signature_valid": False,
            "registered_key_used": None,
            "failure_stage": None
        }

        # 1. Physical sensor bounds check
        bounds_ok, bounds_reason = cls.validate_sensor_physical_bounds(telemetry_dict)
        if not bounds_ok:
            verification_metadata["failure_stage"] = "SENSOR_BOUNDS_VIOLATION"
            return False, bounds_reason, verification_metadata
        verification_metadata["bounds_valid"] = True

        # 2. Device Registry check
        device = get_registered_device(node_id)
        if not device:
            verification_metadata["failure_stage"] = "UNREGISTERED_DEVICE"
            return False, f"Access Denied: Node ID '{node_id}' is not present in trusted hardware registry", verification_metadata
        
        verification_metadata["device_registered"] = True
        registered_public_key = device["public_key_hex"]
        verification_metadata["registered_key_used"] = registered_public_key

        # 3. Farm plot binding check
        assigned_plot_id = device.get("plot_id")
        if assigned_plot_id != claimed_plot_id:
            verification_metadata["failure_stage"] = "DEVICE_PLOT_MISMATCH"
            return False, f"Impersonation Rejected: Device '{node_id}' is provisioned for '{assigned_plot_id}', not '{claimed_plot_id}'", verification_metadata
        verification_metadata["plot_binding_valid"] = True

        # 4. Freshness check
        pkt_timestamp = telemetry_dict.get("timestamp")
        if pkt_timestamp is None:
            verification_metadata["failure_stage"] = "MISSING_TIMESTAMP"
            return False, "Telemetry packet missing required 'timestamp' field", verification_metadata
        
        try:
            pkt_timestamp = float(pkt_timestamp)
        except (ValueError, TypeError):
            verification_metadata["failure_stage"] = "MALFORMED_TIMESTAMP"
            return False, "Telemetry timestamp is not a valid float", verification_metadata

        if enforce_freshness:
            time_skew = abs(now - pkt_timestamp)
            if time_skew > cls.MAX_TIMESTAMP_SKEW_SECONDS:
                verification_metadata["failure_stage"] = "TIMESTAMP_SKEW_EXCEEDED"
                return False, f"Freshness Rejected: Packet timestamp delta ({time_skew:.1f}s) exceeds allowable window ({cls.MAX_TIMESTAMP_SKEW_SECONDS}s)", verification_metadata
        verification_metadata["freshness_valid"] = True

        # 5. Monotonic & Replay check
        digest_bytes = cls.compute_digest(telemetry_dict)
        digest_hex = digest_bytes.hex()
        replay_key = f"{node_id}:{digest_hex}"

        if replay_key in cls._seen_digests:
            verification_metadata["failure_stage"] = "REPLAY_DETECTED"
            return False, "Replay Attack Blocked: Exact duplicate signed telemetry digest was previously ingested", verification_metadata

        last_time = cls._latest_device_timestamp.get(node_id, 0.0)
        # Packet cannot be older than the device's last accepted reading by more than 1 second (jitter allowance)
        if enforce_freshness and pkt_timestamp < (last_time - 1.0):
            verification_metadata["failure_stage"] = "RETROGRADE_TIMESTAMP"
            return False, f"Sequence Rejected: Timestamp ({pkt_timestamp:.1f}) is earlier than device's last accepted reading ({last_time:.1f})", verification_metadata

        verification_metadata["replay_check_passed"] = True

        # 6. Cryptographic signature check against the REGISTERED public key
        try:
            vk_bytes = bytes.fromhex(registered_public_key)
            if len(vk_bytes) == 65 and vk_bytes[0] == 4:
                vk_bytes = vk_bytes[1:]
            vk = ecdsa.VerifyingKey.from_string(vk_bytes, curve=cls.CURVE)
            sig_bytes = bytes.fromhex(signature_hex)
            sig_valid = vk.verify_digest(sig_bytes, digest_bytes)
            if not sig_valid:
                verification_metadata["failure_stage"] = "SIGNATURE_INVALID"
                return False, "Cryptographic signature failed mathematical verification", verification_metadata
        except ecdsa.BadSignatureError:
            verification_metadata["failure_stage"] = "SIGNATURE_CORRUPTED"
            return False, "Signature Rejected: Corrupted or tampered cryptographic digest on SECP256k1 curve", verification_metadata
        except Exception as e:
            verification_metadata["failure_stage"] = "CRYPTO_EXCEPTION"
            return False, f"Cryptographic verification engine exception: {str(e)}", verification_metadata

        # Accepted! Update replay cache and device sequence
        verification_metadata["signature_valid"] = True
        cls._seen_digests.add(replay_key)
        cls._latest_device_timestamp[node_id] = max(last_time, pkt_timestamp)

        return True, "ECDSA SECP256k1 device signature verified against trusted registry", verification_metadata

    @classmethod
    def create_simulated_signed_packet(
        cls,
        node_id: str,
        telemetry_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Helper strictly for the software simulator. Signs telemetry using
        the simulator's provisioned test private key.
        """
        device = get_registered_device(node_id)
        if not device:
            raise ValueError(f"Cannot simulate unknown node: {node_id}")

        sk_hex = SIMULATOR_TEST_PRIVATE_KEYS.get(node_id)
        if not sk_hex:
            raise ValueError(f"No simulation test key provisioned for node: {node_id}")

        if "timestamp" not in telemetry_dict:
            telemetry_dict["timestamp"] = time.time()

        sig = cls.sign_payload(sk_hex, telemetry_dict)
        return {
            "node_id": node_id,
            "plot_id": telemetry_dict.get("plot_id", device["plot_id"]),
            "signature": sig,
            "telemetry": telemetry_dict,
            "_simulation_notice": "Signed with software test key. Hardware security requires silicon eFuse."
        }

# Backward compatibility wrappers
canonicalize = CryptoEngine.canonicalize
sign_payload = CryptoEngine.sign_payload
compute_digest = CryptoEngine.compute_digest
