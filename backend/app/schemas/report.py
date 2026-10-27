from pydantic import BaseModel


class QuestionScore(BaseModel):
    question: str
    answer: str
    overall: float
    completeness: int
    relevance: int
    clarity: int
    evidence: list[str]


class InterviewReport(BaseModel):
    interview_id: int
    state: str
    questions_evaluated: int
    overall_score: float
    strongest: QuestionScore | None
    weakest: QuestionScore | None
    items: list[QuestionScore]
    limitations: str