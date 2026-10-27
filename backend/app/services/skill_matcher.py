import re
from dataclasses import dataclass, field

KNOWN_SKILLS = [
    "python", "fastapi", "sql", "postgresql", "docker", "git",
    "machine learning", "deep learning", "nlp", "pytorch", "tensorflow",
    "pandas", "scikit-learn", "langchain", "rest api", "pydantic",
]


@dataclass
class SkillMatchResult:
    jd_skills: list[str] = field(default_factory=list)
    supported: list[str] = field(default_factory=list)
    not_mentioned: list[str] = field(default_factory=list)


def find_skills(text: str) -> set[str]:
    """Return the known skills that appear as whole words in the text."""
    lowered = text.lower()
    found = set()
    for skill in KNOWN_SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, lowered):
            found.add(skill)
    return found


def match_skills(jd_text: str, resume_text: str) -> SkillMatchResult:
    """Compare JD skills with the resume. 'Not mentioned' is not the same as 'missing'."""
    jd_skills = sorted(find_skills(jd_text))
    resume_skills = find_skills(resume_text)
    return SkillMatchResult(
        jd_skills=jd_skills,
        supported=[s for s in jd_skills if s in resume_skills],
        not_mentioned=[s for s in jd_skills if s not in resume_skills],
    )