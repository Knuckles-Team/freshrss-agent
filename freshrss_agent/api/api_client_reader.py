#!/usr/bin/python
"""Reader operations for the FreshRSS GReader API (stream contents, item bodies)."""

from typing import Any


class ReaderMixin:
    """Read-side GReader operations: stream contents, item bodies, unread counts."""

    request: Any

    def stream_contents(
        self,
        stream_id: str = "user/-/state/com.google/reading-list",
        count: int = 100,
        order: str = "o",
        newer_than: int | None = None,
        continuation: str | None = None,
    ) -> dict[str, Any]:
        """Fetch items for a stream.

        ``stream_id`` is a GReader stream id (e.g.
        ``user/-/state/com.google/reading-list`` for all items, ``feed/<feedUrl>``
        for one feed, or ``user/-/label/<category>``). ``order`` is ``o`` (oldest
        first) or ``n`` (newest first). ``newer_than`` is a unix-seconds watermark
        mapped to the GReader ``ot`` parameter (exclude items older than this).
        ``continuation`` resumes a previous page. Returns the raw
        ``{"items": [...], "continuation": "..."}`` payload.
        """
        params: dict[str, Any] = {"n": count, "r": order}
        if newer_than is not None:
            params["ot"] = int(newer_than)
        if continuation:
            params["c"] = continuation
        result = self.request(
            "GET",
            f"reader/api/0/stream/contents/{stream_id}",
            params=params,
        )
        # Normalize each item to flat, transport-safe top-level fields so a KG
        # connector reads ``text`` directly (a nested ``summary.content`` field-map
        # does not survive the MCP structured-output round-trip reliably). The raw
        # GReader fields (origin/categories/canonical) are preserved alongside.
        if isinstance(result, dict) and isinstance(result.get("items"), list):
            for item in result["items"]:
                if not isinstance(item, dict):
                    continue
                body = (
                    (item.get("summary") or {}).get("content")
                    or (item.get("content") or {}).get("content")
                    or ""
                )
                item["text"] = body
                canonical = item.get("canonical") or []
                if isinstance(canonical, list) and canonical:
                    item["url"] = canonical[0].get("href", "")
        return result

    def item_contents(self, item_ids: list[str] | str) -> dict[str, Any]:
        """Fetch full contents for specific item ids (GReader ``i`` parameters)."""
        if isinstance(item_ids, str):
            item_ids = [item_ids]
        data = [("i", item_id) for item_id in item_ids]
        return self.request(
            "POST",
            "reader/api/0/stream/items/contents",
            data=data,
        )

    def unread_count(self) -> dict[str, Any]:
        """Return unread counts per stream."""
        return self.request("GET", "reader/api/0/unread-count")
