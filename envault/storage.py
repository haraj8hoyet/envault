"""Persistent encrypted storage for envault vaults."""

import json
import os
from pathlib import Path
from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_DIR = Path.home() / ".envault"


def _vault_path(vault_name: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> Path:
    vault_dir.mkdir(parents=True, exist_ok=True)
    return vault_dir / f"{vault_name}.vault"


def save_vault(vault_name: str, data: dict, password: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> None:
    """Serialize and encrypt vault data, then write to disk."""
    plaintext = json.dumps(data)
    token = encrypt(plaintext, password)
    path = _vault_path(vault_name, vault_dir)
    path.write_text(token)


def load_vault(vault_name: str, password: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> dict:
    """Read, decrypt, and deserialize vault data from disk."""
    path = _vault_path(vault_name, vault_dir)
    if not path.exists():
        raise FileNotFoundError(f"Vault '{vault_name}' does not exist.")
    token = path.read_text().strip()
    plaintext = decrypt(token, password)
    return json.loads(plaintext)


def vault_exists(vault_name: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> bool:
    return _vault_path(vault_name, vault_dir).exists()


def list_vaults(vault_dir: Path = DEFAULT_VAULT_DIR) -> list[str]:
    if not vault_dir.exists():
        return []
    return [p.stem for p in vault_dir.glob("*.vault")]


def delete_vault(vault_name: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> None:
    path = _vault_path(vault_name, vault_dir)
    if not path.exists():
        raise FileNotFoundError(f"Vault '{vault_name}' does not exist.")
    path.unlink()
