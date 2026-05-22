"""RSS/Atom adapter using httpx and feedparser."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import feedparser
import httpx

from pipeline.ingest.adapters.base import SourceAdapter
from pipeline.models import RawItem, SourceConfig


class RssAdapter(SourceAdapter):
    """Fetch and parse RSS feeds; optionally follow entry links for full text."""

    def __init__(
        self,
        *,
        timeout: float = 30.0,
        fetch_linked_pages: bool = True,
        client: httpx.Client | None = None,
    ) -> None:
        self._timeout = timeout
        self._fetch_linked_pages = fetch_linked_pages
        self._client = client
        self._owns_client = client is None

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=self._timeout,
                follow_redirects=True,
                headers={"User-Agent": "intel-pipeline/0.1 (+https://github.com/HiyaMehta02/intel-pipeline)"},
            )
        return self._client

    def close(self) -> None:
        if self._owns_client and self._client is not None:
            self._client.close()
            self._client = None

    def fetch(self, source: SourceConfig) -> list[RawItem]:
        client = self._get_client()
        response = client.get(str(source.url))
        response.raise_for_status()
        parsed = feedparser.parse(response.text)
        if getattr(parsed, "bozo", False) and not parsed.entries:
            exc = getattr(parsed, "bozo_exception", None)
            msg = f"RSS parse error for {source.id}: {exc}"
            raise ValueError(msg)

        return entries_to_raw_items(
            source,
            parsed.entries[:50],
            client,
            fetch_linked_pages=self._fetch_linked_pages,
        )

    def _entry_to_raw_item(
        self,
        source: SourceConfig,
        entry: Any,
        client: httpx.Client,
    ) -> RawItem | None:
        title = (entry.get("title") or "").strip()
        if not title:
            return None

        link = entry.get("link")
        summary = entry.get("summary") or entry.get("description")
        body_html = None
        body_text = None

        content_list = entry.get("content") or []
        if content_list:
            body_html = content_list[0].get("value")

        published_at = None
        if entry.get("published_parsed"):
            published_at = _struct_time_to_datetime(entry.published_parsed)
        elif entry.get("updated_parsed"):
            published_at = _struct_time_to_datetime(entry.updated_parsed)

        if self._fetch_linked_pages and link and _needs_page_fetch(body_html, summary):
            try:
                page = client.get(link)
                page.raise_for_status()
                body_html = page.text
            except httpx.HTTPError:
                pass

        return RawItem(
            source_id=source.id,
            source_name=source.name,
            domain_tag=source.domain_tag,
            title=title,
            summary=_strip_html(summary) if summary else None,
            body_html=body_html,
            body_text=body_text,
            canonical_url=link,
            published_at=published_at,
        )


def _needs_page_fetch(body_html: str | None, summary: str | None) -> bool:
    if body_html and len(_strip_html(body_html)) > 400:
        return False
    if summary and len(_strip_html(summary)) > 400:
        return False
    return True


def _strip_html(value: str) -> str:
    if not value:
        return ""
    try:
        import trafilatura

        return trafilatura.extract(value, include_comments=False, include_tables=False) or value
    except Exception:
        return value


def entries_to_raw_items(
    source: SourceConfig,
    entries: list[Any],
    client: httpx.Client,
    *,
    fetch_linked_pages: bool,
) -> list[RawItem]:
    adapter = RssAdapter(fetch_linked_pages=fetch_linked_pages, client=client)
    items: list[RawItem] = []
    for entry in entries:
        item = adapter._entry_to_raw_item(source, entry, client)  # noqa: SLF001
        if item is not None:
            items.append(item)
    return items


def _struct_time_to_datetime(struct_time: Any) -> datetime:
    return datetime(*struct_time[:6], tzinfo=UTC)
