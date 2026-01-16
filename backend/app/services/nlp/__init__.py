"""
NLP services for sports commentary analysis.
"""

from app.services.nlp.preprocessing import TextPreprocessor, ProcessedText, preprocessor
from app.services.nlp.entity_recognition import (
    EntityRecognizer,
    EntityMention,
    IdentifiedPlayer,
    entity_recognizer,
)
from app.services.nlp.sentiment import (
    SentimentAnalyzer,
    SentimentResult,
    SentimentLabel,
    sentiment_analyzer,
)
from app.services.nlp.adjectives import (
    AdjectiveExtractor,
    AdjectiveInfo,
    PlayerAdjectiveProfile,
    adjective_extractor,
)

__all__ = [
    # Preprocessing
    'TextPreprocessor',
    'ProcessedText',
    'preprocessor',
    # Entity Recognition
    'EntityRecognizer',
    'EntityMention',
    'IdentifiedPlayer',
    'entity_recognizer',
    # Sentiment Analysis
    'SentimentAnalyzer',
    'SentimentResult',
    'SentimentLabel',
    'sentiment_analyzer',
    # Adjective Extraction
    'AdjectiveExtractor',
    'AdjectiveInfo',
    'PlayerAdjectiveProfile',
    'adjective_extractor',
]
