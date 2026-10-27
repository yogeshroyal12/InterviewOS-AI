from app.evaluation.rubric import RUBRIC_VERSION, evaluate_answer


def test_full_coverage_scores_high() -> None:
    result = evaluate_answer(
        "How do you validate input in FastAPI?",
        "I use Pydantic models to validate input in FastAPI, and errors return a 422 response with details for each field.",
        ["pydantic", "validate", "422"],
    )
    assert result.completeness == 5
    assert result.needs_follow_up is False


def test_short_vague_answer_needs_follow_up() -> None:
    result = evaluate_answer("Explain indexing.", "I think maybe it is fast.", ["index", "query"])
    assert result.needs_follow_up is True
    assert any("Vague" in line for line in result.evidence)


def test_result_records_rubric_version() -> None:
    result = evaluate_answer("Q?", "An answer.", [])
    assert result.rubric_version == RUBRIC_VERSION