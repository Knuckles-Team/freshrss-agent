from .api_client_base import FreshRSSClientBase
from .api_client_reader import ReaderMixin
from .api_client_subscriptions import SubscriptionsMixin


class FreshRSSApi(ReaderMixin, SubscriptionsMixin, FreshRSSClientBase):
    """FreshRSS GReader API client (reader + subscriptions)."""


# Backward-compat alias for the scaffold (auth.py imports ApiClientSystem).
ApiClientSystem = FreshRSSApi

__all__ = [
    "FreshRSSApi",
    "FreshRSSClientBase",
    "ReaderMixin",
    "SubscriptionsMixin",
    "ApiClientSystem",
]
