# Architecture

Write Like Me separates the durable profile engine from agent-specific transport.

## Components

- `src/write_like_me`: dependency-free Python CLI, capture pipeline, SQLite store, analysis, and profile rendering.
- `plugins/write-like-me`: shared Codex, Claude Code, and Cursor plugin manifests, prompt hook, and voice skill.
- `adapters`: Gemini CLI extension, OpenCode plugin, Cursor hook template, and universal instructions.
- `scripts/install.py`: isolated runtime setup and idempotent agent configuration.

## Data Flow

```text
user prompt or imported transcript
  -> native agent hook / wlm learn
  -> normalize and eligibility checks
  -> local redaction
  -> content-hash deduplication
  -> ~/.write-like-me/voice.db
  -> deterministic analysis
  -> agent-ready context
  -> voice-matched draft
```

Hooks are capture-only. They emit no model-visible context and fail open. The voice skill calls `wlm context` only when a writing request needs the profile, keeping ordinary agent turns small.

## Profile Model

The analyzer derives aggregate statistics and repeated lexical patterns. It does not train weights or call a remote model. Agent context contains:

- evidence and confidence counts
- structural and punctuation tendencies
- characteristic vocabulary and repeated phrases
- bounded excerpts from up to three recent redacted samples
- guardrails against copying facts, secrets, and identity claims

SQLite provides atomic writes, bounded retention, and portable exports without a service process.
