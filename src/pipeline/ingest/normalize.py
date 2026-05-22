"""Normalize RawItem into RawDocument."""

from __future__ import annotations

import logging

import trafilatura
from bs4 import BeautifulSoup

from pipeline.models import RawDocument, RawItem

logger = logging.getLogger(__name__)


class NormalizationError(Exception):
    """Raised when no usable text can be extracted."""


def extract_text(
    item: RawItem,
    *,
    max_chars: int = 50_000,
) -> str:
    """Extract plain text from HTML, summary, or title."""
    candidates: list[str] = []

    if item.body_html:
        extracted = trafilatura.extract(
            item.body_html,
            include_comments=False,
            include_tables=False,
        )
        if extracted:
            candidates.append(extracted)

    if not candidates and item.body_html:
        soup = BeautifulSoup(item.body_html, "html.parser")
        fallback = soup.get_text(separator="\n", strip=True)
        if fallback:
            candidates.append(fallback)

    if item.body_text:
        candidates.append(item.body_text.strip())

    if item.summary:
        summary_text = trafilatura.extract(item.summary) or item.summary
        candidates.append(summary_text.strip())

    candidates.append(item.title.strip())

    for text in candidates:
        cleaned = " ".join(text.split())
        if len(cleaned) >= 20:
            if len(cleaned) > max_chars:
                logger.warning(
                    "Truncating normalized text for %s from %d to %d chars",
                    item.source_id,
                    len(cleaned),
                    max_chars,
                )
                return cleaned[:max_chars]
            return cleaned

    msg = f"Could not extract sufficient text for item: {item.title!r}"
    raise NormalizationError(msg)


def normalize_item(
    item: RawItem,
    *,
    max_chars: int = 50_000,
) -> RawDocument:
    """Convert RawItem to RawDocument with computed content_hash."""
    normalized_text = extract_text(item, max_chars=max_chars)
    return RawDocument.from_normalized(
        source_id=item.source_id,
        source_name=item.source_name,
        domain_tag=item.domain_tag,
        title=item.title,
        normalized_text=normalized_text,
        canonical_url=item.canonical_url,
        raw_html=item.body_html,
        published_at=item.published_at,
    )
