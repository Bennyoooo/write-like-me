from __future__ import annotations

import os
from pathlib import Path


def home() -> Path:
    override = os.environ.get("WLM_HOME")
    if override:
        return Path(override).expanduser()
    state_home = os.environ.get("XDG_STATE_HOME")
    if state_home:
        return Path(state_home).expanduser() / "write-like-me"
    return Path.home() / ".write-like-me"


def ensure_private_dir() -> Path:
    root = home()
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        root.chmod(0o700)
    except OSError:
        pass
    return root


def config_path() -> Path:
    return home() / "config.json"


def database_path() -> Path:
    return home() / "voice.db"

