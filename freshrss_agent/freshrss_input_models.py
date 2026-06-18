#!/usr/bin/python
"""Pydantic input models for FreshRSS GReader API request parameters."""

from pydantic import BaseModel, Field


class StreamContentsParams(BaseModel):
    """Parameters for fetching stream contents."""

    stream_id: str = Field(
        default="user/-/state/com.google/reading-list",
        description="GReader stream id (reading-list, feed/<url>, user/-/label/<cat>).",
    )
    count: int = Field(
        default=100, description="Maximum number of items (GReader 'n')."
    )
    order: str = Field(
        default="o", description="'o' oldest-first or 'n' newest-first (GReader 'r')."
    )
    newer_than: int | None = Field(
        default=None,
        description="Unix-seconds watermark; exclude items older than this (GReader 'ot').",
    )
    continuation: str | None = Field(
        default=None, description="Continuation token for pagination (GReader 'c')."
    )


class ItemContentsParams(BaseModel):
    """Parameters for fetching specific item bodies."""

    item_ids: list[str] | str = Field(
        description="One or more GReader long-form item ids."
    )


class SubscribeParams(BaseModel):
    """Parameters for subscribing to a feed."""

    feed_url: str = Field(description="Feed URL (or 'feed/<url>' stream id).")
    title: str | None = Field(default=None, description="Optional feed title.")
    category: str | None = Field(
        default=None, description="Optional category label to assign."
    )


class UnsubscribeParams(BaseModel):
    """Parameters for unsubscribing from a feed."""

    feed_url: str = Field(description="Feed URL (or 'feed/<url>' stream id).")


class LabelParams(BaseModel):
    """Parameters for adding a category label to a feed."""

    feed_url: str = Field(description="Feed URL (or 'feed/<url>' stream id).")
    category: str = Field(description="Category label to add.")


class MarkReadParams(BaseModel):
    """Parameters for marking items as read."""

    item_ids: list[str] | str = Field(description="One or more item ids.")


class StarParams(BaseModel):
    """Parameters for starring/unstarring an item."""

    item_id: str = Field(description="The item id to star or unstar.")
    starred: bool = Field(default=True, description="True to star, False to unstar.")
