import pytest

from app.interview.session import InterviewSession
from app.interview.state import InterviewState

def test_completes_after_last_question() -> None:
    session = InterviewSession(questions=["Q1", "Q2"])
    session.start()
    session.submit_answer("A1")
    assert session.next_step(False) == "next_question"
    session.ask_next()
    session.submit_answer("A2")
    assert session.next_step(False) == "completed"
    assert session.state == InterviewState.COMPLETED


def test_follow_up_is_limited() -> None:
    session = InterviewSession(questions=["Q1"])
    session.start()
    for _ in range(2):
        session.submit_answer("vague")
        assert session.next_step(True) == "follow_up"
        session.ask_next()
    session.submit_answer("still vague")
    assert session.next_step(True) == "completed"


def test_blank_answer_is_rejected() -> None:
    session = InterviewSession(questions=["Q1"])
    session.start()
    with pytest.raises(ValueError):
        session.submit_answer("   ")


def test_empty_question_list_is_rejected() -> None:
    with pytest.raises(ValueError):
        InterviewSession(questions=[])