#!/bin/sh

if command -v wlm >/dev/null 2>&1; then
  exec wlm hook --agent "${1:-gemini}" 2>/dev/null
fi

runtime="${WLM_HOME:-$HOME/.write-like-me}/runtime/bin/wlm"
if [ -x "$runtime" ]; then
  exec "$runtime" hook --agent "${1:-gemini}" 2>/dev/null
fi

cat >/dev/null
exit 0
