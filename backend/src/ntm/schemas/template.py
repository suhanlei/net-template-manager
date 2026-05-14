from datetime import datetime
from pydantic import BaseModel, Field


# --- Template ---
class TemplateCreate(BaseModel):
    name: str = Field(..., max_length=200)
    filename: str = Field(..., max_length=200)
    category_id: int
    github_path: str | None = None
    status: str = "draft"


class TemplateUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    filename: str | None = Field(None, max_length=200)
    category_id: int | None = None
    github_path: str | None = None
    status: str | None = None


class TemplateOut(BaseModel):
    id: int
    name: str
    filename: str
    category_id: int
    category_name: str = ""
    current_version: str | None
    status: str
    github_path: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TemplateDetailOut(TemplateOut):
    versions: list["TemplateVersionOut"] = []


# --- TemplateVersion ---
class TemplateVersionCreate(BaseModel):
    content: str
    change_type: str = Field(..., pattern="^(major|minor|patch)$")
    commit_message: str | None = None
    diff_summary: str | None = None
    created_by: str = "anonymous"


class TemplateVersionOut(BaseModel):
    id: int
    template_id: int
    version: str
    content_hash: str
    change_type: str
    commit_message: str | None
    github_commit_sha: str | None
    status: str
    diff_summary: str | None
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TemplateVersionContentOut(TemplateVersionOut):
    content: str


class DiffOut(BaseModel):
    template_id: int
    version1: str
    version2: str
    unified_diff: str
