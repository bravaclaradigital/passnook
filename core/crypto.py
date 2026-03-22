"""
PassNook — Cryptography layer
PBKDF2-HMAC-SHA256 key derivation + Fernet authenticated encryption.
"""

import os
import hashlib
import base64
from cryptography.fernet import Fernet, InvalidToken

SALT_SIZE        = 32
PBKDF2_ITERS     = 390_000   # OWASP 2023 recommendation for SHA-256
KEY_LEN          = 32


def generate_salt() -> bytes:
    return os.urandom(SALT_SIZE)


def derive_key(password: str, salt: bytes) -> bytes:
    """Return a 32-byte URL-safe base64 key suitable for Fernet."""
    raw = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERS,
        dklen=KEY_LEN,
    )
    return base64.urlsafe_b64encode(raw)


def encrypt(plaintext: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(plaintext)


def decrypt(token: bytes, key: bytes) -> bytes:
    """Raises cryptography.fernet.InvalidToken on wrong key or tampered data."""
    return Fernet(key).decrypt(token)
