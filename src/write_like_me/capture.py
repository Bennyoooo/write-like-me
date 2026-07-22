from __future__ import annotations

from dataclasses import dataclass, field

from .config import load_config
from .privacy import looks_like_code, normalize, redact
from .storage import Store


@dataclass
class CaptureResult:
    captured: bool
    reason: str
    redactions: list[str] = field(default_factory=list)


def capture(text: str, source: str = "manual", channel: str = "typed", store: Store | None = None) -> CaptureResult:
    config = load_config()
    if not config.initialized:
        return CaptureResult(False, "not initialized")
    if not config.enabled:
        return CaptureResult(False, "capture paused")
    cleaned = normalize(text)
    if len(cleaned) < config.min_chars:
        return CaptureResult(False, "sample too short")
    if looks_like_code(cleaned):
        return CaptureResult(False, "sample is mostly code")
    cleaned = cleaned[: config.max_chars]
    redactions: list[str] = []
    if config.redact_secrets:
        cleaned, redactions = redact(cleaned)
    inserted = (store or Store()).add(cleaned, source, channel, redactions, config.max_samples)
    return CaptureResult(inserted, "captured" if inserted else "duplicate", redactions)

