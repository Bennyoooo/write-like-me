# Contributing

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest -q
```

Keep the core dependency-free unless a dependency removes substantial complexity and has a clear privacy and maintenance story. Agent hooks must be silent, fail open, and capture only user-authored input.

Changes should include focused tests. Validate changed JSON manifests and run `python -m build` before opening a pull request. For a new agent adapter, document the official hook event, install location, input shape, and failure behavior.

Use conventional commit subjects where practical, such as `feat:`, `fix:`, `docs:`, and `test:`.
