from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


class AdjectiveDetail(BaseModel):
    word: str
    count: int
    sentiment: Optional[float] = None


class PhraseDetail(BaseModel):
    phrase: str
    count: int
    context: Optional[str] = None


class ExcerptDetail(BaseModel):
    text: str
    sentiment: float
    position: Optional[int] = None


class AnalysisResultBase(BaseModel):
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    confidence: Optional[float] = None
    mention_count: int = 0


class AnalysisResultResponse(AnalysisResultBase):
    id: UUID
    transcript_id: UUID
    player_id: UUID
    adjectives: List[AdjectiveDetail] = []
    phrases: List[PhraseDetail] = []
    excerpts: List[ExcerptDetail] = []
    analyzed_at: datetime

    class Config:
        from_attributes = True


class PlayerAnalysisSummary(BaseModel):
    player_id: UUID
    player_name: str
    total_mentions: int
    average_sentiment: Optional[float] = None
    sentiment_label: Optional[str] = None
    top_adjectives: List[AdjectiveDetail] = []
    transcript_count: int
