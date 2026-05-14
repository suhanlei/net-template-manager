from datetime import datetime
from pydantic import BaseModel, Field


# --- Release ---
class ReleaseCreate(BaseModel):
    name: str = Field(..., max_length=200)
    version: str = Field(..., max_length=20)
    release_notes: str | None = None


class ReleaseUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    changelog: str | None = None
    release_notes: str | None = None


class ReleaseTemplateAdd(BaseModel):
    template_id: int
    template_version_id: int


class ReleaseOut(BaseModel):
    id: int
    name: str
    version: str
    status: str
    changelog: str | None
    release_notes: str | None
    github_tag: str | None
    github_release_url: str | None
    created_at: datetime
    updated_at: datetime
    template_count: int = 0

    model_config = {"from_attributes": True}


class ReleaseDetailOut(ReleaseOut):
    snapshots: list["SnapshotOut"] = []


# --- Snapshot ---
class SnapshotOut(BaseModel):
    id: int
    release_id: int
    template_id: int
    template_version_id: int
    template_name: str = ""
    template_filename: str = ""
    version: str = ""

    model_config = {"from_attributes": True}
