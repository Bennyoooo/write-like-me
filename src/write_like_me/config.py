from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass

from .paths import config_path, ensure_private_dir


@dataclass
class Config:
    enabled: bool = False
    initialized: bool = False
    min_chars: int = 20
    max_chars: int = 12_000
    max_samples: int = 2_000
    redact_secrets: bool = True


def load_config() -> Config:
    path = config_path()
    if not path.exists():
        return Config()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        allowed = Config.__dataclass_fields__.keys()
        return Config(**{key: value for key, value in data.items() if key in allowed})
    except (OSError, ValueError, TypeError):
        return Config()


def save_config(config: Config) -> None:
    ensure_private_dir()
    path = config_path()
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(asdict(config), indent=2) + "\n", encoding="utf-8")
    try:
        os.chmod(temporary, 0o600)
    except OSError:
        pass
    temporary.replace(path)

