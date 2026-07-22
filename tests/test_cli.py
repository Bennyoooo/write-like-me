import json
from pathlib import Path

from write_like_me.cli import main


def test_cli_lifecycle(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setenv("WLM_HOME", str(tmp_path / "state"))

    assert main(["init", "--yes"]) == 0
    assert main(["capture", "This is a complete sample of how I normally write."]) == 0
    transcript = tmp_path / "transcript.txt"
    transcript.write_text("Here is a spoken explanation with enough detail to learn from.")
    assert main(["learn", "--channel", "spoken", str(transcript)]) == 0
    assert main(["status"]) == 0
    assert "Samples: 2" in capsys.readouterr().out

    export_path = tmp_path / "export.json"
    assert main(["export", str(export_path)]) == 0
    assert len(json.loads(export_path.read_text())["samples"]) == 2

    assert main(["pause"]) == 0
    assert main(["forget", "--yes"]) == 0
    assert main(["restore", str(export_path)]) == 0
    assert main(["status"]) == 0
    assert "Samples: 2" in capsys.readouterr().out
