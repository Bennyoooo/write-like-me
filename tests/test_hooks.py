import json

from write_like_me.hooks import extract_prompt


def test_extracts_standard_hook_prompt() -> None:
    payload = json.dumps({"session_id": "abc", "hook_event_name": "UserPromptSubmit", "prompt": "Write this in my voice."})
    assert extract_prompt(payload, "codex") == "Write this in my voice."


def test_extracts_content_parts() -> None:
    payload = json.dumps({"message": {"parts": [{"type": "text", "text": "First part"}, {"text": "Second part"}]}})
    assert extract_prompt(payload, "opencode") == "First part\nSecond part"


def test_plain_text_passes_through() -> None:
    assert extract_prompt("ordinary prompt") == "ordinary prompt"

