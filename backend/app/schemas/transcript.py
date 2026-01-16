from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID


class TranscriptBase(BaseModel):
    game_date: Optional[date] = None
    sport: Optional[str] = None
    teams: Optional[List[str]] = None
    commentators: Optional[List[str]] = None
    source: Optional[str] = None


class TranscriptCreate(TranscriptBase):
    content: Optional[str] = None  # For direct text input


class TranscriptUpdate(TranscriptBase):
    pass


class TranscriptResponse(TranscriptBase):
    id: UUID
    filename: str
    original_filename: str
    content: str
    processed: bool
    word_count: Optional[str] = None
    uploaded_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TranscriptListResponse(BaseModel):
    id: UUID
    filename: str
    original_filename: str
    sport: Optional[str] = None
    teams: Optional[List[str]] = None
    processed: bool
    word_count: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


class TranscriptUploadResponse(BaseModel):
    id: UUID
    filename: str
    message: str
