import re
import logging
from dataclasses import dataclass, field
from typing import List, Tuple

logger = logging.getLogger(__name__)

REDACT = "[REDACTED:{label}]"

# (pattern, label, description for logging)
# Ordered: keyword-aware patterns first, then standalone high-confidence patterns.
_PII_RULES: List[Tuple[re.Pattern, str]] = [
    # Credentials shared with context words (high confidence)
    (
        re.compile(
            r"(?i)\b(?:password|passwd|pwd|passcode|pin\s*code|api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|bearer\s+token|private[_-]?key)\s*(?:is|:|=|->|\s+)\S{4,}",
            re.IGNORECASE,
        ),
        "credential",
    ),
    (
        re.compile(
            r"(?i)\b(?:my|the)\s+(?:password|pin|passcode|api\s*key|secret)\s+(?:is|:)\s*\S+",
            re.IGNORECASE,
        ),
        "credential",
    ),
    # Bank / account numbers with context
    (
        re.compile(
            r"(?i)\b(?:account|routing|iban|sort\s*code|bank)\s*(?:#|number|no\.?|:|=)?\s*[\d\s\-]{8,22}\b",
            re.IGNORECASE,
        ),
        "financial_id",
    ),
    # SSN (US)
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "ssn"),
    # Credit / debit card (16 digits, common separators)
    (re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"), "payment_card"),
    # API / secret key formats
    (re.compile(r"\bsk-[a-zA-Z0-9]{20,}\b"), "api_key"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "aws_key"),
    (re.compile(r"\beyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b"), "jwt_token"),
    # Long standalone digit sequences (10–17 digits) — likely account/card; skip shorter to avoid false positives
    (re.compile(r"\b\d{10,17}\b"), "long_number"),
    # Phone numbers (US-style, with area code)
    (re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)\s*[-.\s]?\d{3}[-.\s]?\d{4}\b"), "phone"),
    # Email only when user explicitly shares it as personal info
    (
        re.compile(
            r"(?i)\b(?:my|personal|private|contact)\s+email\s+(?:is|:)\s*[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            re.IGNORECASE,
        ),
        "email",
    ),
]


@dataclass
class PIIScanResult:
    original_text: str
    sanitized_text: str
    pii_detected: bool = False
    flags: List[str] = field(default_factory=list)
    redaction_count: int = 0


class PIIService:
    """Detect and redact sensitive personal data before AI processing or storage."""

    def scan_and_redact(self, text: str) -> PIIScanResult:
        if not text or not text.strip():
            return PIIScanResult(original_text=text, sanitized_text=text)

        sanitized = text
        flags: List[str] = []
        redaction_count = 0

        for pattern, label in _PII_RULES:
            matches = list(pattern.finditer(sanitized))
            if not matches:
                continue

            flags.append(label)
            replacement = REDACT.format(label=label)

            # Replace from end to start so indices stay valid
            for match in reversed(matches):
                sanitized = sanitized[: match.start()] + replacement + sanitized[match.end() :]
                redaction_count += 1

        # Deduplicate flags while preserving order
        seen = set()
        unique_flags = []
        for f in flags:
            if f not in seen:
                seen.add(f)
                unique_flags.append(f)

        pii_detected = redaction_count > 0
        if pii_detected:
            logger.info(
                "PII redacted: %d item(s), types=%s",
                redaction_count,
                unique_flags,
            )

        return PIIScanResult(
            original_text=text,
            sanitized_text=sanitized,
            pii_detected=pii_detected,
            flags=unique_flags,
            redaction_count=redaction_count,
        )

    def flag_label(self, flag: str) -> str:
        labels = {
            "credential": "password or secret",
            "financial_id": "financial ID",
            "ssn": "SSN",
            "payment_card": "payment card",
            "api_key": "API key",
            "aws_key": "cloud access key",
            "jwt_token": "access token",
            "long_number": "account number",
            "phone": "phone number",
            "email": "personal email",
        }
        return labels.get(flag, flag.replace("_", " "))
