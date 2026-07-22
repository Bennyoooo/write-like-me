#!/bin/sh

# Prompt capture is intentionally fail-open and silent.
agent="${1:-plugin}"
if command -v wlm >/dev/null 2>&1; then
  exec wlm hook --agent "$agent" 2>/dev/null
fi

runtime="${WLM_HOME:-$HOME/.write-like-me}/runtime/bin/wlm"
if [ -x "$runtime" ]; then
  exec "$runtime" hook --agent "$agent" 2>/dev/null
fi

cat >/dev/null
exit 0
