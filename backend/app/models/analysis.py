import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    transcript_id = Column(UUID(as_uuid=True), ForeignKey("transcripts.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)

    # Sentiment metrics
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    sentiment_label = Column(String(20), nullable=True)  # positive, negative, neutral
    confidence = Column(Float, nullable=True)  # 0 to 1

    # Mention tracking
    mention_count = Column(Integer, default=0)

    # Detailed analysis (stored as JSON)
    adjectives = Column(JSONB, default=list)  # [{"word": str, "count": int, "sentiment": float}]
    phrases = Column(JSONB, default=list)  # [{"phrase": str, "count": int, "context": str}]
    excerpts = Column(JSONB, default=list)  # [{"text": str, "sentiment": float, "position": int}]

    # Timestamps
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    transcript = relationship("Transcript", back_populates="analysis_results")
    player = relationship("Player", back_populates="analysis_results")

    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, player_id={self.player_id}, sentiment={self.sentiment_label})>"
