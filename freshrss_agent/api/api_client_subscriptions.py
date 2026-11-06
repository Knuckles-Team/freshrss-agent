#!/usr/bin/python
"""Subscription, category and tagging operations for the FreshRSS GReader API."""

import time
from typing import Any

import httpx

_GATEWAY_TIMEOUTS = (502, 504)


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

    def _find_subscription(self, feed: str) -> dict[str, Any] | None:
        """Return the subscription whose id (``feed/<n>``) or feed URL is ``feed``."""
        wanted = feed[len("feed/") :] if feed.startswith("feed/") else feed
        listing = self.subscription_list()
        for sub in (
            listing.get("subscriptions", []) if isinstance(listing, dict) else []
        ):
            if wanted in (
                sub.get("id", "")[len("feed/") :],
                sub.get("url"),
                sub.get("htmlUrl"),
            ):
                return sub
        return None

    def _confirm(self, feed: str, present: bool, attempts: int = 12) -> bool:
        """Poll the subscription list until ``feed`` is (not) subscribed."""
        for _ in range(attempts):
            if (self._find_subscription(feed) is not None) == present:
                return True
            time.sleep(5)
        return False

    def _write_subscription(self, data: list[tuple[str, str]]) -> dict[str, Any]:
        try:
            return self.request("POST", "reader/api/0/subscription/edit", data=data)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code not in _GATEWAY_TIMEOUTS:
                raise
        except httpx.TimeoutException:
            pass
        return {"status": 202, "text": "pending"}

    def subscribe(
        self,
        feed_url: str,
        title: str | None = None,
        category: str | None = None,
    ) -> dict[str, Any]:
        """Subscribe to a feed, optionally setting its title and category.

        FreshRSS fetches the feed before it answers, so a slow origin ends in a gateway
        timeout while the subscription still completes. The result is confirmed against
        the subscription list. Subscribing twice returns ``already_subscribed``.
        """
        existing = self._find_subscription(feed_url)
        if existing is not None:
            return {"status": "already_subscribed", "id": existing.get("id")}
        data: list[tuple[str, str]] = [
            ("ac", "subscribe"),
            ("s", self._stream_for_feed(feed_url)),
            ("T", self._get_write_token()),
        ]
        if title:
            data.append(("t", title))
        if category:
            data.append(("a", f"user/-/label/{category}"))
        result = self._write_subscription(data)
        if result.get("status") == 202 and not self._confirm(feed_url, True):
            raise TimeoutError(
                f"FreshRSS did not confirm the subscription to {feed_url}"
            )
        found = self._find_subscription(feed_url)
        return {"status": "subscribed", "id": found.get("id") if found else None}

    def unsubscribe(self, feed_url: str) -> dict[str, Any]:
        """Unsubscribe from a feed given its URL or its ``feed/<n>`` id.

        Returns ``not_subscribed`` when the feed is not in the subscription list.
        """
        existing = self._find_subscription(feed_url)
        if existing is None:
            return {"status": "not_subscribed"}
        data = [
            ("ac", "unsubscribe"),
            ("s", existing["id"]),
            ("T", self._get_write_token()),
        ]
        result = self._write_subscription(data)
        if result.get("status") == 202 and not self._confirm(feed_url, False):
            raise TimeoutError(f"FreshRSS did not confirm the removal of {feed_url}")
        return {"status": "unsubscribed", "id": existing["id"]}

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
