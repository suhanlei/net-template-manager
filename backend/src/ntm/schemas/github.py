from datetime import datetime
from pydantic import BaseModel


class GitLogOut(BaseModel):
    id: int
    action: str
    target_type: str
    target_id: int | None
    detail: str | None
    github_sha: str | None
    status: str
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
