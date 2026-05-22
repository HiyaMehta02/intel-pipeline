"""Tests for ADR-002 content hashing."""

from __future__ import annotations

from pipeline.models.hashing import CONTENT_HASH_HEX_LENGTH, compute_content_hash


def test_compute_content_hash_deterministic() -> None:
    text = "  Same content, different padding should not matter.  "
    assert compute_content_hash(text) == compute_content_hash(text.strip())
    assert compute_content_hash("alpha") == compute_content_hash("alpha")


def test_compute_content_hash_length_and_hex() -> None:
    digest = compute_content_hash("hello world")
    assert len(digest) == CONTENT_HASH_HEX_LENGTH
    assert digest == digest.lower()
    int(digest, 16)


def test_compute_content_hash_changes_when_content_changes() -> None:
    assert compute_content_hash("version-a") != compute_content_hash("version-b")
