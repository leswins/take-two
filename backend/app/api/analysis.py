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


@router.get("/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get aggregated statistics for the dashboard."""
    # Count totals
    transcript_count = db.query(Transcript).count()
    analyzed_count = db.query(Transcript).filter(Transcript.processed == True).count()
    player_count = db.query(Player).count()

    # Get all analysis results for sentiment distribution
    results = db.query(AnalysisResult).all()

    positive_count = sum(1 for r in results if r.sentiment_label == "positive")
    negative_count = sum(1 for r in results if r.sentiment_label == "negative")
    neutral_count = sum(1 for r in results if r.sentiment_label == "neutral")

    # Get top players by mentions
    player_mentions = {}
    player_sentiments = {}
    for result in results:
        pid = str(result.player_id)
        if pid not in player_mentions:
            player_mentions[pid] = 0
            player_sentiments[pid] = []
        player_mentions[pid] += result.mention_count or 0
        if result.sentiment_score is not None:
            player_sentiments[pid].append(result.sentiment_score)

    # Build top players list
    top_players = []
    players = db.query(Player).all()
    player_map = {str(p.id): p for p in players}

    for pid, mentions in sorted(player_mentions.items(), key=lambda x: x[1], reverse=True)[:5]:
        player = player_map.get(pid)
        if player:
            sentiments = player_sentiments.get(pid, [])
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            top_players.append({
                "id": pid,
                "name": player.name,
                "mentions": mentions,
                "sentiment_score": avg_sentiment,
                "sentiment_label": "positive" if avg_sentiment > 0.1 else "negative" if avg_sentiment < -0.1 else "neutral",
            })

    # Aggregate all adjectives
    all_adjectives = {}
    for result in results:
        for adj in result.adjectives or []:
            word = adj.get("word", "")
            if word:
                if word not in all_adjectives:
                    all_adjectives[word] = {"word": word, "count": 0, "sentiment": adj.get("sentiment", "neutral")}
                all_adjectives[word]["count"] += adj.get("count", 1)

    top_adjectives = sorted(all_adjectives.values(), key=lambda x: x["count"], reverse=True)[:15]

    return {
        "totals": {
            "transcripts": transcript_count,
            "analyzed": analyzed_count,
            "players": player_count,
            "total_analyses": len(results),
        },
        "sentiment_distribution": {
            "positive": positive_count,
            "negative": negative_count,
            "neutral": neutral_count,
        },
        "top_players": top_players,
        "top_adjectives": top_adjectives,
    }
