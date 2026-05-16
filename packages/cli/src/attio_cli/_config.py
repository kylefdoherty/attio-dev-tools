"""Auth and configuration management for the Attio CLI.

Handles API key resolution (flag > env var > config file), profile management,
and config file read/write at ~/.config/attio/config.json.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


def get_config_dir() -> Path:
    """Return the config directory, respecting XDG_CONFIG_HOME."""
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        base = Path(xdg)
    else:
        base = Path.home() / ".config"
    return base / "attio"


def get_config_path() -> Path:
    """Return the path to the config file."""
    return get_config_dir() / "config.json"


def _read_config() -> dict[str, Any]:
    """Read the config file, returning an empty dict if it doesn't exist."""
    path = get_config_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())  # type: ignore[no-any-return]
    except (json.JSONDecodeError, OSError):
        return {}


def _write_config(config: dict[str, Any]) -> None:
    """Write the config file, creating parent directories as needed."""
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2) + "\n")


def _resolve_1password(op_reference: str) -> str | None:
    """Resolve a secret from 1Password using the `op` CLI.

    Returns the secret value, or None if `op` is not installed or the reference is invalid.
    """
    try:
        result = subprocess.run(
            ["op", "read", op_reference],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def get_api_key(
    *,
    flag_value: str | None = None,
    profile_name: str | None = None,
) -> str | None:
    """Resolve the API key using the priority chain.

    Priority: explicit flag > ATTIO_API_KEY env var > profile (1password or plain key) > default profile.
    """
    # 1. Explicit flag
    if flag_value:
        return flag_value

    # 2. Environment variable
    env_key = os.environ.get("ATTIO_API_KEY")
    if env_key:
        return env_key

    # 3. Named profile or active profile
    config = _read_config()
    profiles = config.get("profiles", {})

    name = profile_name or config.get("active_profile", "default")
    profile = profiles.get(name, {})

    # 3a. 1Password reference — resolve at runtime
    op_ref = profile.get("op_reference")
    if op_ref:
        return _resolve_1password(op_ref)

    # 3b. Plain API key
    return profile.get("api_key")


def save_api_key(api_key: str, *, profile_name: str = "default", workspace_name: str | None = None) -> None:
    """Save an API key to a named profile."""
    config = _read_config()
    profiles = config.setdefault("profiles", {})
    profile = profiles.setdefault(profile_name, {})
    profile["api_key"] = api_key
    profile.pop("op_reference", None)
    if workspace_name:
        profile["workspace_name"] = workspace_name
    if "active_profile" not in config:
        config["active_profile"] = profile_name
    _write_config(config)


def save_1password_ref(op_reference: str, *, profile_name: str = "default", workspace_name: str | None = None) -> None:
    """Save a 1Password reference to a named profile. No secret is stored on disk."""
    config = _read_config()
    profiles = config.setdefault("profiles", {})
    profile = profiles.setdefault(profile_name, {})
    profile["op_reference"] = op_reference
    profile.pop("api_key", None)
    if workspace_name:
        profile["workspace_name"] = workspace_name
    if "active_profile" not in config:
        config["active_profile"] = profile_name
    _write_config(config)


def remove_api_key(*, profile_name: str | None = None) -> bool:
    """Remove credentials. If no profile specified, remove the active profile's key.

    Returns True if a key was actually removed.
    """
    config = _read_config()
    profiles = config.get("profiles", {})
    name = profile_name or config.get("active_profile", "default")
    profile = profiles.get(name, {})
    if "api_key" in profile:
        del profile["api_key"]
        _write_config(config)
        return True
    return False


def save_profile(name: str, api_key: str, *, workspace_name: str | None = None) -> None:
    """Save a named profile."""
    save_api_key(api_key, profile_name=name, workspace_name=workspace_name)


def load_profile(name: str) -> dict[str, Any] | None:
    """Load a named profile, returning None if it doesn't exist."""
    config = _read_config()
    return config.get("profiles", {}).get(name)


def set_active_profile(name: str) -> bool:
    """Set the active profile. Returns True if the profile exists."""
    config = _read_config()
    profiles = config.get("profiles", {})
    if name not in profiles:
        return False
    config["active_profile"] = name
    _write_config(config)
    return True


def list_profiles() -> dict[str, dict[str, Any]]:
    """Return all saved profiles."""
    config = _read_config()
    return config.get("profiles", {})


def get_active_profile_name() -> str:
    """Return the active profile name."""
    config = _read_config()
    return config.get("active_profile", "default")
