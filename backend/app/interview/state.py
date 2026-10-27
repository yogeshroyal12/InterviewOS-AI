from enum import Enum


class InterviewState(str, Enum):
    CREATED = "created"
    ASKING = "asking"
    LISTENING = "listening"
    EVALUATING = "evaluating"
    FOLLOW_UP = "follow_up"
    NEXT_QUESTION = "next_question"
    PAUSED = "paused"
    ERROR_RECOVERY = "error_recovery"
    COMPLETED = "completed"


# The only legal moves. Anything else is a bug and must raise an error.
ALLOWED_TRANSITIONS: dict[InterviewState, set[InterviewState]] = {
    InterviewState.CREATED: {InterviewState.ASKING},
    InterviewState.ASKING: {InterviewState.LISTENING, InterviewState.ERROR_RECOVERY, InterviewState.PAUSED},
    InterviewState.LISTENING: {InterviewState.EVALUATING, InterviewState.PAUSED, InterviewState.COMPLETED},
    InterviewState.EVALUATING: {InterviewState.FOLLOW_UP, InterviewState.NEXT_QUESTION, InterviewState.ERROR_RECOVERY},
    InterviewState.FOLLOW_UP: {InterviewState.ASKING},
    InterviewState.NEXT_QUESTION: {InterviewState.ASKING, InterviewState.COMPLETED},
    InterviewState.PAUSED: {InterviewState.ASKING, InterviewState.LISTENING, InterviewState.COMPLETED},
    InterviewState.ERROR_RECOVERY: {InterviewState.ASKING, InterviewState.LISTENING, InterviewState.COMPLETED},
    InterviewState.COMPLETED: set(),
}


class InvalidTransitionError(RuntimeError):
    """Raised when the interview tries a move that is not allowed."""


def transition(current: InterviewState, target: InterviewState) -> InterviewState:
    """Return the new state if the move is allowed, otherwise raise."""
    if target not in ALLOWED_TRANSITIONS[current]:
        raise InvalidTransitionError(f"Cannot move from {current.value} to {target.value}")
    return target