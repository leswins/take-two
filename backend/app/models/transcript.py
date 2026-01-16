import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, Date, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)

    # Metadata
    game_date = Column(Date, nullable=True)
    sport = Column(String(100), nullable=True)
    teams = Column(ARRAY(String), nullable=True)
    commentators = Column(ARRAY(String), nullable=True)
    source = Column(String(255), nullable=True)

    # Processing status
    processed = Column(Boolean, default=False)
    word_count = Column(String(50), nullable=True)

    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    analysis_results = relationship("AnalysisResult", back_populates="transcript", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Transcript(id={self.id}, filename={self.filename})>"
