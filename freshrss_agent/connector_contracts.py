"""Surface contracts: tool use, links, data locations and business roles."""

from scion_sdk.surface_contracts import (
    BusinessRole,
    DataLocation,
    Refusal,
    SurfaceLink,
    ToolStep,
    ToolUseContract,
)

CONTRACTS = (
    ToolUseContract(
        "triage-unread",
        (
            ToolStep(
                "freshrss_unread_count",
                params=(),
                result=(
                    "max",
                    "unreadcounts",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the GReader login or write token is rejected"
                    ),
                    Refusal("NOT_FOUND", "the stream, feed or item does not exist"),
                ),
            ),
            ToolStep(
                "freshrss_stream_contents",
                params=(
                    "stream_id",
                    "count",
                    "order",
                    "newer_than",
                    "continuation",
                ),
                result=(
                    "items",
                    "continuation",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the GReader login or write token is rejected"
                    ),
                    Refusal("NOT_FOUND", "the stream, feed or item does not exist"),
                ),
            ),
            ToolStep(
                "freshrss_item_contents",
                params=("item_ids",),
                result=("items",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the GReader login or write token is rejected"
                    ),
                    Refusal("NOT_FOUND", "the stream, feed or item does not exist"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "curate-items",
        (
            ToolStep(
                "freshrss_stream_contents",
                params=(
                    "stream_id",
                    "count",
                    "newer_than",
                ),
                result=("items",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the GReader login or write token is rejected"
                    ),
                    Refusal("NOT_FOUND", "the stream, feed or item does not exist"),
                ),
            ),
            ToolStep(
                "freshrss_mark_read",
                params=("item_ids",),
                result=("status",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the GReader login or write token is rejected"
                    ),
                    Refusal("NOT_FOUND", "the stream, feed or item does not exist"),
                ),
            ),
            ToolStep(
                "freshrss_star",
                params=(
                    "item_id",
                    "starred",
                ),
                result=("status",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the GReader login or write token is rejected"
                    ),
                    Refusal("NOT_FOUND", "the stream, feed or item does not exist"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "manage-subscriptions",
        (
            ToolStep(
                "freshrss_subscription_list",
                params=(),
                result=("subscriptions",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the GReader login or write token is rejected"
                    ),
                    Refusal("NOT_FOUND", "the stream, feed or item does not exist"),
                ),
            ),
            ToolStep(
                "freshrss_categories",
                params=(),
                result=("tags",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the GReader login or write token is rejected"
                    ),
                    Refusal("NOT_FOUND", "the stream, feed or item does not exist"),
                ),
            ),
            ToolStep(
                "freshrss_subscribe",
                params=(
                    "feed_url",
                    "title",
                    "category",
                ),
                result=(
                    "status",
                    "id",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the GReader login or write token is rejected"
                    ),
                    Refusal(
                        "BAD_REQUEST",
                        "FreshRSS refuses the feed: unreachable, not allowed to resolve, or invalid",
                    ),
                ),
            ),
            ToolStep(
                "freshrss_label",
                params=(
                    "feed_url",
                    "category",
                ),
                result=("status",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the GReader login or write token is rejected"
                    ),
                    Refusal("NOT_FOUND", "the stream, feed or item does not exist"),
                ),
            ),
            ToolStep(
                "freshrss_unsubscribe",
                params=("feed_url",),
                result=(
                    "status",
                    "id",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the GReader login or write token is rejected"
                    ),
                    Refusal("NOT_FOUND", "the stream, feed or item does not exist"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "ingest-feed-to-graph",
        (
            ToolStep(
                "freshrss_ingest_items",
                params=("params_json",),
                result=(
                    "listed",
                    "ingested",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the GReader login or write token is rejected"
                    ),
                    Refusal("NOT_FOUND", "the stream, feed or item does not exist"),
                ),
            ),
            ToolStep(
                "freshrss_ingest_subscriptions",
                params=("params_json",),
                result=(
                    "listed",
                    "ingested",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the GReader login or write token is rejected"
                    ),
                    Refusal("NOT_FOUND", "the stream, feed or item does not exist"),
                ),
            ),
        ),
    ),
)

LINKS = (
    SurfaceLink(
        "triage-unread",
        tools=(
            "freshrss_unread_count",
            "freshrss_stream_contents",
            "freshrss_item_contents",
        ),
        prompts=(
            "freshrss-operator",
            "freshrss-feed-reader",
        ),
        skills=("freshrss-feed-reader",),
    ),
    SurfaceLink(
        "curate-items",
        tools=(
            "freshrss_stream_contents",
            "freshrss_mark_read",
            "freshrss_star",
        ),
        prompts=(
            "freshrss-operator",
            "freshrss-feed-reader",
        ),
        skills=("freshrss-feed-reader",),
    ),
    SurfaceLink(
        "manage-subscriptions",
        tools=(
            "freshrss_subscription_list",
            "freshrss_categories",
            "freshrss_subscribe",
            "freshrss_label",
            "freshrss_unsubscribe",
        ),
        prompts=(
            "freshrss-operator",
            "freshrss-feed-curator",
        ),
        skills=("freshrss-subscription-management",),
    ),
    SurfaceLink(
        "ingest-feed-to-graph",
        tools=(
            "freshrss_ingest_items",
            "freshrss_ingest_subscriptions",
        ),
        prompts=(
            "freshrss-operator",
            "freshrss-knowledge-curator",
        ),
        skills=("freshrss-knowledge-ingestion",),
    ),
    SurfaceLink(
        "freshrss-agent-development",
        tools=(
            "freshrss_unread_count",
            "freshrss_stream_contents",
            "freshrss_item_contents",
            "freshrss_mark_read",
            "freshrss_star",
            "freshrss_subscription_list",
            "freshrss_categories",
            "freshrss_subscribe",
            "freshrss_label",
            "freshrss_unsubscribe",
            "freshrss_ingest_items",
            "freshrss_ingest_subscriptions",
        ),
        skills=("freshrss-agent-development",),
    ),
)

LOCATIONS = (
    DataLocation(
        "freshrss-streams",
        (
            "Document",
            "FeedSubscription",
        ),
        "FRESHRSS_URL",
        "freshrss_stream_contents",
        federation_key="stream_id",
    ),
    DataLocation(
        "freshrss-subscriptions",
        (
            "FeedSubscription",
            "FeedCategory",
        ),
        "FRESHRSS_URL",
        "freshrss_subscription_list",
        federation_key="id",
    ),
)

ROLES = (
    BusinessRole(
        "feed-reader",
        tasks=(
            "triage-unread",
            "curate-items",
        ),
    ),
    BusinessRole("feed-curator", tasks=("manage-subscriptions",)),
    BusinessRole("knowledge-curator", tasks=("ingest-feed-to-graph",)),
)
