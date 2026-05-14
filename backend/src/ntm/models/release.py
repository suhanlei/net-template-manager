from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ntm.core.database import Base
from ntm.models.base import TimestampMixin


class Release(Base, TimestampMixin):
    __tablename__ = "releases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    changelog: Mapped[str | None] = mapped_column(Text, nullable=True)
    release_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    github_tag: Mapped[str | None] = mapped_column(String(100), nullable=True)
    github_release_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    snapshots: Mapped[list["ReleaseTemplateSnapshot"]] = relationship(
        back_populates="release", lazy="selectin", cascade="all, delete-orphan"
    )


class ReleaseTemplateSnapshot(Base, TimestampMixin):
    __tablename__ = "release_template_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    release_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("releases.id"), nullable=False
    )
    template_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("templates.id"), nullable=False
    )
    template_version_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("template_versions.id"), nullable=False
    )

    release: Mapped["Release"] = relationship(back_populates="snapshots")
    template: Mapped["Template"] = relationship()  # noqa: F821
    template_version: Mapped["TemplateVersion"] = relationship()  # noqa: F821

    __table_args__ = (
        UniqueConstraint("release_id", "template_id", name="uq_release_template"),
    )
