# Privacy

Prompt collection is disabled until `wlm init` succeeds. The installer requires confirmation unless the caller explicitly passes `--yes`.

## Stored Data

By default Write Like Me stores redacted sample text, source labels, timestamps, hashes, and redaction labels in `~/.write-like-me/voice.db`. Configuration is stored beside it. Files and directories are created with user-only permissions where the operating system supports POSIX modes.

No data is sent over the network by the runtime. Installing Python build dependencies and agent plugins may use the network.

## Filtering

Before storage, the capture pipeline:

- skips short and code-dominant samples
- truncates unusually long samples
- deduplicates exact normalized text
- redacts common API keys, bearer tokens, credentials, private keys, and email addresses
- removes old samples after the configured retention count

Pattern-based redaction is not a security boundary and cannot recognize every secret or personal identifier. Do not submit secrets to an AI agent or rely on this tool to make unsafe text safe.

## Controls

```bash
wlm status
wlm pause
wlm resume
wlm export profile.json
wlm restore profile.json
wlm forget --yes
```

`wlm forget` removes learned samples. To remove the runtime and all remaining state, first uninstall the agent plugins, then delete `~/.write-like-me`.

Exports contain sample text. Review them before sharing.
