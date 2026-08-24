from pydantic import BaseModel


class InvestigationResult(BaseModel):
    case_id: str
    root_cause: str
    evidence: list[str]
    confidence: float
    recommendation: str