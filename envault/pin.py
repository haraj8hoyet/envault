"""PIN-based quick-unlock for vaults (short numeric/alphanumeric code stored as a derived key hint)."""

import json
import os
import hashlib
import secrets
from pathlib import Path

PIN_DIR_NAME = ".pins"


class PinError(Exception):
    pass


def _pin_dir(base_dir: str | None = None) -> Path:
    root = Path(base_dir) if base_dir else Path.home() / ".envault"
    pin_dir = root / PIN_DIR_NAME
    pin_dir.mkdir(parents=True, exist_ok=True)
    return pin_dir


def _pin_file(vault_name: str, base_dir: str | None = None) -> Path:
    return _pin_dir(base_dir) / f"{vault_name}.pin.json"


def set_pin(vault_name: str, password: str, pin: str, base_dir: str | None = None) -> None:
    """Associate a PIN with a vault by storing a salted hash of (pin + password)."""
    if not pin or not pin.strip():
        raise PinError("PIN must not be empty.")
    if len(pin) < 4:
        raise PinError("PIN must be at least 4 characters.")

    salt = secrets.token_hex(16)
    combined = f"{pin}:{password}"
    digest = hashlib.sha256(f"{salt}{combined}".encode()).hexdigest()

    data = {"vault": vault_name, "salt": salt, "digest": digest}
    _pin_file(vault_name, base_dir).write_text(json.dumps(data))


def verify_pin(vault_name: str, password: str, pin: str, base_dir: str | None = None) -> bool:
    """Return True if the PIN is valid for the given vault and password."""
    pf = _pin_file(vault_name, base_dir)
    if not pf.exists():
        raise PinError(f"No PIN set for vault '{vault_name}'.")

    data = json.loads(pf.read_text())
    salt = data["salt"]
    expected = data["digest"]
    combined = f"{pin}:{password}"
    actual = hashlib.sha256(f"{salt}{combined}".encode()).hexdigest()
    return secrets.compare_digest(actual, expected)


def clear_pin(vault_name: str, base_dir: str | None = None) -> None:
    """Remove the stored PIN for a vault."""
    pf = _pin_file(vault_name, base_dir)
    if pf.exists():
        pf.unlink()


def has_pin(vault_name: str, base_dir: str | None = None) -> bool:
    """Return True if a PIN is configured for the vault."""
    return _pin_file(vault_name, base_dir).exists()
