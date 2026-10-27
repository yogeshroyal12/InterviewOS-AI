from pydantic import BaseModel, Field


class InterviewStartRequest(BaseModel):
    job_document_id: int
    resume_document_id: int


class AnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=4000)


class InterviewResponse(BaseModel):
    id: int
    state: str
    current_question: str | None
    follow_ups_used: int
    answers_given: int
    completed: bool