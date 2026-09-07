"""Input safety controls for untrusted user and document content."""

import re
from typing import Any


class SafetyViolation(ValueError):
    """Raised when input attempts to override policy or exfiltrate data."""


INJECTION_PATTERNS = (
    r"ignore\s+(all\s+)?previous instructions",
    r"disregard\s+(all\s+)?(prior|previous) instructions",
    r"reveal\s+(the\s+)?system prompt",
    r"show\s+(me\s+)?your\s+(hidden|secret) instructions",
    r"bypass\s+(your\s+)?(security|safety|policy)",
    r"print\s+(all\s+)?(api keys|secrets|credentials|tokens)",
    r"send\s+.*(password|secret|api key|credential).*(https?://|email)",
)

_COMPILED_PATTERNS = tuple(re.compile(pattern, re.IGNORECASE) for pattern in INJECTION_PATTERNS)


def assert_safe_text(value: str | None, field_name: str = "input") -> None:
    """Reject known instruction-override and credential-exfiltration attempts."""
    if not value:
        return
    for pattern in _COMPILED_PATTERNS:
        if pattern.search(value):
            raise SafetyViolation(f"Unsafe {field_name}: instruction override or data exfiltration detected")


def redact_sensitive_text(value: str) -> str:
    """Remove common credential formats before text is persisted or traced."""
    value = re.sub(
        r"(?i)(api[_ -]?key|token|password|secret)\s*[:=]\s*[^\s,;]+",
        r"\1=[REDACTED]",
        value,
    )
    value = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[EMAIL]", value)
    value = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]", value)
    value = re.sub(r"\b(?:\d[ -]*?){13,19}\b", "[CARD]", value)
    return value


def redact_sensitive_data(value: Any) -> Any:
    """Redact sensitive strings inside JSON-compatible nested data."""
    if isinstance(value, str):
        return redact_sensitive_text(value)
    if isinstance(value, dict):
        return {key: redact_sensitive_data(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_sensitive_data(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_sensitive_data(item) for item in value)
    return value
