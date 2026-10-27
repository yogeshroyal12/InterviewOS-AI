import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.api.interviews import _get_owned_record
from app.db.database import get_db
from app.models.user import User
from app.schemas.report import InterviewReport, QuestionScore

router = APIRouter(prefix="/api/v1/interviews", tags=["reports"])

LIMITATIONS = (
    "Scores come from a rule-based rubric that checks keyword coverage, "
    "relevance, and wording. They estimate practice performance only and "
    "do not predict hiring outcomes."
)


@router.get("/{interview_id}/report", response_model=InterviewReport)
def get_report(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewReport:
    record = _get_owned_record(db, interview_id, current_user)
    items = [QuestionScore(**e) for e in json.loads(record.evaluations_json)]
    overall = round(sum(i.overall for i in items) / len(items), 2) if items else 0.0
    ranked = sorted(items, key=lambda i: i.overall)
    return InterviewReport(
        interview_id=record.id,
        state=record.state,
        questions_evaluated=len(items),
        overall_score=overall,
        strongest=ranked[-1] if ranked else None,
        weakest=ranked[0] if ranked else None,
        items=items,
        limitations=LIMITATIONS,
    )