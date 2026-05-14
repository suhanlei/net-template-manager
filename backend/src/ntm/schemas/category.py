from datetime import datetime
from pydantic import BaseModel, Field


# --- Category ---
class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=50)
    slug: str = Field(..., max_length=50)
    description: str | None = None
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, max_length=50)
    slug: str | None = Field(None, max_length=50)
    description: str | None = None
    sort_order: int | None = None


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    sort_order: int
    created_at: datetime
    updated_at: datetime
    template_count: int = 0

    model_config = {"from_attributes": True}
