from prometheus_client import Counter, Histogram

webhook_received = Counter(
    "recoverrecon_webhooks_received_total",
    "Webhook events received",
)

webhook_duplicates = Counter(
    "recoverrecon_webhook_duplicates_total",
    "Duplicate webhook events",
)

investigations_total = Counter(
    "recoverrecon_investigations_total",
    "AI investigations",
)

auto_resolutions = Counter(
    "recoverrecon_auto_resolutions_total",
    "Autonomous resolutions",
)

human_reviews = Counter(
    "recoverrecon_human_reviews_total",
    "Human review cases",
)

investigation_latency = Histogram(
    "recoverrecon_investigation_latency_seconds",
    "Investigation latency",
)
