import json
from datetime import datetime
from sqlalchemy import select

from app.ai.evidence.builder import (
    EvidenceBuilder,
)
from app.ai.evidence.facts import (
    build_financial_facts,
)
from app.ai.evidence.graph import (
    build_transaction_graph,
)
from app.ai.prompts.investigation import (
    SYSTEM_PROMPT,
    build_investigation_prompt,
)
from app.ai.providers.gemini_provider import (
    GeminiProvider,
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

        self.provider = GeminiProvider()

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

        graph = build_transaction_graph(
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
            graph=graph,
        )

        raw_output = (
            self.provider.investigate(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=prompt,
                case_id=exception.case_id,
            )
        )

        result = parse_investigation(
            raw_output
        )

        existing_investigation = self.db.scalar(
            select(Investigation).where(
                Investigation.case_id == exception.case_id
            )
        )

        evidence_json = json.dumps(
            [item.model_dump() for item in result.evidence]
        )
        hypotheses_json = json.dumps(
            [item.model_dump() for item in result.hypotheses]
        )

        if existing_investigation:
            existing_investigation.status = "completed"
            existing_investigation.root_cause = result.root_cause
            existing_investigation.confidence = result.confidence
            existing_investigation.recommendation = result.recommendation
            existing_investigation.summary = result.summary
            existing_investigation.evidence_json = evidence_json
            existing_investigation.hypotheses_json = hypotheses_json
            investigation = existing_investigation
        else:
            investigation = Investigation(
                case_id=exception.case_id,
                status="completed",
                root_cause=result.root_cause,
                confidence=result.confidence,
                recommendation=result.recommendation,
                summary=result.summary,
                evidence_json=evidence_json,
                hypotheses_json=hypotheses_json,
                created_at=datetime.utcnow(),
            )
            self.db.add(investigation)

        # Clear prior evidence records for this case if re-running
        prior_evidence = list(
            self.db.scalars(
                select(InvestigationEvidence).where(
                    InvestigationEvidence.case_id == exception.case_id
                )
            ).all()
        )
        for prev in prior_evidence:
            self.db.delete(prev)

        for item in evidence:
            self.db.add(
                InvestigationEvidence(
                    case_id=exception.case_id,
                    source_type=item["source_type"],
                    source_id=str(item["source_id"]),
                    field=item["field"],
                    value=str(item["value"]),
                    created_at=datetime.utcnow(),
                )
            )

        self.db.commit()
        self.db.refresh(investigation)

        return result