"""Adapter tests with respx (mocked HTTP)."""

from __future__ import annotations

import httpx
import respx

from pipeline.ingest.adapters.rss import RssAdapter
from pipeline.models import DomainTag, SourceConfig, SourceType


@respx.mock
def test_rss_adapter_fetches_and_parses() -> None:
    feed_url = "https://example.com/test-feed.xml"
    respx.get(feed_url).mock(
        return_value=httpx.Response(
            200,
            text="""<?xml version="1.0"?><rss><channel>
            <item><title>Mock Post</title><link>https://example.com/p/1</link>
            <description>Long enough description for normalization tests.</description>
            </item></channel></rss>""",
        ),
    )

    source = SourceConfig(
        id="mock",
        name="Mock",
        type=SourceType.RSS,
        url=feed_url,
        domain_tag=DomainTag.AI,
    )
    adapter = RssAdapter(fetch_linked_pages=False, timeout=5.0)
    try:
        items = adapter.fetch(source)
    finally:
        adapter.close()

    assert len(items) == 1
    assert items[0].title == "Mock Post"
