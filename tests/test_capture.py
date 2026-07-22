from pathlib import Path

from write_like_me.capture import capture
from write_like_me.config import Config, save_config
from write_like_me.storage import Store


def test_capture_requires_opt_in(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("WLM_HOME", str(tmp_path))
    result = capture("This is long enough to become a useful writing sample.")
    assert not result.captured
    assert result.reason == "not initialized"


def test_capture_redacts_and_deduplicates(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("WLM_HOME", str(tmp_path))
    save_config(Config(initialized=True, enabled=True))
    text = "Please email person@example.com and use token sk-abcdefghijklmnopqrstuvwxyz."

    first = capture(text, source="test")
    second = capture(text, source="test")

    assert first.captured
    assert set(first.redactions) == {"api-key", "email"}
    assert not second.captured
    assert second.reason == "duplicate"
    stored = Store().texts()[0]
    assert "person@example.com" not in stored
    assert "abcdefghijklmnopqrstuvwxyz" not in stored


def test_capture_skips_mostly_code(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("WLM_HOME", str(tmp_path))
    save_config(Config(initialized=True, enabled=True))
    result = capture("def one():\n    return 1;\ndef two():\n    return 2;")
    assert not result.captured
    assert result.reason == "sample is mostly code"

