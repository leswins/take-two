import uuid
import os
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models import Transcript
from app.schemas import (
    TranscriptResponse,
    TranscriptListResponse,
    TranscriptUploadResponse,
    TranscriptUpdate,
)

router = APIRouter(prefix="/transcripts", tags=["transcripts"])


def validate_file_extension(filename: str) -> bool:
    """Check if file has allowed extension."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in settings.ALLOWED_EXTENSIONS


def count_words(text: str) -> str:
    """Count words in text and return formatted string."""
    count = len(text.split())
    if count >= 1000:
        return f"{count // 1000}k"
    return str(count)


@router.post("/upload", response_model=TranscriptUploadResponse)
async def upload_transcript(
    file: UploadFile = File(...),
    game_date: Optional[date] = Form(None),
    sport: Optional[str] = Form(None),
    teams: Optional[str] = Form(None),  # Comma-separated
    commentators: Optional[str] = Form(None),  # Comma-separated
    source: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Upload a transcript file for analysis."""
    # Validate file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )

    # Read file content
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB",
        )

    # Decode content
    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text_content = content.decode("latin-1")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Unable to decode file content")

    # Parse arrays from comma-separated strings
    teams_list = [t.strip() for t in teams.split(",")] if teams else None
    commentators_list = [c.strip() for c in commentators.split(",")] if commentators else None

    # Generate unique filename
    file_id = uuid.uuid4()
    stored_filename = f"{file_id}_{file.filename}"

    # Create transcript record
    transcript = Transcript(
        id=file_id,
        filename=stored_filename,
        original_filename=file.filename,
        content=text_content,
        game_date=game_date,
        sport=sport,
        teams=teams_list,
        commentators=commentators_list,
        source=source,
        word_count=count_words(text_content),
        processed=False,
    )

    db.add(transcript)
    db.commit()
    db.refresh(transcript)

    return TranscriptUploadResponse(
        id=transcript.id,
        filename=transcript.original_filename,
        message="Transcript uploaded successfully",
    )


@router.post("/text", response_model=TranscriptUploadResponse)
async def upload_transcript_text(
    content: str = Form(...),
    title: str = Form("Untitled Transcript"),
    game_date: Optional[date] = Form(None),
    sport: Optional[str] = Form(None),
    teams: Optional[str] = Form(None),
    commentators: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Upload transcript as direct text input."""
    if not content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    # Parse arrays
    teams_list = [t.strip() for t in teams.split(",")] if teams else None
    commentators_list = [c.strip() for c in commentators.split(",")] if commentators else None

    file_id = uuid.uuid4()

    transcript = Transcript(
        id=file_id,
        filename=f"{file_id}.txt",
        original_filename=title,
        content=content,
        game_date=game_date,
        sport=sport,
        teams=teams_list,
        commentators=commentators_list,
        source=source,
        word_count=count_words(content),
        processed=False,
    )

    db.add(transcript)
    db.commit()
    db.refresh(transcript)

    return TranscriptUploadResponse(
        id=transcript.id,
        filename=transcript.original_filename,
        message="Transcript created successfully",
    )


@router.get("", response_model=List[TranscriptListResponse])
async def list_transcripts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    sport: Optional[str] = Query(None),
    processed: Optional[bool] = Query(None),
    commentator: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List all transcripts with optional filtering."""
    query = db.query(Transcript)

    if sport:
        query = query.filter(Transcript.sport == sport)
    if processed is not None:
        query = query.filter(Transcript.processed == processed)
    if commentator:
        # Filter by commentator (stored in JSONB array)
        query = query.filter(Transcript.commentators.contains([commentator]))

    transcripts = query.order_by(Transcript.uploaded_at.desc()).offset(skip).limit(limit).all()
    return transcripts


@router.get("/filters/commentators")
async def get_commentators(db: Session = Depends(get_db)):
    """Get list of unique commentators from all transcripts."""
    from sqlalchemy import func

    transcripts = db.query(Transcript).filter(Transcript.commentators.isnot(None)).all()

    commentators_set = set()
    for t in transcripts:
        if t.commentators:
            for c in t.commentators:
                commentators_set.add(c)

    return sorted(list(commentators_set))


@router.get("/filters/sports")
async def get_sports(db: Session = Depends(get_db)):
    """Get list of unique sports from all transcripts."""
    sports = db.query(Transcript.sport).filter(Transcript.sport.isnot(None)).distinct().all()
    return sorted([s[0] for s in sports if s[0]])


@router.get("/{transcript_id}", response_model=TranscriptResponse)
async def get_transcript(transcript_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a specific transcript by ID."""
    transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return transcript


@router.put("/{transcript_id}", response_model=TranscriptResponse)
async def update_transcript(
    transcript_id: uuid.UUID,
    update_data: TranscriptUpdate,
    db: Session = Depends(get_db),
):
    """Update transcript metadata."""
    transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(transcript, field, value)

    db.commit()
    db.refresh(transcript)
    return transcript


@router.delete("/{transcript_id}")
async def delete_transcript(transcript_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete a transcript and its analysis results."""
    transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    db.delete(transcript)
    db.commit()
    return {"message": "Transcript deleted successfully"}


@router.post("/{transcript_id}/analyze")
async def trigger_analysis(transcript_id: uuid.UUID, db: Session = Depends(get_db)):
    """Trigger NLP analysis for a transcript."""
    transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    # Import here to avoid circular imports
    from app.services.analysis import get_analysis_service

    try:
        analysis_service = get_analysis_service()
        results = analysis_service.analyze_and_persist(transcript_id, db)

        return {
            "message": "Analysis completed successfully",
            "transcript_id": str(transcript_id),
            "status": "completed",
            "players_found": len(results),
            "results": [
                {
                    "player_id": str(r.player_id),
                    "sentiment_label": r.sentiment_label,
                    "mention_count": r.mention_count,
                }
                for r in results
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )
