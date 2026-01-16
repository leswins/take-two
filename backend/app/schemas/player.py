from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class PlayerBase(BaseModel):
    name: str
    aliases: Optional[List[str]] = []
    team: Optional[str] = None
    sport: Optional[str] = None
    position: Optional[str] = None


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    aliases: Optional[List[str]] = None
    team: Optional[str] = None
    sport: Optional[str] = None
    position: Optional[str] = None


class PlayerResponse(PlayerBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlayerListResponse(BaseModel):
    id: UUID
    name: str
    team: Optional[str] = None
    sport: Optional[str] = None

    class Config:
        from_attributes = True
