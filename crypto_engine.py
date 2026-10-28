import hashlib
import json
import time
from typing import Dict, Any, Tuple, Optional
import ecdsa

PRESEEDED_NODE_KEYS = {
    "node_1": {
        "sk": "c98b671a5c13f64c67f8e79246a489f6645318e8011c2dfc9ff2d5cf78119854",
        "vk": "04b50c128ff0b1a0f9687e35aa19842f778a4869c9b466184a1d48c0a87a8a25c114e9f7833076ecf258a36021200be649f807be1778c8531ebcd7ff514120ec0e"
    },
    "node_2": {
        "sk": "4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d",
        "vk": "04936d97e84bf60eb80f08a478cbef2c7a363a033ebf61a153d9e84cc22a571ea0e051c91ffec94978be7b3d30b1bc01d14e9411963f2d2ee5fc30689b6b77df83"
    },
    "node_3": {
        "sk": "18e14a7b6a307f426a94f8114701e7c8e774e7f9a47e2c2035db29a206321725",
        "vk": "0450863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b23522cd470243453a299fa9e77237716103abc11a1df38855ed6f2ee187e9c582ba6"
    }
}

class CryptoEngine:
    CURVE = ecdsa.SECP256k1
    TIMESTAMP_TOLERANCE_SECONDS = 3600.0

    @classmethod
    def generate_keypair(cls) -> Tuple[str, str]:
        sk = ecdsa.SigningKey.generate(curve=cls.CURVE)
        vk = sk.verifying_key
        return sk.to_string().hex(), vk.to_string().hex()

    @classmethod
    def canonicalize(cls, data: Dict[str, Any]) -> bytes:
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")

    @classmethod
    def compute_digest(cls, data: Dict[str, Any]) -> bytes:
        return hashlib.sha256(cls.canonicalize(data)).digest()

    @classmethod
    def sign_payload(cls, private_key_hex: str, data: Dict[str, Any]) -> str:
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex), curve=cls.CURVE)
        digest = cls.compute_digest(data)
        return sk.sign_digest(digest).hex()

    @classmethod
    def verify_payload(
        cls,
        public_key_hex: str,
        data: Dict[str, Any],
        signature_hex: str,
        check_freshness: bool = False
    ) -> Tuple[bool, str]:
        if check_freshness and "timestamp" in data:
            try:
                pkt_time = float(data["timestamp"])
                now = time.time()
                if abs(now - pkt_time) > cls.TIMESTAMP_TOLERANCE_SECONDS:
                    return False, f"Replay check failed: Timestamp delta {abs(now - pkt_time):.1f}s exceeds tolerance ({cls.TIMESTAMP_TOLERANCE_SECONDS}s)"
            except (ValueError, TypeError):
                return False, "Invalid timestamp format in telemetry"

        try:
            vk_bytes = bytes.fromhex(public_key_hex)
            if len(vk_bytes) == 65 and vk_bytes[0] == 4:
                vk_bytes = vk_bytes[1:]
            vk = ecdsa.VerifyingKey.from_string(vk_bytes, curve=cls.CURVE)
            digest = cls.compute_digest(data)
            sig_bytes = bytes.fromhex(signature_hex)
            valid = vk.verify_digest(sig_bytes, digest)
            if valid:
                return True, "ECDSA SECP256k1 signature cryptographically valid"
            return False, "Signature verification failed"
        except ecdsa.BadSignatureError:
            return False, "Signature rejected: Corrupted or tampered cryptographic digest"
        except Exception as e:
            return False, f"Cryptographic verification error: {str(e)}"

    @classmethod
    def create_signed_packet(
        cls,
        node_id: str,
        private_key_hex: str,
        public_key_hex: str,
        telemetry_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        if "timestamp" not in telemetry_dict:
            telemetry_dict["timestamp"] = time.time()
        sig = cls.sign_payload(private_key_hex, telemetry_dict)
        return {
            "node_id": node_id,
            "public_key": public_key_hex,
            "signature": sig,
            "telemetry": telemetry_dict
        }

    @classmethod
    def get_or_create_node_keypair(cls, node_id: str) -> Tuple[str, str]:
        if node_id in PRESEEDED_NODE_KEYS:
            return PRESEEDED_NODE_KEYS[node_id]["sk"], PRESEEDED_NODE_KEYS[node_id]["vk"]
        sk, vk = cls.generate_keypair()
        PRESEEDED_NODE_KEYS[node_id] = {"sk": sk, "vk": vk}
        return sk, vk

generate_keypair = CryptoEngine.generate_keypair
canonicalize = CryptoEngine.canonicalize
sign_payload = CryptoEngine.sign_payload
verify_payload = lambda pk, d, sig: CryptoEngine.verify_payload(pk, d, sig)[0]
verify_payload_detailed = CryptoEngine.verify_payload
create_signed_packet = CryptoEngine.create_signed_packet
