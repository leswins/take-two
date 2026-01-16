"""
Analysis orchestration service.
Coordinates NLP pipeline components to analyze sports commentary transcripts.
"""

import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict

from sqlalchemy.orm import Session

from app.models import Transcript, Player, AnalysisResult
from app.services.nlp import (
    preprocessor,
    entity_recognizer,
    sentiment_analyzer,
    adjective_extractor,
    phrase_detector,
    bias_scorer,
    ProcessedText,
    IdentifiedPlayer,
    SentimentLabel,
    BiasScore,
    ComparativeBiasAnalysis,
)


@dataclass
class PlayerAnalysisResult:
    """Complete analysis result for a single player."""
    player_name: str
    player_id: Optional[str] = None
    mention_count: int = 0
    sentiment_score: float = 0.0
    sentiment_label: str = "neutral"
    confidence: float = 0.0
    adjectives: List[Dict[str, Any]] = field(default_factory=list)
    phrases: List[Dict[str, Any]] = field(default_factory=list)
    excerpts: List[Dict[str, Any]] = field(default_factory=list)
    bias_score: Optional[float] = None
    bias_level: Optional[str] = None
    bias_indicators: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TranscriptAnalysisResult:
    """Complete analysis result for a transcript."""
    transcript_id: str
    processed_text: ProcessedText
    players_found: List[str]
    player_results: List[PlayerAnalysisResult]
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)
    comparative_analysis: Optional[Dict[str, Any]] = None


class AnalysisService:
    """
    Main service for analyzing sports commentary transcripts.
    Orchestrates preprocessing, NER, sentiment analysis, adjective extraction,
    phrase detection, and bias scoring.
    """

    def __init__(self, db: Optional[Session] = None):
        """
        Initialize the analysis service.

        Args:
            db: Optional database session for persisting results
        """
        self.db = db

    def analyze_transcript(
        self,
        transcript_id: str,
        content: str,
        known_players: Optional[List[Dict]] = None
    ) -> TranscriptAnalysisResult:
        """
        Perform full analysis on a transcript.

        Args:
            transcript_id: ID of the transcript being analyzed
            content: Raw transcript text
            known_players: Optional list of known players with aliases

        Returns:
            TranscriptAnalysisResult with all analysis data
        """
        # Step 1: Preprocess the text
        processed = preprocessor.preprocess(content)

        # Step 2: Register known players if provided
        if known_players:
            entity_recognizer.register_known_players(known_players)

        # Step 3: Identify entities (players)
        mentions = entity_recognizer.identify_entities(processed.cleaned)
        players_grouped = entity_recognizer.group_mentions_by_player(mentions)

        # Step 4: Analyze each player
        player_results = []
        for canonical_name, identified_player in players_grouped.items():
            result = self._analyze_player(
                processed.cleaned,
                identified_player
            )
            player_results.append(result)

        # Sort by mention count (most mentioned first)
        player_results.sort(key=lambda x: x.mention_count, reverse=True)

        # Step 5: Comparative bias analysis
        comparative_analysis = None
        if len(player_results) >= 2:
            comparative_analysis = self._compare_players(player_results)

        return TranscriptAnalysisResult(
            transcript_id=transcript_id,
            processed_text=processed,
            players_found=[p.player_name for p in player_results],
            player_results=player_results,
            comparative_analysis=comparative_analysis
        )

    def _analyze_player(
        self,
        text: str,
        identified_player: IdentifiedPlayer
    ) -> PlayerAnalysisResult:
        """
        Perform detailed analysis for a single player.

        Args:
            text: Preprocessed text
            identified_player: Player with their mentions

        Returns:
            PlayerAnalysisResult with sentiment, adjective, phrase, and bias data
        """
        player_name = identified_player.canonical_name
        mentions = identified_player.mentions

        # Convert mentions to dict format for sentiment analysis
        mention_dicts = [
            {'sentence': m.sentence, 'text': m.text, 'start': m.start}
            for m in mentions
        ]

        # Sentiment analysis on mentions
        avg_sentiment, sentiment_label, sentiment_results = \
            sentiment_analyzer.analyze_player_mentions(mention_dicts, text)

        # Adjective extraction
        aliases = list(identified_player.aliases)
        adjective_profile = adjective_extractor.build_player_profile(
            text, player_name, aliases
        )

        # Build adjectives list for storage
        adjectives = [
            {
                'word': adj.word,
                'count': adj.count,
                'sentiment': adj.sentiment_hint or 'neutral'
            }
            for adj in adjective_profile.adjectives[:20]  # Top 20
        ]

        # Phrase detection
        phrase_profile = phrase_detector.build_player_phrase_profile(
            text, player_name, aliases
        )

        # Build phrases list for storage
        phrases = [
            {
                'phrase': p.phrase,
                'count': p.count,
                'sentiment': p.sentiment_hint or 'neutral',
                'context': p.contexts[0] if p.contexts else ''
            }
            for p in phrase_profile.phrases[:15]  # Top 15
        ]

        # Build excerpts (sample sentences mentioning the player)
        excerpts = []
        excerpt_sentiments = []
        for i, mention in enumerate(mentions[:10]):  # First 10 mentions
            if mention.sentence:
                sentiment_result = sentiment_results[i] if i < len(sentiment_results) else None
                sentiment_value = sentiment_result.score if sentiment_result else 0.0
                excerpts.append({
                    'text': mention.sentence,
                    'sentiment': sentiment_value,
                    'position': mention.start
                })
                excerpt_sentiments.append(sentiment_value)

        # Calculate sentiment distribution
        sentiment_distribution = {
            'positive': sum(1 for r in sentiment_results if r.score > 0.1),
            'negative': sum(1 for r in sentiment_results if r.score < -0.1),
            'neutral': sum(1 for r in sentiment_results if -0.1 <= r.score <= 0.1),
        }

        # Bias scoring
        bias_result = bias_scorer.calculate_bias_score(
            player_name=player_name,
            sentiment_score=avg_sentiment,
            sentiment_distribution=sentiment_distribution,
            adjective_sentiments=adjectives,
            mention_count=identified_player.mention_count,
            excerpt_sentiments=excerpt_sentiments
        )

        # Calculate confidence based on multiple factors
        confidence = bias_result.confidence

        # Build bias indicators for storage
        bias_indicators = [
            {
                'category': ind.category,
                'description': ind.description,
                'score': ind.score,
                'weight': ind.weight,
                'evidence': ind.evidence
            }
            for ind in bias_result.indicators
        ]

        return PlayerAnalysisResult(
            player_name=player_name,
            mention_count=identified_player.mention_count,
            sentiment_score=avg_sentiment,
            sentiment_label=sentiment_label.value if isinstance(sentiment_label, SentimentLabel) else str(sentiment_label),
            confidence=confidence,
            adjectives=adjectives,
            phrases=phrases,
            excerpts=excerpts,
            bias_score=bias_result.overall_score,
            bias_level=bias_result.bias_level.value,
            bias_indicators=bias_indicators
        )

    def _compare_players(
        self,
        player_results: List[PlayerAnalysisResult]
    ) -> Dict[str, Any]:
        """
        Perform comparative bias analysis across players.

        Args:
            player_results: List of player analysis results

        Returns:
            Comparative analysis data
        """
        # Build bias scores for comparison
        bias_scores = []
        for result in player_results:
            if result.bias_score is not None:
                # Reconstruct BiasScore for comparison
                from app.services.nlp.bias import BiasScore, BiasLevel, BiasIndicator
                indicators = [
                    BiasIndicator(
                        category=ind['category'],
                        description=ind['description'],
                        score=ind['score'],
                        weight=ind['weight'],
                        evidence=ind.get('evidence', [])
                    )
                    for ind in result.bias_indicators
                ]
                bias_score = BiasScore(
                    player_name=result.player_name,
                    overall_score=result.bias_score,
                    bias_level=BiasLevel(result.bias_level),
                    confidence=result.confidence,
                    indicators=indicators
                )
                bias_scores.append(bias_score)

        if len(bias_scores) < 2:
            return None

        # Run comparative analysis
        comparison = bias_scorer.compare_players(bias_scores)

        return {
            'fairness_score': comparison.fairness_score,
            'most_favored': comparison.most_favored,
            'least_favored': comparison.least_favored,
            'disparity_score': comparison.disparity_score,
            'player_rankings': [
                {
                    'player_name': p.player_name,
                    'rank': p.comparative_rank,
                    'bias_score': p.overall_score,
                    'bias_level': p.bias_level.value
                }
                for p in comparison.players
            ]
        }

    def analyze_and_persist(
        self,
        transcript_id: uuid.UUID,
        db: Session
    ) -> List[AnalysisResult]:
        """
        Analyze a transcript and persist results to database.

        Args:
            transcript_id: UUID of transcript to analyze
            db: Database session

        Returns:
            List of created AnalysisResult records
        """
        # Fetch transcript
        transcript = db.query(Transcript).filter(
            Transcript.id == transcript_id
        ).first()

        if not transcript:
            raise ValueError(f"Transcript {transcript_id} not found")

        # Fetch known players from database
        known_players = db.query(Player).all()
        known_players_data = [
            {'name': p.name, 'aliases': p.aliases or []}
            for p in known_players
        ]

        # Run analysis
        result = self.analyze_transcript(
            str(transcript_id),
            transcript.content,
            known_players_data
        )

        # Persist results
        analysis_results = []
        for player_result in result.player_results:
            # Find or create player
            player = self._find_or_create_player(
                db,
                player_result.player_name,
                transcript.sport
            )

            # Create analysis result
            analysis = AnalysisResult(
                transcript_id=transcript_id,
                player_id=player.id,
                sentiment_score=player_result.sentiment_score,
                sentiment_label=player_result.sentiment_label,
                confidence=player_result.confidence,
                mention_count=player_result.mention_count,
                adjectives=player_result.adjectives,
                phrases=player_result.phrases,
                excerpts=player_result.excerpts
            )
            db.add(analysis)
            analysis_results.append(analysis)

        # Update transcript status
        transcript.processed = True
        transcript.processed_at = datetime.utcnow()

        db.commit()

        # Refresh to get IDs
        for ar in analysis_results:
            db.refresh(ar)

        return analysis_results

    def _find_or_create_player(
        self,
        db: Session,
        player_name: str,
        sport: Optional[str] = None
    ) -> Player:
        """
        Find existing player or create new one.

        Args:
            db: Database session
            player_name: Player's canonical name
            sport: Sport type

        Returns:
            Player record
        """
        # Try to find existing player
        player = db.query(Player).filter(
            Player.name.ilike(player_name)
        ).first()

        if not player:
            # Check aliases
            players = db.query(Player).all()
            for p in players:
                if p.aliases:
                    for alias in p.aliases:
                        if alias.lower() == player_name.lower():
                            return p

            # Create new player
            player = Player(
                name=player_name,
                sport=sport,
                aliases=[]
            )
            db.add(player)
            db.flush()

        return player


def get_analysis_service(db: Optional[Session] = None) -> AnalysisService:
    """Factory function for AnalysisService."""
    return AnalysisService(db)
