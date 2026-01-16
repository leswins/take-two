"""
Bias detection and scoring service for sports commentary analysis.
Identifies patterns of favoritism or negativity toward specific players.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math


class BiasLevel(str, Enum):
    """Classification of bias intensity."""
    STRONG_POSITIVE = "strong_positive"
    MODERATE_POSITIVE = "moderate_positive"
    SLIGHT_POSITIVE = "slight_positive"
    NEUTRAL = "neutral"
    SLIGHT_NEGATIVE = "slight_negative"
    MODERATE_NEGATIVE = "moderate_negative"
    STRONG_NEGATIVE = "strong_negative"


@dataclass
class BiasIndicator:
    """A specific indicator contributing to bias detection."""
    category: str  # sentiment, language, frequency, context
    description: str
    score: float  # -1 to 1
    weight: float  # importance of this indicator
    evidence: List[str] = field(default_factory=list)


@dataclass
class BiasScore:
    """Complete bias analysis for a player."""
    player_name: str
    overall_score: float  # -1 (strong negative) to 1 (strong positive)
    bias_level: BiasLevel
    confidence: float  # 0 to 1
    indicators: List[BiasIndicator]
    comparative_rank: Optional[int] = None  # Rank among compared players
    explanation: str = ""


@dataclass
class ComparativeBiasAnalysis:
    """Comparison of bias across multiple players."""
    players: List[BiasScore]
    fairness_score: float  # 0 to 1 (1 = perfectly fair)
    most_favored: Optional[str] = None
    least_favored: Optional[str] = None
    disparity_score: float = 0.0  # Difference between most and least favored


class BiasScorer:
    """
    Calculates bias scores based on multiple factors:
    - Sentiment distribution
    - Language patterns (adjective sentiment)
    - Mention frequency relative to context
    - Consistency of treatment
    """

    # Weights for different bias indicators
    INDICATOR_WEIGHTS = {
        'sentiment': 0.35,
        'language': 0.25,
        'frequency': 0.15,
        'consistency': 0.15,
        'context': 0.10,
    }

    # Thresholds for bias levels
    BIAS_THRESHOLDS = [
        (0.6, BiasLevel.STRONG_POSITIVE),
        (0.3, BiasLevel.MODERATE_POSITIVE),
        (0.1, BiasLevel.SLIGHT_POSITIVE),
        (-0.1, BiasLevel.NEUTRAL),
        (-0.3, BiasLevel.SLIGHT_NEGATIVE),
        (-0.6, BiasLevel.MODERATE_NEGATIVE),
    ]

    def calculate_bias_score(
        self,
        player_name: str,
        sentiment_score: float,
        sentiment_distribution: Dict[str, int],  # positive, negative, neutral counts
        adjective_sentiments: List[Dict],  # [{word, count, sentiment}]
        mention_count: int,
        excerpt_sentiments: List[float],  # Individual mention sentiments
        context_stats: Optional[Dict] = None  # Additional context
    ) -> BiasScore:
        """
        Calculate comprehensive bias score for a player.

        Args:
            player_name: Name of the player
            sentiment_score: Overall sentiment (-1 to 1)
            sentiment_distribution: Counts of positive/negative/neutral
            adjective_sentiments: Adjectives with sentiment classification
            mention_count: Total mentions
            excerpt_sentiments: Sentiment scores for individual mentions
            context_stats: Optional additional context

        Returns:
            BiasScore with detailed breakdown
        """
        indicators = []

        # 1. Sentiment Indicator
        sentiment_indicator = self._calculate_sentiment_indicator(
            sentiment_score, sentiment_distribution
        )
        indicators.append(sentiment_indicator)

        # 2. Language Pattern Indicator
        language_indicator = self._calculate_language_indicator(adjective_sentiments)
        indicators.append(language_indicator)

        # 3. Frequency Indicator (if context available)
        if context_stats and 'expected_mentions' in context_stats:
            freq_indicator = self._calculate_frequency_indicator(
                mention_count, context_stats['expected_mentions']
            )
            indicators.append(freq_indicator)

        # 4. Consistency Indicator
        consistency_indicator = self._calculate_consistency_indicator(excerpt_sentiments)
        indicators.append(consistency_indicator)

        # Calculate overall score
        overall_score = self._weighted_average(indicators)

        # Determine bias level
        bias_level = self._score_to_level(overall_score)

        # Calculate confidence
        confidence = self._calculate_confidence(
            mention_count, len(excerpt_sentiments), len(adjective_sentiments)
        )

        # Generate explanation
        explanation = self._generate_explanation(
            player_name, bias_level, indicators, confidence
        )

        return BiasScore(
            player_name=player_name,
            overall_score=overall_score,
            bias_level=bias_level,
            confidence=confidence,
            indicators=indicators,
            explanation=explanation
        )

    def _calculate_sentiment_indicator(
        self,
        sentiment_score: float,
        distribution: Dict[str, int]
    ) -> BiasIndicator:
        """Calculate bias indicator from sentiment data."""
        total = sum(distribution.values()) or 1
        pos_ratio = distribution.get('positive', 0) / total
        neg_ratio = distribution.get('negative', 0) / total

        # Score based on both overall sentiment and distribution skew
        distribution_skew = pos_ratio - neg_ratio
        combined_score = (sentiment_score * 0.6) + (distribution_skew * 0.4)

        evidence = []
        if pos_ratio > 0.5:
            evidence.append(f"{pos_ratio*100:.0f}% of mentions are positive")
        if neg_ratio > 0.5:
            evidence.append(f"{neg_ratio*100:.0f}% of mentions are negative")

        return BiasIndicator(
            category='sentiment',
            description='Overall sentiment analysis',
            score=combined_score,
            weight=self.INDICATOR_WEIGHTS['sentiment'],
            evidence=evidence
        )

    def _calculate_language_indicator(
        self,
        adjective_sentiments: List[Dict]
    ) -> BiasIndicator:
        """Calculate bias indicator from language patterns."""
        if not adjective_sentiments:
            return BiasIndicator(
                category='language',
                description='Language pattern analysis',
                score=0.0,
                weight=self.INDICATOR_WEIGHTS['language'],
                evidence=['Insufficient adjective data']
            )

        positive_count = sum(
            adj.get('count', 1) for adj in adjective_sentiments
            if adj.get('sentiment') == 'positive'
        )
        negative_count = sum(
            adj.get('count', 1) for adj in adjective_sentiments
            if adj.get('sentiment') == 'negative'
        )
        total = positive_count + negative_count or 1

        score = (positive_count - negative_count) / total

        evidence = []
        top_positive = [adj['word'] for adj in adjective_sentiments
                        if adj.get('sentiment') == 'positive'][:3]
        top_negative = [adj['word'] for adj in adjective_sentiments
                        if adj.get('sentiment') == 'negative'][:3]

        if top_positive:
            evidence.append(f"Positive terms: {', '.join(top_positive)}")
        if top_negative:
            evidence.append(f"Negative terms: {', '.join(top_negative)}")

        return BiasIndicator(
            category='language',
            description='Adjective and descriptive language analysis',
            score=score,
            weight=self.INDICATOR_WEIGHTS['language'],
            evidence=evidence
        )

    def _calculate_frequency_indicator(
        self,
        actual_mentions: int,
        expected_mentions: float
    ) -> BiasIndicator:
        """Calculate bias indicator from mention frequency."""
        if expected_mentions <= 0:
            return BiasIndicator(
                category='frequency',
                description='Mention frequency analysis',
                score=0.0,
                weight=self.INDICATOR_WEIGHTS['frequency'],
                evidence=['No expected frequency baseline']
            )

        ratio = actual_mentions / expected_mentions
        # Normalize: 2x expected = +0.5, 0.5x expected = -0.5
        score = max(-1, min(1, (ratio - 1) * 0.5))

        evidence = []
        if ratio > 1.5:
            evidence.append(f"Mentioned {ratio:.1f}x more than expected")
        elif ratio < 0.67:
            evidence.append(f"Mentioned {ratio:.1f}x less than expected")

        return BiasIndicator(
            category='frequency',
            description='Mention frequency relative to expectations',
            score=score,
            weight=self.INDICATOR_WEIGHTS['frequency'],
            evidence=evidence
        )

    def _calculate_consistency_indicator(
        self,
        excerpt_sentiments: List[float]
    ) -> BiasIndicator:
        """Calculate bias indicator from sentiment consistency."""
        if len(excerpt_sentiments) < 2:
            return BiasIndicator(
                category='consistency',
                description='Sentiment consistency analysis',
                score=0.0,
                weight=self.INDICATOR_WEIGHTS['consistency'],
                evidence=['Insufficient data for consistency analysis']
            )

        # Calculate variance - low variance with bias indicates consistent bias
        mean = sum(excerpt_sentiments) / len(excerpt_sentiments)
        variance = sum((x - mean) ** 2 for x in excerpt_sentiments) / len(excerpt_sentiments)
        std_dev = math.sqrt(variance)

        # If consistently positive or negative (low std_dev), amplify the mean
        # If highly variable (high std_dev), reduce toward neutral
        consistency_factor = 1 - min(1, std_dev)
        score = mean * (0.5 + 0.5 * consistency_factor)

        evidence = []
        if std_dev < 0.3:
            evidence.append("Highly consistent treatment across mentions")
        elif std_dev > 0.7:
            evidence.append("Inconsistent treatment - varies by context")

        return BiasIndicator(
            category='consistency',
            description='Consistency of treatment across mentions',
            score=score,
            weight=self.INDICATOR_WEIGHTS['consistency'],
            evidence=evidence
        )

    def _weighted_average(self, indicators: List[BiasIndicator]) -> float:
        """Calculate weighted average of indicator scores."""
        total_weight = sum(ind.weight for ind in indicators)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(ind.score * ind.weight for ind in indicators)
        return weighted_sum / total_weight

    def _score_to_level(self, score: float) -> BiasLevel:
        """Convert numeric score to bias level."""
        for threshold, level in self.BIAS_THRESHOLDS:
            if score >= threshold:
                return level
        return BiasLevel.STRONG_NEGATIVE

    def _calculate_confidence(
        self,
        mention_count: int,
        excerpt_count: int,
        adjective_count: int
    ) -> float:
        """Calculate confidence in the bias score."""
        # More data = higher confidence
        mention_factor = min(1.0, mention_count / 20)
        excerpt_factor = min(1.0, excerpt_count / 10)
        adjective_factor = min(1.0, adjective_count / 10)

        # Weighted combination
        confidence = (
            mention_factor * 0.4 +
            excerpt_factor * 0.35 +
            adjective_factor * 0.25
        )

        return round(confidence, 2)

    def _generate_explanation(
        self,
        player_name: str,
        level: BiasLevel,
        indicators: List[BiasIndicator],
        confidence: float
    ) -> str:
        """Generate human-readable explanation of bias."""
        level_descriptions = {
            BiasLevel.STRONG_POSITIVE: "shows strong positive bias toward",
            BiasLevel.MODERATE_POSITIVE: "shows moderate positive bias toward",
            BiasLevel.SLIGHT_POSITIVE: "shows slight positive bias toward",
            BiasLevel.NEUTRAL: "shows neutral treatment of",
            BiasLevel.SLIGHT_NEGATIVE: "shows slight negative bias toward",
            BiasLevel.MODERATE_NEGATIVE: "shows moderate negative bias toward",
            BiasLevel.STRONG_NEGATIVE: "shows strong negative bias toward",
        }

        conf_text = "high" if confidence > 0.7 else "moderate" if confidence > 0.4 else "low"
        base = f"The commentary {level_descriptions[level]} {player_name} ({conf_text} confidence)."

        # Add key evidence
        key_evidence = []
        for ind in indicators:
            if ind.evidence and abs(ind.score) > 0.2:
                key_evidence.extend(ind.evidence[:1])

        if key_evidence:
            base += " Key factors: " + "; ".join(key_evidence[:3]) + "."

        return base

    def compare_players(
        self,
        player_scores: List[BiasScore]
    ) -> ComparativeBiasAnalysis:
        """
        Compare bias scores across multiple players.

        Args:
            player_scores: List of BiasScore objects to compare

        Returns:
            ComparativeBiasAnalysis with fairness assessment
        """
        if not player_scores:
            return ComparativeBiasAnalysis(
                players=[],
                fairness_score=1.0
            )

        # Sort by overall score
        sorted_scores = sorted(player_scores, key=lambda x: x.overall_score, reverse=True)

        # Assign ranks
        for i, score in enumerate(sorted_scores):
            score.comparative_rank = i + 1

        # Calculate fairness (inverse of score range)
        scores = [p.overall_score for p in sorted_scores]
        score_range = max(scores) - min(scores)
        fairness = 1 - min(1, score_range)

        most_favored = sorted_scores[0].player_name if sorted_scores else None
        least_favored = sorted_scores[-1].player_name if sorted_scores else None

        return ComparativeBiasAnalysis(
            players=sorted_scores,
            fairness_score=round(fairness, 2),
            most_favored=most_favored,
            least_favored=least_favored,
            disparity_score=round(score_range, 2)
        )


# Singleton instance
bias_scorer = BiasScorer()
