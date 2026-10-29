"""
AgriSentinel Cryptographic Service
==================================
Backward-compatibility adapter forwarding to crypto_engine.py.
"""

from crypto_engine import (
    CryptoEngine,
    canonicalize,
    sign_payload,
    compute_digest
)

def generate_keypair():
    sk, vk = CryptoEngine.generate_keypair()
    return sk, vk

def verify_payload(public_key_hex: str, data: dict, signature_hex: str) -> bool:
    try:
        valid, _, _ = CryptoEngine.verify_telemetry_packet(
            node_id="node_1",
            claimed_plot_id=data.get("plot_id", "plot_1"),
            signature_hex=signature_hex,
            telemetry_dict=data,
            enforce_freshness=False
        )
        return valid
    except Exception:
        return False
