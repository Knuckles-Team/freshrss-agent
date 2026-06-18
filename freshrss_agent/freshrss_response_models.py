#!/usr/bin/python
# coding: utf-8
"""Pydantic response models for FreshRSS GReader API payloads."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FeedItem(BaseModel):
    """A single feed item from a stream-contents response."""

    id: Optional[str] = Field(default=None, description="GReader long-form item id.")
    title: Optional[str] = Field(default=None, description="Item title.")
    published: Optional[int] = Field(
        default=None, description="Publish time (unix seconds)."
    )
    updated: Optional[int] = Field(
        default=None, description="Update time (unix seconds)."
    )
    canonical: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Canonical link(s), each with an 'href'."
    )
    summary: Optional[Dict[str, Any]] = Field(
        default=None, description="Summary content ({'content': ...})."
    )
    content: Optional[Dict[str, Any]] = Field(
        default=None, description="Full content ({'content': ...})."
    )
    origin: Optional[Dict[str, Any]] = Field(
        default=None, description="Feed origin (streamId, title, htmlUrl)."
    )
    categories: Optional[List[str]] = Field(
        default=None, description="Category/state tags applied to the item."
    )


class StreamContentsResponse(BaseModel):
    """Response from a stream-contents request."""

    items: List[FeedItem] = Field(default_factory=list, description="Feed items.")
    continuation: Optional[str] = Field(
        default=None, description="Continuation token for the next page."
    )


class Subscription(BaseModel):
    """A feed subscription entry."""

    id: Optional[str] = Field(default=None, description="Stream id (feed/<url>).")
    title: Optional[str] = Field(default=None, description="Feed title.")
    url: Optional[str] = Field(default=None, description="Feed URL.")
    htmlUrl: Optional[str] = Field(default=None, description="Site HTML URL.")
    categories: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Categories the feed belongs to."
    )


class Category(BaseModel):
    """A category / tag entry."""

    id: Optional[str] = Field(default=None, description="Tag id (user/-/label/<cat>).")
    type: Optional[str] = Field(default=None, description="Tag type, e.g. 'folder'.")


class UnreadCount(BaseModel):
    """An unread-count entry for one stream."""

    id: Optional[str] = Field(default=None, description="Stream id.")
    count: Optional[int] = Field(default=None, description="Unread item count.")
    newestItemTimestampUsec: Optional[str] = Field(
        default=None, description="Newest item timestamp (microseconds)."
    )
