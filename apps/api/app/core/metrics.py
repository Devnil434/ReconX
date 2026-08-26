from prometheus_client import Counter, Histogram
 
webhook_received = Counter(
    "reconx_webhooks_received_total",
    "Webhook events received",
)

webhook_duplicates = Counter(
    "reconx_webhook_duplicates_total",
    "Duplicate webhook events",
)

investigations_total = Counter(
    "reconx_investigations_total",
    "AI investigations",
)

auto_resolutions = Counter(
    "reconx_auto_resolutions_total",
    "Autonomous resolutions",
)

human_reviews = Counter(
    "reconx_human_reviews_total",
    "Human review cases",
)

investigation_latency = Histogram(
    "reconx_investigation_latency_seconds",
    "Investigation latency",
)

