from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional


class CardBase(BaseModel):
    title: str
    description: Optional[str] = None
    check: bool = False


class CardCreate(CardBase):
    list_id: int
    due_date: Optional[datetime] = None
    tags: Optional[list[str]] = []


class CardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    check: Optional[bool] = None
    due_date: Optional[datetime] = None
    list_id: Optional[int] = None


class CardMove(BaseModel):
    list_id: int
    position: Optional[int] = None


class CardResponse(CardBase):
    id: int
    list_id: int
    position: int = 0
    due_date: Optional[datetime] = None
    tags: Optional[list[str]] = []

    @field_validator("tags", mode="before")
    @classmethod
    def _tag_names(cls, v):
        return [t if isinstance(t, str) else t.name for t in (v or [])]

    class Config:
        from_attributes = True

class CardSearchParams(BaseModel):
    q: Optional[str] = None
    tag_id: Optional[list[int]] = None
    due_before: Optional[datetime] = None
    due_after: Optional[datetime] = None