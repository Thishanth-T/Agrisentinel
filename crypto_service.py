import hashlib
import json
import ecdsa

def generate_keypair():
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    return sk.to_string().hex(), vk.to_string().hex()

def canonicalize(data: dict) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")

def sign_payload(private_key_hex: str, data: dict) -> str:
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex), curve=ecdsa.SECP256k1)
    digest = hashlib.sha256(canonicalize(data)).digest()
    return sk.sign_digest(digest).hex()

def verify_payload(public_key_hex: str, data: dict, signature_hex: str) -> bool:
    try:
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=ecdsa.SECP256k1)
        digest = hashlib.sha256(canonicalize(data)).digest()
        return vk.verify_digest(bytes.fromhex(signature_hex), digest)
    except Exception:
        return False
