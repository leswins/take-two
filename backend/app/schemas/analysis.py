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
    top_phrases: List[PhraseDetail] = []
    transcript_count: int


class BiasIndicatorDetail(BaseModel):
    category: str
    description: str
    score: float
    weight: float
    evidence: List[str] = []


class PlayerBiasScore(BaseModel):
    player_id: UUID
    player_name: str
    bias_score: float
    bias_level: str  # minimal, low, moderate, high, severe
    confidence: float
    indicators: List[BiasIndicatorDetail] = []


class PlayerComparisonItem(BaseModel):
    player_id: str
    player_name: str
    rank: int
    bias_score: float
    bias_level: str
    sentiment_score: Optional[float] = None
    mention_count: int = 0


class ComparativeAnalysisResponse(BaseModel):
    fairness_score: float
    most_favored: Optional[str] = None
    least_favored: Optional[str] = None
    disparity_score: float
    players: List[PlayerComparisonItem] = []


class TranscriptBiasAnalysis(BaseModel):
    transcript_id: UUID
    players_analyzed: int
    comparative_analysis: Optional[ComparativeAnalysisResponse] = None
    player_scores: List[PlayerBiasScore] = []
