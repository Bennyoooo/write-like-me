import json
from pathlib import Path

from scripts import install


def test_cursor_install_preserves_existing_hooks(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    cursor_dir = tmp_path / ".cursor"
    cursor_dir.mkdir()
    hooks_path = cursor_dir / "hooks.json"
    hooks_path.write_text(json.dumps({"version": 1, "hooks": {"stop": [{"command": "existing"}]}}))

    install.install_cursor()
    install.install_cursor()

    payload = json.loads(hooks_path.read_text())
    assert payload["hooks"]["stop"] == [{"command": "existing"}]
    assert len(payload["hooks"]["beforeSubmitPrompt"]) == 1
    assert "wlm hook --agent cursor" in payload["hooks"]["beforeSubmitPrompt"][0]["command"]


def test_detects_opencode_config(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / ".config/opencode").mkdir(parents=True)
    assert install.detected("opencode")
