from dataclasses import dataclass

RUBRIC_VERSION = "1.0"

VAGUE_PHRASES = ["i think", "maybe", "i guess", "not sure", "somehow", "etc"]


@dataclass(frozen=True)
class Evaluation:
    rubric_version: str
    completeness: int  # 0-5
    relevance: int  # 0-5
    clarity: int  # 0-5
    overall: float  # weighted, calculated here, never taken from the model
    evidence: list[str]
    needs_follow_up: bool


def _tokens(text: str) -> set[str]:
    cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
    return set(cleaned.split())


def evaluate_answer(question: str, answer: str, expected_terms: list[str]) -> Evaluation:
    """Score one answer against the rubric. Scores are computed in Python."""
    words = answer.split()
    answer_tokens = _tokens(answer)
    question_tokens = _tokens(question)
    evidence: list[str] = []

    # Completeness: how many expected concepts the answer mentions.
    hits = [t for t in expected_terms if t.lower() in answer_tokens]
    if expected_terms:
        completeness = round(5 * len(hits) / len(expected_terms))
    else:
        completeness = 5 if len(words) >= 30 else 3 if len(words) >= 15 else 1
    evidence.append(f"Mentions {len(hits)} of {len(expected_terms)} expected concepts")

    # Relevance: overlap between the answer and the question's own words.
    overlap = len(answer_tokens & question_tokens) / max(len(question_tokens), 1)
    relevance = min(5, round(overlap * 10))
    evidence.append(f"Shares {round(overlap * 100)}% of key words with the question")

    # Clarity: penalize very short answers and vague wording.
    vague = [p for p in VAGUE_PHRASES if p in answer.lower()]
    clarity = 5
    if len(words) < 15:
        clarity -= 2
    clarity -= min(3, len(vague))
    clarity = max(0, clarity)
    if vague:
        evidence.append(f"Vague wording: {', '.join(vague)}")

    overall = round(0.5 * completeness + 0.3 * relevance + 0.2 * clarity, 2)
    return Evaluation(
        rubric_version=RUBRIC_VERSION,
        completeness=completeness,
        relevance=relevance,
        clarity=clarity,
        overall=overall,
        evidence=evidence,
        needs_follow_up=overall < 2.5 or len(words) < 15,
    )