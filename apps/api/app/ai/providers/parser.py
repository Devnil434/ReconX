import json
import re

from app.ai.schemas.investigation import (
    InvestigationResult,
)


def parse_investigation(
    raw_output: str,
) -> InvestigationResult:

    cleaned = raw_output.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned)
        cleaned = cleaned.strip()

    data = json.loads(cleaned)

    return InvestigationResult.model_validate(
        data
    )