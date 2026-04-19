"""High-level vault operations for envault."""

from envault.storage import save_vault, load_vault, vault_exists, delete_vault, list_vaults


class Vault:
    def __init__(self, name: str, password: str):
        self.name = name
        self._password = password
        self._data: dict = {}

    @classmethod
    def create(cls, name: str, password: str) -> "Vault":
        """Create a new empty vault and persist it."""
        v = cls(name, password)
        save_vault(name, {}, password)
        return v

    @classmethod
    def open(cls, name: str, password: str) -> "Vault":
        """Open an existing vault from disk."""
        v = cls(name, password)
        v._data = load_vault(name, password)
        return v

    def set(self, key: str, value: str) -> None:
        """Set an environment variable in the vault."""
        self._data[key] = value
        self._save()

    def get(self, key: str) -> str:
        """Retrieve an environment variable from the vault."""
        if key not in self._data:
            raise KeyError(f"Key '{key}' not found in vault '{self.name}'.")
        return self._data[key]

    def delete(self, key: str) -> None:
        """Remove an environment variable from the vault."""
        if key not in self._data:
            raise KeyError(f"Key '{key}' not found in vault '{self.name}'.")
        del self._data[key]
        self._save()

    def all(self) -> dict:
        """Return all key-value pairs in the vault."""
        return dict(self._data)

    def _save(self) -> None:
        save_vault(self.name, self._data, self._password)

    def __repr__(self) -> str:
        return f"Vault(name={self.name!r}, keys={list(self._data.keys())})"
