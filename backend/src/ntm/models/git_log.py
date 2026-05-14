from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ntm.core.database import Base
from ntm.models.base import TimestampMixin


class GitLog(Base, TimestampMixin):
    __tablename__ = "git_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # commit, tag, release, sync
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)  # template, release
    target_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    github_sha: Mapped[str | None] = mapped_column(String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="success", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
