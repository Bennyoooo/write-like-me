# Write Like Me

Local-first writing voice memory for AI agents.

Write Like Me learns from the prompts, documents, and speech transcripts you choose to capture. It builds a portable voice profile that Codex, Claude Code, OpenCode, Gemini CLI, Cursor, and other agents can use when you ask them to write in your style.

- Local by default: no API key, cloud account, or telemetry
- Explicit opt-in before prompt capture starts
- Automatic secret and email redaction
- Native prompt hooks plus a portable agent skill
- Inspect, pause, export, or delete the profile at any time
- Dependency-free runtime on Python 3.10+

## Quick Start

```bash
git clone https://github.com/Bennyoooo/write-like-me.git
cd write-like-me
./scripts/install.sh --agent auto
```

The installer shows the local storage notice and asks before enabling capture. Use `--yes` only when you intentionally want a non-interactive install:

```bash
./scripts/install.sh --agent all --yes
```

Then write normally in an installed agent. Once the profile has useful evidence, ask:

```text
Rewrite this so it sounds like me.
Draft this update in my voice.
Write a concise reply using my style.
```

## Agent Support

| Agent | Capture integration | Voice integration | Install |
| --- | --- | --- | --- |
| Codex | `UserPromptSubmit` hook | Native skill/plugin | `./scripts/install.sh --agent codex` |
| Claude Code | `UserPromptSubmit` hook | Native skill/plugin | `./scripts/install.sh --agent claude` |
| OpenCode | `chat.message` plugin hook | Native skill | `./scripts/install.sh --agent opencode` |
| Gemini CLI | `BeforeAgent` extension hook | Native skill | `./scripts/install.sh --agent gemini` |
| Cursor | `beforeSubmitPrompt` hook | Native skill | `./scripts/install.sh --agent cursor` |
| Other agents | Manual or external hook | Portable instructions | See [Other agents](#other-agents) |

The Codex CLI asks you to review and trust a new command hook. Run `/hooks` after installation and approve the Write Like Me hook. Other agents may show a similar trust prompt.

Run the installer more than once to upgrade the runtime and refresh adapters. Existing Cursor hooks are preserved.

## Build A Better Profile

Short coding prompts are weak evidence for prose. Import representative writing for better results:

```bash
~/.write-like-me/runtime/bin/wlm learn essay.txt emails.txt
~/.write-like-me/runtime/bin/wlm learn --channel spoken meeting-transcript.txt
```

Transcripts teach spoken phrasing; Write Like Me does not record a microphone or transcribe audio. Only text passed to `wlm` or a configured prompt hook is captured.

## CLI

The installer puts the isolated executable at `~/.write-like-me/runtime/bin/wlm`. Add that directory to `PATH` for a shorter command, or install the package with `pipx install .`.

```bash
wlm status                 # capture state, sample count, and data path
wlm profile                # human-readable analysis
wlm profile --json         # machine-readable metrics
wlm context                # instructions and redacted excerpts for an agent
wlm capture "sample text"  # add one sample manually
wlm learn file.txt         # learn from a document
wlm pause                  # stop new capture
wlm resume                 # resume capture
wlm export profile.json    # export redacted samples and metrics
wlm restore profile.json   # restore an exported profile
wlm forget --yes           # delete every learned sample
```

Set `WLM_HOME` to move all state, or `XDG_STATE_HOME` to use an XDG state directory.

## How It Works

1. A native hook receives the submitted user prompt and passes JSON to `wlm hook`.
2. The capture pipeline ignores short, duplicate, and code-dominant samples, then redacts common credentials and emails.
3. Samples are stored in a private SQLite database with bounded retention.
4. `wlm context` measures sentence rhythm, paragraph density, punctuation, contractions, vocabulary, phrases, openers, and pronoun use.
5. The agent skill applies those tendencies and a few bounded redacted excerpts when the user requests voice-matched writing.

Analysis is deterministic and runs locally. No model is used to build the profile. The final quality still depends on the installed agent and the quality of the samples.

See [Architecture](docs/ARCHITECTURE.md) and [Privacy](docs/PRIVACY.md) for the detailed design.

## Other Agents

Agents that can run commands can use the project without a native adapter:

1. Install the runtime with `./scripts/install.sh --agent auto` or `pipx install .`.
2. Add [WRITE_LIKE_ME.md](adapters/universal/WRITE_LIKE_ME.md) to the agent's global instructions.
3. Send each eligible user prompt to `wlm hook --agent <agent-name>` on standard input when the agent exposes a prompt hook.

The hook command is silent, always exits successfully, and never blocks the agent loop.

## Development

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest -q
python -m build
gemini extensions validate adapters/gemini
```

Plugin manifests live under `plugins/write-like-me`; agent-specific adapters live under `adapters`. Contributions for additional agents should reuse `wlm hook` rather than implement a second profile store.

See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

MIT
