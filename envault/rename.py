"""Rename keys within a vault, optionally across vaults."""

from envault.vault import Vault
from envault.storage import vault_exists


class RenameError(Exception):
    """Raised when a rename operation fails."""


def rename_key(vault_name: str, old_key: str, new_key: str, password: str, overwrite: bool = False) -> None:
    """Rename a key within the same vault.

    Args:
        vault_name: Name of the vault.
        old_key: Existing key name.
        new_key: Desired new key name.
        password: Vault password.
        overwrite: If True, overwrite new_key if it already exists.

    Raises:
        RenameError: If the vault does not exist, old_key is missing,
                     or new_key already exists and overwrite is False.
    """
    if not vault_exists(vault_name):
        raise RenameError(f"Vault '{vault_name}' does not exist.")

    vault = Vault.open(vault_name, password)

    if not vault.has(old_key):
        raise RenameError(f"Key '{old_key}' not found in vault '{vault_name}'.")

    if vault.has(new_key) and not overwrite:
        raise RenameError(
            f"Key '{new_key}' already exists in vault '{vault_name}'. "
            "Use overwrite=True to replace it."
        )

    value = vault.get(old_key)
    meta = vault.get_meta(old_key)

    vault.set(new_key, value)
    if meta:
        vault.set_meta(new_key, meta)

    vault.delete(old_key)
    vault.save(password)


def rename_keys_bulk(vault_name: str, mapping: dict[str, str], password: str, overwrite: bool = False) -> dict[str, str]:
    """Rename multiple keys at once.

    Args:
        vault_name: Name of the vault.
        mapping: Dict of {old_key: new_key}.
        password: Vault password.
        overwrite: If True, overwrite existing destination keys.

    Returns:
        Dict of {old_key: new_key} for successfully renamed keys.

    Raises:
        RenameError: If the vault does not exist.
    """
    if not vault_exists(vault_name):
        raise RenameError(f"Vault '{vault_name}' does not exist.")

    renamed = {}
    errors = []

    for old_key, new_key in mapping.items():
        try:
            rename_key(vault_name, old_key, new_key, password, overwrite=overwrite)
            renamed[old_key] = new_key
        except RenameError as exc:
            errors.append(str(exc))

    if errors:
        raise RenameError("Some keys could not be renamed:\n" + "\n".join(f"  - {e}" for e in errors))

    return renamed
