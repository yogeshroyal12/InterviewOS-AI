from app.services.skill_matcher import find_skills, match_skills


def test_finds_whole_words_only() -> None:
    assert "sql" not in find_skills("nosql databases")
    assert "sql" in find_skills("SQL and PostgreSQL")


def test_separates_supported_from_not_mentioned() -> None:
    result = match_skills("Need Python, FastAPI and SQL.", "Built APIs in Python with FastAPI.")
    assert result.supported == ["fastapi", "python"]
    assert result.not_mentioned == ["sql"]


def test_empty_text_has_no_skills() -> None:
    result = match_skills("", "")
    assert result.jd_skills == []