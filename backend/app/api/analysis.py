import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models import AnalysisResult, Player, Transcript
from app.schemas import (
    AnalysisResultResponse,
    PlayerAnalysisSummary,
    PlayerBiasScore,
    BiasIndicatorDetail,
    ComparativeAnalysisResponse,
    PlayerComparisonItem,
    TranscriptBiasAnalysis,
)
from app.services.analysis import get_analysis_service

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
            top_phrases=[],
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

    # Aggregate phrases
    phrase_counts = {}
    for result in results:
        for phrase in result.phrases or []:
            p_text = phrase.get("phrase", "")
            if p_text:
                if p_text not in phrase_counts:
                    phrase_counts[p_text] = {"phrase": p_text, "count": 0, "context": phrase.get("context", "")}
                phrase_counts[p_text]["count"] += phrase.get("count", 1)

    top_phrases = sorted(phrase_counts.values(), key=lambda x: x["count"], reverse=True)[:10]

    return PlayerAnalysisSummary(
        player_id=player_id,
        player_name=player.name,
        total_mentions=total_mentions,
        average_sentiment=avg_sentiment,
        sentiment_label=sentiment_label,
        top_adjectives=top_adjectives,
        top_phrases=top_phrases,
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


@router.get("/transcript/{transcript_id}/bias", response_model=TranscriptBiasAnalysis)
async def get_transcript_bias_analysis(transcript_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get bias analysis for all players in a transcript."""
    transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    if not transcript.processed:
        raise HTTPException(status_code=400, detail="Transcript has not been analyzed yet")

    # Get analysis results for the transcript
    results = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.transcript_id == transcript_id)
        .all()
    )

    if not results:
        return TranscriptBiasAnalysis(
            transcript_id=transcript_id,
            players_analyzed=0,
            comparative_analysis=None,
            player_scores=[],
        )

    # Run live bias analysis
    service = get_analysis_service(db)
    analysis_result = service.analyze_transcript(
        str(transcript_id),
        transcript.content,
    )

    # Build player bias scores
    player_scores = []
    for player_result in analysis_result.player_results:
        player = db.query(Player).filter(Player.name.ilike(player_result.player_name)).first()
        player_id = player.id if player else uuid.uuid4()

        indicators = [
            BiasIndicatorDetail(
                category=ind["category"],
                description=ind["description"],
                score=ind["score"],
                weight=ind["weight"],
                evidence=ind.get("evidence", []),
            )
            for ind in player_result.bias_indicators
        ]

        player_scores.append(PlayerBiasScore(
            player_id=player_id,
            player_name=player_result.player_name,
            bias_score=player_result.bias_score or 0.0,
            bias_level=player_result.bias_level or "minimal",
            confidence=player_result.confidence,
            indicators=indicators,
        ))

    # Build comparative analysis
    comparative = None
    if analysis_result.comparative_analysis:
        comp = analysis_result.comparative_analysis
        players = [
            PlayerComparisonItem(
                player_id=str(p.get("player_id", "")),
                player_name=p["player_name"],
                rank=p["rank"],
                bias_score=p["bias_score"],
                bias_level=p["bias_level"],
                sentiment_score=None,
                mention_count=0,
            )
            for p in comp.get("player_rankings", [])
        ]
        comparative = ComparativeAnalysisResponse(
            fairness_score=comp.get("fairness_score", 0.0),
            most_favored=comp.get("most_favored"),
            least_favored=comp.get("least_favored"),
            disparity_score=comp.get("disparity_score", 0.0),
            players=players,
        )

    return TranscriptBiasAnalysis(
        transcript_id=transcript_id,
        players_analyzed=len(player_scores),
        comparative_analysis=comparative,
        player_scores=player_scores,
    )


@router.get("/compare/bias")
async def compare_players_bias(
    player_ids: str = Query(..., description="Comma-separated player IDs"),
    db: Session = Depends(get_db),
):
    """Compare bias scores across multiple players from all their transcripts."""
    ids = [uuid.UUID(pid.strip()) for pid in player_ids.split(",")]

    from app.services.nlp.bias import BiasScore, BiasLevel, BiasIndicator, bias_scorer

    player_bias_scores = []

    for player_id in ids:
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            continue

        results = db.query(AnalysisResult).filter(AnalysisResult.player_id == player_id).all()
        if not results:
            continue

        # Aggregate sentiment data across all transcripts
        total_mentions = sum(r.mention_count for r in results)
        sentiments = [r.sentiment_score for r in results if r.sentiment_score is not None]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0

        # Aggregate adjectives sentiment data
        adjective_sentiments = []
        for result in results:
            for adj in result.adjectives or []:
                adjective_sentiments.append({
                    "word": adj.get("word", ""),
                    "sentiment": adj.get("sentiment", "neutral"),
                })

        # Calculate sentiment distribution
        positive = sum(1 for r in results if r.sentiment_label == "positive")
        negative = sum(1 for r in results if r.sentiment_label == "negative")
        neutral = sum(1 for r in results if r.sentiment_label == "neutral")

        sentiment_distribution = {
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
        }

        # Get excerpt sentiments
        excerpt_sentiments = []
        for result in results:
            for exc in result.excerpts or []:
                if exc.get("sentiment") is not None:
                    excerpt_sentiments.append(exc["sentiment"])

        # Calculate bias score
        bias_result = bias_scorer.calculate_bias_score(
            player_name=player.name,
            sentiment_score=avg_sentiment,
            sentiment_distribution=sentiment_distribution,
            adjective_sentiments=adjective_sentiments,
            mention_count=total_mentions,
            excerpt_sentiments=excerpt_sentiments,
        )

        player_bias_scores.append(bias_result)

    if len(player_bias_scores) < 2:
        return {
            "error": "Need at least 2 players with analysis data to compare",
            "players_found": len(player_bias_scores),
        }

    # Run comparative analysis
    comparison = bias_scorer.compare_players(player_bias_scores)

    return {
        "fairness_score": comparison.fairness_score,
        "most_favored": comparison.most_favored,
        "least_favored": comparison.least_favored,
        "disparity_score": comparison.disparity_score,
        "player_rankings": [
            {
                "player_name": p.player_name,
                "rank": p.comparative_rank,
                "bias_score": p.overall_score,
                "bias_level": p.bias_level.value,
                "confidence": p.confidence,
            }
            for p in comparison.players
        ],
    }
