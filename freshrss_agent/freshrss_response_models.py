#!/usr/bin/python
"""Pydantic response models for FreshRSS GReader API payloads."""

from typing import Any

from pydantic import BaseModel, Field


class FeedItem(BaseModel):
    """A single feed item from a stream-contents response."""

    id: str | None = Field(default=None, description="GReader long-form item id.")
    title: str | None = Field(default=None, description="Item title.")
    published: int | None = Field(
        default=None, description="Publish time (unix seconds)."
    )
    updated: int | None = Field(default=None, description="Update time (unix seconds).")
    canonical: list[dict[str, Any]] | None = Field(
        default=None, description="Canonical link(s), each with an 'href'."
    )
    summary: dict[str, Any] | None = Field(
        default=None, description="Summary content ({'content': ...})."
    )
    content: dict[str, Any] | None = Field(
        default=None, description="Full content ({'content': ...})."
    )
    origin: dict[str, Any] | None = Field(
        default=None, description="Feed origin (streamId, title, htmlUrl)."
    )
    categories: list[str] | None = Field(
        default=None, description="Category/state tags applied to the item."
    )


class StreamContentsResponse(BaseModel):
    """Response from a stream-contents request."""

    items: list[FeedItem] = Field(default_factory=list, description="Feed items.")
    continuation: str | None = Field(
        default=None, description="Continuation token for the next page."
    )


class Subscription(BaseModel):
    """A feed subscription entry."""

    id: str | None = Field(default=None, description="Stream id (feed/<url>).")
    title: str | None = Field(default=None, description="Feed title.")
    url: str | None = Field(default=None, description="Feed URL.")
    htmlUrl: str | None = Field(default=None, description="Site HTML URL.")
    categories: list[dict[str, Any]] | None = Field(
        default=None, description="Categories the feed belongs to."
    )


class Category(BaseModel):
    """A category / tag entry."""

    id: str | None = Field(default=None, description="Tag id (user/-/label/<cat>).")
    type: str | None = Field(default=None, description="Tag type, e.g. 'folder'.")


class UnreadCount(BaseModel):
    """An unread-count entry for one stream."""

    id: str | None = Field(default=None, description="Stream id.")
    count: int | None = Field(default=None, description="Unread item count.")
    newestItemTimestampUsec: str | None = Field(
        default=None, description="Newest item timestamp (microseconds)."
    )
