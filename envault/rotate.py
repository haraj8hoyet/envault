"""Password rotation for envault vaults."""

from envault.storage import load_vault, save_vault, vault_exists
from envault.crypto import derive_key, encrypt, decrypt
import json


class RotationError(Exception):
    pass


def rotate_password(vault_name: str, old_password: str, new_password: str) -> int:
    """Re-encrypt all secrets in a vault with a new password.

    Returns the number of keys re-encrypted.
    Raises RotationError if the vault does not exist or the old password is wrong.
    """
    if not vault_exists(vault_name):
        raise RotationError(f"Vault '{vault_name}' does not exist.")

    try:
        raw = load_vault(vault_name, old_password)
    except Exception as exc:
        raise RotationError(f"Failed to open vault with old password: {exc}") from exc

    try:
        save_vault(vault_name, new_password, raw)
    except Exception as exc:
        raise RotationError(f"Failed to save vault with new password: {exc}") from exc

    return len(raw)


def verify_password(vault_name: str, password: str) -> bool:
    """Return True if *password* can decrypt the vault, False otherwise."""
    if not vault_exists(vault_name):
        return False
    try:
        load_vault(vault_name, password)
        return True
    except Exception:
        return False
