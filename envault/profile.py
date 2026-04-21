"""Profile support: named sets of vaults for different environments (dev, staging, prod)."""

import json
import os
from pathlib import Path
from typing import List, Optional


class ProfileError(Exception):
    pass


def _profile_path(base_dir: Optional[str] = None) -> Path:
    root = Path(base_dir) if base_dir else Path.home() / ".envault"
    return root / "profiles.json"


def _load_profiles(base_dir: Optional[str] = None) -> dict:
    path = _profile_path(base_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_profiles(data: dict, base_dir: Optional[str] = None) -> None:
    path = _profile_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def create_profile(name: str, vaults: List[str], base_dir: Optional[str] = None) -> None:
    """Create a named profile with a list of vault names."""
    profiles = _load_profiles(base_dir)
    if name in profiles:
        raise ProfileError(f"Profile '{name}' already exists.")
    profiles[name] = {"vaults": vaults}
    _save_profiles(profiles, base_dir)


def get_profile(name: str, base_dir: Optional[str] = None) -> dict:
    """Return profile data for the given name."""
    profiles = _load_profiles(base_dir)
    if name not in profiles:
        raise ProfileError(f"Profile '{name}' not found.")
    return profiles[name]


def delete_profile(name: str, base_dir: Optional[str] = None) -> None:
    """Delete a profile by name."""
    profiles = _load_profiles(base_dir)
    if name not in profiles:
        raise ProfileError(f"Profile '{name}' not found.")
    del profiles[name]
    _save_profiles(profiles, base_dir)


def list_profiles(base_dir: Optional[str] = None) -> List[str]:
    """Return sorted list of profile names."""
    return sorted(_load_profiles(base_dir).keys())


def update_profile(name: str, vaults: List[str], base_dir: Optional[str] = None) -> None:
    """Replace the vault list for an existing profile."""
    profiles = _load_profiles(base_dir)
    if name not in profiles:
        raise ProfileError(f"Profile '{name}' not found.")
    profiles[name] = {"vaults": vaults}
    _save_profiles(profiles, base_dir)
