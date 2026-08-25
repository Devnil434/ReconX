from typing import Literal

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    source_type: str
    source_id: str
    field: str
    observed_value: str
    significance: str


class Hypothesis(BaseModel):
    cause: str
    probability: float = Field(
        ge=0,
        le=1,
    )
    supporting_evidence: list[str]
    contradicting_evidence: list[str]


class InvestigationResult(BaseModel):
    case_id: str

    root_cause: str

    confidence: float = Field(
        ge=0,
        le=1,
    )

    summary: str

    hypotheses: list[Hypothesis]

    evidence: list[EvidenceItem]

    recommendation: Literal[
        "AUTO_RESOLVE",
        "HUMAN_REVIEW",
        "BLOCK",
    ]

    unresolved_questions: list[str]