from dataclasses import dataclass, field

from app.interview.state import InterviewState, transition

MAX_FOLLOW_UPS_PER_QUESTION = 2


@dataclass
class InterviewSession:
    questions: list[str]
    max_questions: int = 5
    state: InterviewState = InterviewState.CREATED
    current_index: int = 0
    follow_ups_used: int = 0
    answers: list[str] = field(default_factory=list)
    evaluations: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.questions:
            raise ValueError("An interview needs at least one question.")
        self.questions = self.questions[: self.max_questions]

    @property
    def current_question(self) -> str | None:
        if self.current_index >= len(self.questions):
            return None
        return self.questions[self.current_index]

    def start(self) -> str:
        self.state = transition(self.state, InterviewState.ASKING)
        return self.current_question or ""

    def submit_answer(self, answer: str) -> None:
        """Record the candidate's answer. Blank answers are rejected, not counted."""
        if not answer.strip():
            raise ValueError("Answer cannot be empty.")
        self.state = transition(self.state, InterviewState.LISTENING)
        self.answers.append(answer.strip())
        self.state = transition(self.state, InterviewState.EVALUATING)

    def next_step(self, needs_follow_up: bool) -> str:
        """Move on to a follow-up or the next question, or finish the interview."""
        if needs_follow_up and self.follow_ups_used < MAX_FOLLOW_UPS_PER_QUESTION:
            self.follow_ups_used += 1
            self.state = transition(self.state, InterviewState.FOLLOW_UP)
            return "follow_up"
        self.follow_ups_used = 0
        self.current_index += 1
        if self.current_question is None:
            self.state = transition(self.state, InterviewState.NEXT_QUESTION)
            self.state = transition(self.state, InterviewState.COMPLETED)
            return "completed"
        self.state = transition(self.state, InterviewState.NEXT_QUESTION)
        return "next_question"

    def ask_next(self) -> str:
        """Ask the current question again (after a follow-up or next question)."""
        self.state = transition(self.state, InterviewState.ASKING)
        return self.current_question or ""