import pytest

from app.interview.state import InterviewState, InvalidTransitionError, transition


def test_allows_normal_flow() -> None:
    assert transition(InterviewState.CREATED, InterviewState.ASKING) == InterviewState.ASKING
    assert transition(InterviewState.ASKING, InterviewState.LISTENING) == InterviewState.LISTENING


def test_blocks_completed_interview_from_restarting() -> None:
    with pytest.raises(InvalidTransitionError):
        transition(InterviewState.COMPLETED, InterviewState.ASKING)


def test_blocks_skipping_evaluation() -> None:
    with pytest.raises(InvalidTransitionError):
        transition(InterviewState.LISTENING, InterviewState.ASKING)