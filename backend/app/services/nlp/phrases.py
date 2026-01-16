"""
Phrase detection service for identifying common expressions about players.
Extracts recurring patterns and notable phrases from commentary.
"""

import re
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import Counter

try:
    import spacy
    from spacy.tokens import Doc
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


@dataclass
class DetectedPhrase:
    """A phrase detected in relation to a player."""
    phrase: str
    count: int
    contexts: List[str] = field(default_factory=list)
    sentiment_hint: Optional[str] = None


@dataclass
class PlayerPhraseProfile:
    """Collection of phrases associated with a player."""
    player_name: str
    phrases: List[DetectedPhrase]
    total_phrase_count: int
    unique_phrases: int


class PhraseDetector:
    """
    Detects and tracks recurring phrases used in sports commentary.
    Focuses on verb phrases, descriptive patterns, and notable expressions.
    """

    # Common phrase patterns in sports commentary
    PHRASE_PATTERNS = [
        # Action phrases
        r'\b(makes|made)\s+(?:a\s+)?(\w+\s+){1,2}(play|shot|pass|save|tackle|catch)',
        r'\b(delivers|delivered)\s+(?:a\s+)?(\w+\s+){0,2}(ball|pass|hit|strike)',
        r'\b(shows|showed)\s+(?:great|incredible|amazing)?\s*(\w+)',

        # Descriptive phrases
        r'\b(what\s+a)\s+(\w+\s+){1,2}(by|from)',
        r'\b(absolutely|completely|totally)\s+(\w+)',
        r'\b(once\s+again)\s+(\w+)',

        # Comparison phrases
        r'\b(like|unlike)\s+(?:no\s+)?(?:other\s+)?(\w+)',
        r'\b(one\s+of\s+the\s+(?:best|worst|greatest))',
        r'\b(reminds\s+(?:me|us)\s+of)',
    ]

    # Common positive phrase indicators
    POSITIVE_INDICATORS = {
        'brilliant', 'amazing', 'incredible', 'fantastic', 'outstanding',
        'superb', 'excellent', 'magnificent', 'spectacular', 'clutch',
        'perfect', 'flawless', 'dominant', 'unstoppable', 'masterful',
    }

    # Common negative phrase indicators
    NEGATIVE_INDICATORS = {
        'terrible', 'awful', 'poor', 'disappointing', 'weak',
        'sloppy', 'careless', 'costly', 'missed', 'failed',
        'embarrassing', 'disastrous', 'horrible', 'pathetic',
    }

    def __init__(self, model_name: str = "en_core_web_sm"):
        self.model_name = model_name
        self._nlp = None
        self._compiled_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.PHRASE_PATTERNS
        ]

    @property
    def nlp(self):
        """Lazy load spaCy model."""
        if self._nlp is None:
            if not SPACY_AVAILABLE:
                raise RuntimeError("spaCy is not installed")
            try:
                self._nlp = spacy.load(self.model_name)
            except OSError:
                self._nlp = spacy.blank("en")
        return self._nlp

    def detect_phrases(
        self,
        text: str,
        target_entity: Optional[str] = None,
        min_length: int = 3,
        max_length: int = 8
    ) -> List[DetectedPhrase]:
        """
        Detect notable phrases in text, optionally near a target entity.

        Args:
            text: Text to analyze
            target_entity: If provided, focus on phrases near this entity
            min_length: Minimum number of words in a phrase
            max_length: Maximum number of words in a phrase

        Returns:
            List of DetectedPhrase objects
        """
        phrases = []

        # Pattern-based detection
        for pattern in self._compiled_patterns:
            for match in pattern.finditer(text):
                phrase_text = match.group().strip()
                if min_length <= len(phrase_text.split()) <= max_length:
                    sentiment = self._get_phrase_sentiment(phrase_text)
                    context = self._get_context(text, match.start(), match.end())
                    phrases.append(DetectedPhrase(
                        phrase=phrase_text,
                        count=1,
                        contexts=[context],
                        sentiment_hint=sentiment
                    ))

        # N-gram based detection using spaCy
        if target_entity:
            ngram_phrases = self._extract_entity_ngrams(text, target_entity, min_length, max_length)
            phrases.extend(ngram_phrases)

        # Aggregate duplicate phrases
        return self._aggregate_phrases(phrases)

    def _extract_entity_ngrams(
        self,
        text: str,
        entity: str,
        min_n: int,
        max_n: int
    ) -> List[DetectedPhrase]:
        """Extract n-grams from sentences containing the entity."""
        phrases = []
        doc = self.nlp(text)

        entity_lower = entity.lower()

        for sent in doc.sents:
            sent_lower = sent.text.lower()
            if entity_lower not in sent_lower:
                continue

            # Extract noun phrases and verb phrases
            for chunk in sent.noun_chunks:
                chunk_text = chunk.text.strip()
                word_count = len(chunk_text.split())
                if min_n <= word_count <= max_n:
                    sentiment = self._get_phrase_sentiment(chunk_text)
                    phrases.append(DetectedPhrase(
                        phrase=chunk_text,
                        count=1,
                        contexts=[sent.text],
                        sentiment_hint=sentiment
                    ))

            # Extract verb phrases (subject + verb + object patterns)
            for token in sent:
                if token.pos_ == 'VERB':
                    # Get the verb and its dependents
                    phrase_tokens = [token]
                    for child in token.children:
                        if child.dep_ in ('dobj', 'pobj', 'advmod', 'acomp'):
                            phrase_tokens.append(child)
                            # Include modifiers of the child
                            for grandchild in child.children:
                                if grandchild.dep_ in ('amod', 'compound', 'det'):
                                    phrase_tokens.append(grandchild)

                    if len(phrase_tokens) >= 2:
                        # Sort by position in sentence
                        phrase_tokens.sort(key=lambda t: t.i)
                        phrase_text = ' '.join(t.text for t in phrase_tokens)
                        sentiment = self._get_phrase_sentiment(phrase_text)
                        phrases.append(DetectedPhrase(
                            phrase=phrase_text,
                            count=1,
                            contexts=[sent.text],
                            sentiment_hint=sentiment
                        ))

        return phrases

    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get surrounding context for a phrase."""
        ctx_start = max(0, start - window)
        ctx_end = min(len(text), end + window)

        # Extend to word boundaries
        while ctx_start > 0 and text[ctx_start] not in ' \n':
            ctx_start -= 1
        while ctx_end < len(text) and text[ctx_end] not in ' \n':
            ctx_end += 1

        return text[ctx_start:ctx_end].strip()

    def _get_phrase_sentiment(self, phrase: str) -> str:
        """Determine sentiment hint for a phrase."""
        phrase_lower = phrase.lower()

        for word in self.POSITIVE_INDICATORS:
            if word in phrase_lower:
                return 'positive'

        for word in self.NEGATIVE_INDICATORS:
            if word in phrase_lower:
                return 'negative'

        return 'neutral'

    def _aggregate_phrases(self, phrases: List[DetectedPhrase]) -> List[DetectedPhrase]:
        """Aggregate duplicate phrases and combine contexts."""
        phrase_map: Dict[str, DetectedPhrase] = {}

        for phrase in phrases:
            key = phrase.phrase.lower()
            if key in phrase_map:
                phrase_map[key].count += 1
                if phrase.contexts:
                    # Limit stored contexts
                    if len(phrase_map[key].contexts) < 5:
                        phrase_map[key].contexts.extend(phrase.contexts[:1])
            else:
                phrase_map[key] = DetectedPhrase(
                    phrase=phrase.phrase,
                    count=1,
                    contexts=phrase.contexts[:3],
                    sentiment_hint=phrase.sentiment_hint
                )

        # Sort by count
        sorted_phrases = sorted(phrase_map.values(), key=lambda p: p.count, reverse=True)
        return sorted_phrases

    def build_player_phrase_profile(
        self,
        text: str,
        player_name: str,
        player_aliases: Optional[List[str]] = None
    ) -> PlayerPhraseProfile:
        """
        Build a complete phrase profile for a player.

        Args:
            text: Full transcript text
            player_name: Player's canonical name
            player_aliases: Alternative names/nicknames

        Returns:
            PlayerPhraseProfile with aggregated phrase data
        """
        all_phrases = []

        names_to_search = [player_name]
        if player_aliases:
            names_to_search.extend(player_aliases)

        for name in names_to_search:
            phrases = self.detect_phrases(text, target_entity=name)
            all_phrases.extend(phrases)

        # Aggregate across all names
        aggregated = self._aggregate_phrases(all_phrases)

        # Filter to top phrases
        top_phrases = aggregated[:20]

        total_count = sum(p.count for p in top_phrases)

        return PlayerPhraseProfile(
            player_name=player_name,
            phrases=top_phrases,
            total_phrase_count=total_count,
            unique_phrases=len(top_phrases)
        )


# Singleton instance
phrase_detector = PhraseDetector()
