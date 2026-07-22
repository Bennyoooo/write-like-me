from __future__ import annotations

import json
from typing import Any


PREFERRED_KEYS = ("prompt", "user_prompt", "message", "content", "text", "query", "input")


def extract_prompt(raw: str, agent: str = "auto") -> str:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return raw.strip()
    if isinstance(payload, str):
        return payload.strip()
    found = _find_text(payload)
    return found.strip() if found else ""


def _find_text(value: Any) -> str:
    if isinstance(value, dict):
        for key in PREFERRED_KEYS:
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate
            if isinstance(candidate, (list, dict)):
                nested = _find_text(candidate)
                if nested:
                    return nested
        for candidate in value.values():
            if isinstance(candidate, (list, dict)):
                nested = _find_text(candidate)
                if nested:
                    return nested
    elif isinstance(value, list):
        parts = [_find_text(item) for item in value]
        return "\n".join(part for part in parts if part)
    return ""

