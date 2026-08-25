import json
from datetime import datetime

from app.ai.evidence.builder import (
    EvidenceBuilder,
)
from app.ai.evidence.facts import (
    build_financial_facts,
)
from app.ai.prompts.investigation import (
    SYSTEM_PROMPT,
    build_investigation_prompt,
)
from app.ai.providers.openai_provider import (
    OpenAIProvider,
)
from app.ai.providers.parser import (
    parse_investigation,
)
from app.models.investigation import (
    Investigation,
)
from app.models.investigation_evidence import (
    InvestigationEvidence,
)


class AIInvestigator:

    def __init__(self, db):

        self.db = db

        self.provider = OpenAIProvider()

        self.evidence_builder = (
            EvidenceBuilder()
        )

    async def investigate(
        self,
        exception,
        payment,
        settlements,
        bank_transactions,
        refunds,
    ):

        evidence = (
            self.evidence_builder.build(
                exception=exception,
                payment=payment,
                settlements=settlements,
                bank_transactions=(
                    bank_transactions
                ),
                refunds=refunds,
            )
        )

        facts = build_financial_facts(
            payment=payment,
            settlements=settlements,
            bank_transactions=(
                bank_transactions
            ),
            refunds=refunds,
        )

        case = {
            "case_id": exception.case_id,
            "exception_type": (
                exception.exception_type
            ),
            "severity": exception.severity,
            "expected_amount": (
                exception.expected_amount
            ),
            "actual_amount": (
                exception.actual_amount
            ),
            "difference": (
                exception.difference
            ),
            "reason": exception.reason,
        }

        prompt = build_investigation_prompt(
            case=case,
            facts=facts,
            evidence=evidence,
        )

        raw_output = (
            self.provider.investigate(
                SYSTEM_PROMPT,
                prompt,
            )
        )

        result = parse_investigation(
            raw_output
        )

        investigation = Investigation(
            case_id=exception.case_id,
            status="completed",
            root_cause=result.root_cause,
            confidence=result.confidence,
            recommendation=(
                result.recommendation
            ),
            summary=result.summary,
            evidence_json=json.dumps(
                [
                    item.model_dump()
                    for item in result.evidence
                ]
            ),
            hypotheses_json=json.dumps(
                [
                    item.model_dump()
                    for item in result.hypotheses
                ]
            ),
            created_at=datetime.utcnow(),
        )

        self.db.add(
            investigation
        )

        for item in evidence:

            self.db.add(
                InvestigationEvidence(
                    case_id=exception.case_id,
                    source_type=(
                        item["source_type"]
                    ),
                    source_id=(
                        item["source_id"]
                    ),
                    field=item["field"],
                    value=item["value"],
                    created_at=datetime.utcnow(),
                )
            )

        self.db.commit()

        self.db.refresh(
            investigation
        )

        return result