"""Copy variables between vaults."""

from envault.vault import Vault


class CopyError(Exception):
    pass


def copy_variable(src_name: str, src_password: str, dst_name: str, dst_password: str, key: str, new_key: str = None) -> str:
    """Copy a single variable from one vault to another. Returns the key name used."""
    src = Vault.open(src_name, src_password)
    value = src.get(key)
    if value is None:
        raise CopyError(f"Key '{key}' not found in vault '{src_name}'")

    dst = Vault.open(dst_name, dst_password)
    target_key = new_key or key
    dst.set(target_key, value)
    return target_key


def copy_variables(src_name: str, src_password: str, dst_name: str, dst_password: str, keys: list, overwrite: bool = True) -> dict:
    """Copy multiple variables from one vault to another.
    Returns dict of {key: 'copied'|'skipped'}.
    """
    src = Vault.open(src_name, src_password)
    dst = Vault.open(dst_name, dst_password)

    results = {}
    for key in keys:
        value = src.get(key)
        if value is None:
            results[key] = "not_found"
            continue
        if not overwrite and dst.get(key) is not None:
            results[key] = "skipped"
            continue
        dst.set(key, value)
        results[key] = "copied"
    return results


def copy_all(src_name: str, src_password: str, dst_name: str, dst_password: str, overwrite: bool = True) -> dict:
    """Copy all variables from source vault to destination vault."""
    src = Vault.open(src_name, src_password)
    keys = src.list_keys()
    return copy_variables(src_name, src_password, dst_name, dst_password, keys, overwrite=overwrite)
