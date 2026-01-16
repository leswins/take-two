"""
Sentiment analysis service for sports commentary.
Uses HuggingFace Transformers for accurate sentiment classification.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class SentimentResult:
    """Result of sentiment analysis on a text segment."""
    text: str
    label: SentimentLabel
    score: float  # -1 to 1 scale
    confidence: float  # 0 to 1
    raw_scores: Dict[str, float]  # Original model scores


class SentimentAnalyzer:
    """
    Analyzes sentiment in sports commentary text.
    Provides both overall sentiment and per-mention sentiment.
    """

    # Default model - good balance of speed and accuracy
    DEFAULT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"

    # Sports-specific positive/negative modifiers
    POSITIVE_MODIFIERS = {
        'brilliant', 'amazing', 'incredible', 'fantastic', 'excellent',
        'outstanding', 'superb', 'magnificent', 'spectacular', 'phenomenal',
        'clutch', 'dominant', 'unstoppable', 'flawless', 'perfect',
    }

    NEGATIVE_MODIFIERS = {
        'terrible', 'awful', 'horrible', 'disastrous', 'pathetic',
        'disappointing', 'poor', 'weak', 'sloppy', 'careless',
        'costly', 'brutal', 'embarrassing', 'shameful', 'inexcusable',
    }

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the sentiment analyzer.

        Args:
            model_name: HuggingFace model name for sentiment analysis
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self._pipeline = None

    @property
    def pipeline(self):
        """Lazy load the sentiment analysis pipeline."""
        if self._pipeline is None:
            if not TRANSFORMERS_AVAILABLE:
                raise RuntimeError("transformers library is not installed")
            self._pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                top_k=None  # Get all scores
            )
        return self._pipeline

    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of a single text.

        Args:
            text: Text to analyze

        Returns:
            SentimentResult with label, score, and confidence
        """
        if not text or not text.strip():
            return SentimentResult(
                text=text,
                label=SentimentLabel.NEUTRAL,
                score=0.0,
                confidence=0.0,
                raw_scores={}
            )

        # Truncate long text (model has token limit)
        truncated = text[:512] if len(text) > 512 else text

        try:
            results = self.pipeline(truncated)

            # Parse results (format varies by model)
            raw_scores = {}
            for item in results[0] if isinstance(results[0], list) else results:
                label = item['label'].lower()
                raw_scores[label] = item['score']

            # Convert to our standard format
            label, score, confidence = self._normalize_scores(raw_scores)

            # Apply sports-specific adjustments
            score = self._apply_sports_modifiers(text, score)
            label = self._score_to_label(score)

            return SentimentResult(
                text=text,
                label=label,
                score=score,
                confidence=confidence,
                raw_scores=raw_scores
            )

        except Exception as e:
            # Fallback to neutral on error
            return SentimentResult(
                text=text,
                label=SentimentLabel.NEUTRAL,
                score=0.0,
                confidence=0.0,
                raw_scores={"error": str(e)}
            )

    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """
        Analyze sentiment of multiple texts efficiently.

        Args:
            texts: List of texts to analyze

        Returns:
            List of SentimentResult objects
        """
        results = []
        for text in texts:
            results.append(self.analyze(text))
        return results

    def analyze_player_mentions(
        self,
        mentions: List[Dict],
        full_text: str
    ) -> Tuple[float, SentimentLabel, List[SentimentResult]]:
        """
        Analyze sentiment specifically around player mentions.

        Args:
            mentions: List of mention dicts with 'sentence' key
            full_text: Full text for context

        Returns:
            Tuple of (average_score, overall_label, individual_results)
        """
        if not mentions:
            return 0.0, SentimentLabel.NEUTRAL, []

        # Analyze each mention's sentence context
        results = []
        for mention in mentions:
            sentence = mention.get('sentence', '')
            if sentence:
                result = self.analyze(sentence)
                results.append(result)

        if not results:
            return 0.0, SentimentLabel.NEUTRAL, []

        # Calculate average sentiment
        scores = [r.score for r in results]
        avg_score = sum(scores) / len(scores)

        # Determine overall label
        overall_label = self._score_to_label(avg_score)

        return avg_score, overall_label, results

    def _normalize_scores(
        self,
        raw_scores: Dict[str, float]
    ) -> Tuple[SentimentLabel, float, float]:
        """
        Normalize model-specific scores to our standard format.

        Returns:
            Tuple of (label, score, confidence)
        """
        # Handle different model output formats
        if 'positive' in raw_scores and 'negative' in raw_scores:
            pos = raw_scores['positive']
            neg = raw_scores['negative']
            score = pos - neg  # -1 to 1 scale
            confidence = max(pos, neg)
        elif 'label_1' in raw_scores:  # Some models use label_0, label_1
            pos = raw_scores.get('label_1', 0)
            neg = raw_scores.get('label_0', 0)
            score = pos - neg
            confidence = max(pos, neg)
        else:
            # Default handling
            score = 0.0
            confidence = 0.5

        label = self._score_to_label(score)
        return label, score, confidence

    def _score_to_label(self, score: float) -> SentimentLabel:
        """Convert numeric score to sentiment label."""
        if score > 0.1:
            return SentimentLabel.POSITIVE
        elif score < -0.1:
            return SentimentLabel.NEGATIVE
        else:
            return SentimentLabel.NEUTRAL

    def _apply_sports_modifiers(self, text: str, base_score: float) -> float:
        """
        Adjust sentiment score based on sports-specific language.

        Args:
            text: Original text
            base_score: Score from model

        Returns:
            Adjusted score
        """
        text_lower = text.lower()
        adjustment = 0.0

        # Count positive and negative modifiers
        for word in self.POSITIVE_MODIFIERS:
            if word in text_lower:
                adjustment += 0.05

        for word in self.NEGATIVE_MODIFIERS:
            if word in text_lower:
                adjustment -= 0.05

        # Clamp to valid range
        adjusted = base_score + adjustment
        return max(-1.0, min(1.0, adjusted))


# Singleton instance
sentiment_analyzer = SentimentAnalyzer()
