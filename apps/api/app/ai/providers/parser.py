import json

from app.ai.schemas.investigation import (
    InvestigationResult,
)


def parse_investigation(
    raw_output: str,
) -> InvestigationResult:

    data = json.loads(raw_output)

    return InvestigationResult.model_validate(
        data
    )