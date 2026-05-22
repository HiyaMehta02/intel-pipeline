"""Content identity hashing (ADR-002)."""

from __future__ import annotations

import hashlib

CONTENT_HASH_HEX_LENGTH = 64


def compute_content_hash(normalized_text: str) -> str:
    """
    SHA-256 of UTF-8 normalized text after strip.

    Changing this algorithm invalidates stored documents and evaluations.
    """
    payload = normalized_text.strip().encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
