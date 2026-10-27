import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import interviews as interviews_module
from app.db.database import Base, get_db
from app.main import app
from app.models import document, interview, user  # noqa: F401  (register tables)


@pytest.fixture()
def client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    # Force the fallback question bank so tests never call Groq.
    monkeypatch.setattr(
        interviews_module,
        "generate_questions",
        lambda jd, resume: [
            {"question": "Q1", "concepts": ["fastapi"]},
            {"question": "Q2", "concepts": ["pytest"]},
        ],
    )    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _register_and_login(client, email):
    client.post("/api/v1/auth/register", json={"email": email, "password": "secret123"})
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "secret123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _upload(client, headers, doc_type, text):
    from io import BytesIO
    from docx import Document as DocxDocument

    doc = DocxDocument()
    doc.add_paragraph(text)
    buffer = BytesIO()
    doc.save(buffer)
    response = client.post(
        "/api/v1/documents/upload",
        headers=headers,
        data={"document_type": doc_type},
        files={"file": ("doc.docx", buffer.getvalue(), "application/octet-stream")},
    )
    return response.json()["id"]


def test_start_and_answer_flow(client) -> None:
    headers = _register_and_login(client, "a@example.com")
    jd_id = _upload(client, headers, "job_description", "Python and FastAPI role.")
    resume_id = _upload(client, headers, "resume", "Built APIs in Python.")

    started = client.post(
        "/api/v1/interviews", headers=headers,
        json={"job_document_id": jd_id, "resume_document_id": resume_id},
    )
    assert started.status_code == 201
    body = started.json()
    assert body["current_question"] == "Q1"
    assert body["answers_given"] == 0

    answered = client.post(
        f"/api/v1/interviews/{body['id']}/answers",
        headers=headers,
        json={"answer": "I used FastAPI with validation and tests " * 5},
    )
    assert answered.status_code == 200
    assert answered.json()["answers_given"] == 1
    assert answered.json()["current_question"] == "Q2"


def test_other_user_cannot_read_interview(client) -> None:
    owner = _register_and_login(client, "owner@example.com")
    other = _register_and_login(client, "other@example.com")
    jd_id = _upload(client, owner, "job_description", "Python role.")
    resume_id = _upload(client, owner, "resume", "Python dev.")
    interview_id = client.post(
        "/api/v1/interviews", headers=owner,
        json={"job_document_id": jd_id, "resume_document_id": resume_id},
    ).json()["id"]

    response = client.get(f"/api/v1/interviews/{interview_id}", headers=other)
    assert response.status_code == 404


def test_cannot_use_another_users_document(client) -> None:
    owner = _register_and_login(client, "doc-owner@example.com")
    other = _register_and_login(client, "doc-thief@example.com")
    jd_id = _upload(client, owner, "job_description", "Python role.")
    resume_id = _upload(client, other, "resume", "Python dev.")

    response = client.post(
        "/api/v1/interviews", headers=other,
        json={"job_document_id": jd_id, "resume_document_id": resume_id},
    )
    assert response.status_code == 404


def test_requires_login(client) -> None:
    response = client.get("/api/v1/interviews/1")
    assert response.status_code == 401