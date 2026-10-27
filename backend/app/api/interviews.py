import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.database import get_db
from app.evaluation.rubric import evaluate_answer
from app.interview.questions import generate_questions
from app.interview.session import InterviewSession
from app.interview.state import InterviewState
from app.models.document import Document
from app.models.interview import InterviewRecord
from app.models.user import User
from app.schemas.interview import AnswerRequest, InterviewResponse, InterviewStartRequest

router = APIRouter(prefix="/api/v1/interviews", tags=["interviews"])


def _owned_document(db: Session, doc_id: int, user: User, expected_type: str) -> Document:
    document = db.get(Document, doc_id)
    if document is None or document.user_id != user.id or document.document_type != expected_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


def _load(record: InterviewRecord) -> InterviewSession:
    session = InterviewSession(questions=json.loads(record.questions_json))
    session.state = InterviewState(record.state)
    session.current_index = record.current_index
    session.answers = json.loads(record.answers_json)
    session.evaluations = json.loads(record.evaluations_json)
    return session


def _save(db: Session, record: InterviewRecord, session: InterviewSession) -> None:
    record.state = session.state.value
    record.current_index = session.current_index
    record.answers_json = json.dumps(session.answers)
    record.evaluations_json = json.dumps(session.evaluations)
    db.commit()


def _response(record: InterviewRecord, session: InterviewSession) -> InterviewResponse:
    return InterviewResponse(
        id=record.id,
        state=session.state.value,
        current_question=session.current_question,
        follow_ups_used=session.follow_ups_used,
        answers_given=len(session.answers),
        completed=session.state == InterviewState.COMPLETED,
    )


def _get_owned_record(db: Session, interview_id: int, user: User) -> InterviewRecord:
    record = db.get(InterviewRecord, interview_id)
    if record is None or record.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")
    return record


@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
def start_interview(
    payload: InterviewStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewResponse:
    job = _owned_document(db, payload.job_document_id, current_user, "job_description")
    resume = _owned_document(db, payload.resume_document_id, current_user, "resume")
    items = generate_questions(job.extracted_text, resume.extracted_text)
    questions = [item["question"] for item in items]
    concepts = [item["concepts"] for item in items]

    session = InterviewSession(questions=questions)
    session.start()
    record = InterviewRecord(
        user_id=current_user.id,
        state=session.state.value,
        questions_json=json.dumps(questions),
        concepts_json=json.dumps(concepts),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    _save(db, record, session)
    return _response(record, session)


@router.post("/{interview_id}/answers", response_model=InterviewResponse)
def submit_answer(
    interview_id: int,
    payload: AnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewResponse:
    record = _get_owned_record(db, interview_id, current_user)
    session = _load(record)
    question = session.current_question or ""
    expected = json.loads(record.concepts_json)[session.current_index]
    session.submit_answer(payload.answer)
    evaluation = evaluate_answer(question, payload.answer, expected)
    session.evaluations.append({
        "question": question,
        "answer": payload.answer,
        "completeness": evaluation.completeness,
        "relevance": evaluation.relevance,
        "clarity": evaluation.clarity,
        "overall": evaluation.overall,
        "evidence": evaluation.evidence,
        "rubric_version": evaluation.rubric_version,
    })
    step = session.next_step(evaluation.needs_follow_up)
    if step != "completed":
        session.ask_next()
    _save(db, record, session)
    return _response(record, session)


@router.get("/{interview_id}", response_model=InterviewResponse)
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewResponse:
    record = _get_owned_record(db, interview_id, current_user)
    return _response(record, _load(record))