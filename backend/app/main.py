from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.interviews import router as interviews_router


app = FastAPI(title="InterviewOS AI", version="0.1.0")
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(interviews_router)

ALLOWED_ORIGINS = [
    "null",                    # page opened directly as a file
    "http://127.0.0.1:5500",   # VS Code Live Server
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Simple check that the server is running."""
    return {"status": "ok", "service": "interviewos-backend"}

@app.get("/")
def root() -> dict[str, str]:
    """Welcome message for the API root."""
    return {"message": "InterviewOS AI backend is running. Visit /docs for the API."}