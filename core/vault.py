"""
PassNook — Vault manager
File format (binary):
  [4 bytes]  magic  b"PN01"
  [32 bytes] salt   (PBKDF2 salt)
  [rest]     Fernet-encrypted JSON payload

JSON structure:
  {
    "version": 1,
    "entries": [
      {
        "id":       str (uuid4),
        "type":     "password" | "note",
        "title":    str,          # site name or note title
        "url":      str,
        "username": str,
        "password": str,
        "content":  str,          # secure-note body
        "notes":    str,          # extra notes on a password entry
        "created":  float,
        "modified": float
      }, ...
    ]
  }
"""

import json
import time
import uuid
from pathlib import Path
from cryptography.fernet import InvalidToken

from core.crypto import generate_salt, derive_key, encrypt, decrypt

MAGIC   = b"PN01"
APPDATA = Path.home() / "AppData" / "Roaming" / "PassNook"
VAULT_PATH = APPDATA / "vault.pn"


class WrongPassword(Exception):
    pass


class VaultManager:
    def __init__(self):
        self._key:     bytes | None = None
        self._entries: list[dict]   = []
        self._salt:    bytes | None = None
        APPDATA.mkdir(parents=True, exist_ok=True)

    # ── State ────────────────────────────────────────────────────────────────

    @property
    def is_unlocked(self) -> bool:
        return self._key is not None

    @property
    def vault_exists(self) -> bool:
        return VAULT_PATH.exists()

    def lock(self):
        self._key     = None
        self._entries = []
        self._salt    = None

    # ── Create / Open ────────────────────────────────────────────────────────

    def create(self, master_password: str) -> None:
        """Initialise a brand-new empty vault with *master_password*."""
        self._salt    = generate_salt()
        self._key     = derive_key(master_password, self._salt)
        self._entries = []
        self._save()

    def open(self, master_password: str) -> None:
        """Open existing vault. Raises WrongPassword on bad password."""
        data = VAULT_PATH.read_bytes()
        if not data.startswith(MAGIC):
            raise ValueError("Not a valid PassNook vault file.")
        salt  = data[4:36]
        token = data[36:]
        key   = derive_key(master_password, salt)
        try:
            payload = decrypt(token, key)
        except (InvalidToken, Exception):
            raise WrongPassword("Incorrect master password.")
        parsed = json.loads(payload.decode("utf-8"))
        self._salt    = salt
        self._key     = key
        self._entries = parsed.get("entries", [])

    # ── CRUD ─────────────────────────────────────────────────────────────────

    def entries(self, kind: str | None = None) -> list[dict]:
        """Return all entries, optionally filtered by type ('password'|'note')."""
        if kind is None:
            return list(self._entries)
        return [e for e in self._entries if e.get("type") == kind]

    def add(self, entry: dict) -> dict:
        entry = dict(entry)
        entry["id"]       = str(uuid.uuid4())
        entry["created"]  = time.time()
        entry["modified"] = time.time()
        self._entries.append(entry)
        self._save()
        return entry

    def update(self, entry_id: str, updates: dict) -> None:
        for e in self._entries:
            if e["id"] == entry_id:
                e.update(updates)
                e["modified"] = time.time()
                break
        self._save()

    def delete(self, entry_id: str) -> None:
        self._entries = [e for e in self._entries if e["id"] != entry_id]
        self._save()

    # ── Backup / Restore ─────────────────────────────────────────────────────

    def export_backup(self, dest_path: str) -> None:
        """Copy the encrypted vault file to *dest_path*."""
        import shutil
        shutil.copy2(str(VAULT_PATH), dest_path)

    def restore_backup(self, src_path: str, master_password: str) -> None:
        """Validate *src_path* is a valid vault then replace current vault."""
        data = Path(src_path).read_bytes()
        if not data.startswith(MAGIC):
            raise ValueError("Not a valid PassNook backup file.")
        salt  = data[4:36]
        token = data[36:]
        key   = derive_key(master_password, salt)
        try:
            decrypt(token, key)          # validate only
        except Exception:
            raise WrongPassword("Master password doesn't match this backup.")
        import shutil
        shutil.copy2(src_path, str(VAULT_PATH))
        self.open(master_password)

    # ── Internal ─────────────────────────────────────────────────────────────

    def _save(self) -> None:
        payload = json.dumps({"version": 1, "entries": self._entries}).encode("utf-8")
        token   = encrypt(payload, self._key)
        VAULT_PATH.write_bytes(MAGIC + self._salt + token)
