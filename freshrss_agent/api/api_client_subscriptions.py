#!/usr/bin/python
"""Subscription, category and tagging operations for the FreshRSS GReader API."""

from typing import Any


class SubscriptionsMixin:
    """Manage feeds, categories and item tags (read/star) via the GReader API."""

    request: Any
    _get_write_token: Any

    def subscription_list(self) -> dict[str, Any]:
        """List all feed subscriptions."""
        return self.request("GET", "reader/api/0/subscription/list")

    def categories(self) -> dict[str, Any]:
        """List categories / tags (``tag/list``)."""
        return self.request("GET", "reader/api/0/tag/list")

    def _stream_for_feed(self, feed_url: str) -> str:
        return feed_url if feed_url.startswith("feed/") else f"feed/{feed_url}"

    def subscribe(
        self,
        feed_url: str,
        title: str | None = None,
        category: str | None = None,
    ) -> dict[str, Any]:
        """Subscribe to a feed, optionally setting its title and category."""
        data: list[tuple[str, str]] = [
            ("ac", "subscribe"),
            ("s", self._stream_for_feed(feed_url)),
            ("T", self._get_write_token()),
        ]
        if title:
            data.append(("t", title))
        if category:
            data.append(("a", f"user/-/label/{category}"))
        return self.request("POST", "reader/api/0/subscription/edit", data=data)

    def unsubscribe(self, feed_url: str) -> dict[str, Any]:
        """Unsubscribe from a feed."""
        data = [
            ("ac", "unsubscribe"),
            ("s", self._stream_for_feed(feed_url)),
            ("T", self._get_write_token()),
        ]
        return self.request("POST", "reader/api/0/subscription/edit", data=data)

    def label(self, feed_url: str, category: str) -> dict[str, Any]:
        """Add a category label to an existing feed subscription."""
        data = [
            ("ac", "edit"),
            ("s", self._stream_for_feed(feed_url)),
            ("a", f"user/-/label/{category}"),
            ("T", self._get_write_token()),
        ]
        return self.request("POST", "reader/api/0/subscription/edit", data=data)

    def mark_read(self, item_ids: list[str] | str) -> dict[str, Any]:
        """Mark one or more items as read."""
        if isinstance(item_ids, str):
            item_ids = [item_ids]
        data: list[tuple[str, str]] = [("T", self._get_write_token())]
        data.append(("a", "user/-/state/com.google/read"))
        data.extend(("i", item_id) for item_id in item_ids)
        return self.request("POST", "reader/api/0/edit-tag", data=data)

    def star(self, item_id: str, starred: bool = True) -> dict[str, Any]:
        """Star or unstar an item."""
        key = "a" if starred else "r"
        data = [
            ("T", self._get_write_token()),
            (key, "user/-/state/com.google/starred"),
            ("i", item_id),
        ]
        return self.request("POST", "reader/api/0/edit-tag", data=data)
