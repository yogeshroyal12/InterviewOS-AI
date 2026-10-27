from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.models.user import utc_now


class InterviewRecord(Base):
    """One practice interview owned by one user."""

    __tablename__ = "interview_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    state: Mapped[str] = mapped_column(String(30))
    current_index: Mapped[int] = mapped_column(default=0)
    questions_json: Mapped[str] = mapped_column(default="[]")
    answers_json: Mapped[str] = mapped_column(default="[]")
    evaluations_json: Mapped[str] = mapped_column(default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)