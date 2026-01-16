"""
Adjective extraction and analysis service for sports commentary.
Identifies descriptive language used about players.
"""

import re
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import Counter

try:
    import spacy
    from spacy.tokens import Token
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


@dataclass
class AdjectiveInfo:
    """Information about an adjective usage."""
    word: str
    lemma: str
    count: int
    sentiment_hint: Optional[str] = None  # positive, negative, neutral
    contexts: List[str] = field(default_factory=list)


@dataclass
class PlayerAdjectiveProfile:
    """Adjective usage profile for a specific player."""
    player_name: str
    adjectives: List[AdjectiveInfo]
    total_adjective_count: int
    unique_adjective_count: int
    top_adjectives: List[Tuple[str, int]]


class AdjectiveExtractor:
    """
    Extracts and analyzes adjectives used in proximity to player mentions.
    """

    # Words that commonly precede adjectives about players
    INTENSIFIERS = {'very', 'really', 'so', 'extremely', 'incredibly', 'absolutely'}

    # Common positive adjectives in sports
    POSITIVE_ADJECTIVES = {
        'great', 'good', 'excellent', 'amazing', 'brilliant', 'fantastic',
        'outstanding', 'incredible', 'superb', 'wonderful', 'spectacular',
        'impressive', 'dominant', 'powerful', 'quick', 'fast', 'strong',
        'skilled', 'talented', 'clutch', 'reliable', 'consistent', 'accurate',
        'athletic', 'explosive', 'dynamic', 'electric', 'elite', 'special',
    }

    # Common negative adjectives in sports
    NEGATIVE_ADJECTIVES = {
        'bad', 'poor', 'terrible', 'awful', 'disappointing', 'weak',
        'slow', 'sloppy', 'careless', 'inconsistent', 'unreliable',
        'costly', 'brutal', 'horrible', 'pathetic', 'embarrassing',
        'lazy', 'selfish', 'reckless', 'undisciplined', 'ineffective',
    }

    # Adjectives to skip (too common/generic)
    SKIP_ADJECTIVES = {
        'other', 'same', 'new', 'old', 'first', 'last', 'next', 'more',
        'many', 'few', 'several', 'such', 'own', 'only', 'main', 'certain',
    }

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize the adjective extractor.

        Args:
            model_name: spaCy model to use
        """
        self.model_name = model_name
        self._nlp = None

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

    def extract_adjectives(
        self,
        text: str,
        target_entity: Optional[str] = None,
        window_size: int = 50
    ) -> List[AdjectiveInfo]:
        """
        Extract adjectives from text, optionally filtering by proximity to an entity.

        Args:
            text: Text to analyze
            target_entity: If provided, only extract adjectives near this entity
            window_size: Character window around entity mentions

        Returns:
            List of AdjectiveInfo objects
        """
        doc = self.nlp(text)
        adjective_counts = Counter()
        adjective_contexts: Dict[str, List[str]] = {}

        # If targeting specific entity, find relevant windows
        if target_entity:
            windows = self._get_entity_windows(text, target_entity, window_size)
            relevant_text = ' '.join(windows)
            doc = self.nlp(relevant_text)

        for token in doc:
            if self._is_valid_adjective(token):
                lemma = token.lemma_.lower()

                # Skip common/generic adjectives
                if lemma in self.SKIP_ADJECTIVES:
                    continue

                adjective_counts[lemma] += 1

                # Store context (the sentence)
                if lemma not in adjective_contexts:
                    adjective_contexts[lemma] = []
                if len(adjective_contexts[lemma]) < 3:  # Limit contexts stored
                    sent_text = token.sent.text if token.sent else ""
                    if sent_text and sent_text not in adjective_contexts[lemma]:
                        adjective_contexts[lemma].append(sent_text)

        # Build AdjectiveInfo objects
        results = []
        for word, count in adjective_counts.most_common():
            sentiment = self._get_adjective_sentiment(word)
            results.append(AdjectiveInfo(
                word=word,
                lemma=word,
                count=count,
                sentiment_hint=sentiment,
                contexts=adjective_contexts.get(word, [])
            ))

        return results

    def _is_valid_adjective(self, token: 'Token') -> bool:
        """Check if token is a valid adjective for our purposes."""
        # Must be an adjective
        if token.pos_ != 'ADJ':
            return False

        # Must be at least 3 characters
        if len(token.text) < 3:
            return False

        # Skip if it looks like a number
        if token.like_num:
            return False

        return True

    def _get_entity_windows(
        self,
        text: str,
        entity: str,
        window_size: int
    ) -> List[str]:
        """Get text windows around entity mentions."""
        windows = []
        pattern = re.compile(re.escape(entity), re.IGNORECASE)

        for match in pattern.finditer(text):
            start = max(0, match.start() - window_size)
            end = min(len(text), match.end() + window_size)
            windows.append(text[start:end])

        return windows

    def _get_adjective_sentiment(self, word: str) -> str:
        """Determine if an adjective has positive or negative sentiment."""
        word_lower = word.lower()
        if word_lower in self.POSITIVE_ADJECTIVES:
            return 'positive'
        elif word_lower in self.NEGATIVE_ADJECTIVES:
            return 'negative'
        return 'neutral'

    def build_player_profile(
        self,
        text: str,
        player_name: str,
        player_aliases: Optional[List[str]] = None
    ) -> PlayerAdjectiveProfile:
        """
        Build a complete adjective profile for a player.

        Args:
            text: Full transcript text
            player_name: Player's canonical name
            player_aliases: Alternative names/nicknames

        Returns:
            PlayerAdjectiveProfile with aggregated adjective data
        """
        all_adjectives = []

        # Search for primary name
        names_to_search = [player_name]
        if player_aliases:
            names_to_search.extend(player_aliases)

        # Combine adjectives from all name variations
        combined_counts = Counter()
        combined_contexts: Dict[str, List[str]] = {}

        for name in names_to_search:
            adjectives = self.extract_adjectives(text, target_entity=name)
            for adj in adjectives:
                combined_counts[adj.lemma] += adj.count
                if adj.lemma not in combined_contexts:
                    combined_contexts[adj.lemma] = []
                combined_contexts[adj.lemma].extend(adj.contexts[:2])

        # Build final list
        for word, count in combined_counts.most_common():
            sentiment = self._get_adjective_sentiment(word)
            all_adjectives.append(AdjectiveInfo(
                word=word,
                lemma=word,
                count=count,
                sentiment_hint=sentiment,
                contexts=combined_contexts.get(word, [])[:3]
            ))

        total_count = sum(adj.count for adj in all_adjectives)
        top_adjectives = [(adj.word, adj.count) for adj in all_adjectives[:10]]

        return PlayerAdjectiveProfile(
            player_name=player_name,
            adjectives=all_adjectives,
            total_adjective_count=total_count,
            unique_adjective_count=len(all_adjectives),
            top_adjectives=top_adjectives
        )

    def compare_players(
        self,
        text: str,
        players: List[Dict[str, any]]
    ) -> Dict[str, PlayerAdjectiveProfile]:
        """
        Compare adjective usage across multiple players.

        Args:
            text: Full transcript text
            players: List of player dicts with 'name' and 'aliases'

        Returns:
            Dict mapping player names to their profiles
        """
        profiles = {}
        for player in players:
            name = player.get('name', '')
            aliases = player.get('aliases', [])
            profiles[name] = self.build_player_profile(text, name, aliases)
        return profiles


# Singleton instance
adjective_extractor = AdjectiveExtractor()
