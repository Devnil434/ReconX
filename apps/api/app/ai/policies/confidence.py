def determine_confidence_band(
    confidence: float,
) -> str:

    if confidence >= 0.95:
        return "high"

    if confidence >= 0.80:
        return "medium"

    return "low"
