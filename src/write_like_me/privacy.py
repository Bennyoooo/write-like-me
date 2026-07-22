from __future__ import annotations

import re


REDACTIONS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S)),
    ("bearer-token", re.compile(r"(?i)\bbearer\s+[a-z0-9._~+/=-]{12,}")),
    ("api-key", re.compile(r"\b(?:sk|pk|rk|ghp|github_pat|xox[baprs])[-_a-zA-Z0-9]{16,}\b")),
    ("credential", re.compile(r"(?i)\b(password|passwd|secret|token|api[_ -]?key)\s*[:=]\s*[^\s,;]{6,}")),
    ("email", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)),
)


def redact(text: str) -> tuple[str, list[str]]:
    labels: list[str] = []
    cleaned = text
    for label, pattern in REDACTIONS:
        cleaned, count = pattern.subn(f"[REDACTED:{label}]", cleaned)
        if count:
            labels.append(label)
    return cleaned, labels


def looks_like_code(text: str) -> bool:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return False
    code_lines = sum(
        1
        for line in lines
        if re.search(r"(^\s{4,}|[{};]$|^(def|class|import|from|const|let|function|SELECT|curl|git)\b)", line)
    )
    return len(lines) >= 3 and code_lines / len(lines) > 0.65


def normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    return re.sub(r"\n{4,}", "\n\n\n", text)

