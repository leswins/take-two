import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models import AnalysisResult, Player, Transcript
from app.schemas import AnalysisResultResponse, PlayerAnalysisSummary

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/player/{player_id}", response_model=List[AnalysisResultResponse])
async def get_player_analysis(
    player_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get all analysis results for a specific player."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    results = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.player_id == player_id)
        .order_by(AnalysisResult.analyzed_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return results


@router.get("/player/{player_id}/summary", response_model=PlayerAnalysisSummary)
async def get_player_summary(player_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get aggregated analysis summary for a player."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Aggregate stats
    results = db.query(AnalysisResult).filter(AnalysisResult.player_id == player_id).all()

    if not results:
        return PlayerAnalysisSummary(
            player_id=player_id,
            player_name=player.name,
            total_mentions=0,
            average_sentiment=None,
            sentiment_label=None,
            top_adjectives=[],
            transcript_count=0,
        )

    total_mentions = sum(r.mention_count for r in results)
    sentiments = [r.sentiment_score for r in results if r.sentiment_score is not None]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else None

    # Determine overall sentiment label
    sentiment_label = None
    if avg_sentiment is not None:
        if avg_sentiment > 0.1:
            sentiment_label = "positive"
        elif avg_sentiment < -0.1:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"

    # Aggregate adjectives
    adjective_counts = {}
    for result in results:
        for adj in result.adjectives or []:
            word = adj.get("word", "")
            if word:
                if word not in adjective_counts:
                    adjective_counts[word] = {"word": word, "count": 0, "sentiment": 0}
                adjective_counts[word]["count"] += adj.get("count", 1)

    top_adjectives = sorted(adjective_counts.values(), key=lambda x: x["count"], reverse=True)[:10]

    return PlayerAnalysisSummary(
        player_id=player_id,
        player_name=player.name,
        total_mentions=total_mentions,
        average_sentiment=avg_sentiment,
        sentiment_label=sentiment_label,
        top_adjectives=top_adjectives,
        transcript_count=len(results),
    )


@router.get("/transcript/{transcript_id}", response_model=List[AnalysisResultResponse])
async def get_transcript_analysis(transcript_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get all analysis results for a specific transcript."""
    transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    results = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.transcript_id == transcript_id)
        .all()
    )
    return results


@router.get("/compare")
async def compare_players(
    player_ids: str = Query(..., description="Comma-separated player IDs"),
    db: Session = Depends(get_db),
):
    """Compare analysis results across multiple players."""
    ids = [uuid.UUID(pid.strip()) for pid in player_ids.split(",")]

    comparisons = []
    for player_id in ids:
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            continue

        results = db.query(AnalysisResult).filter(AnalysisResult.player_id == player_id).all()

        total_mentions = sum(r.mention_count for r in results)
        sentiments = [r.sentiment_score for r in results if r.sentiment_score is not None]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else None

        comparisons.append({
            "player_id": str(player_id),
            "player_name": player.name,
            "total_mentions": total_mentions,
            "average_sentiment": avg_sentiment,
            "transcript_count": len(results),
        })

    return {"comparisons": comparisons}
