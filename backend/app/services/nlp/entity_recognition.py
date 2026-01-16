"""
Named Entity Recognition service for identifying players in sports commentary.
Uses spaCy for NER with custom rules for sports-specific entities.
"""

import re
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, field
from collections import defaultdict

try:
    import spacy
    from spacy.tokens import Doc
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


@dataclass
class EntityMention:
    """Represents a single mention of an entity in text."""
    text: str
    start: int
    end: int
    label: str
    sentence: str
    confidence: float = 1.0


@dataclass
class IdentifiedPlayer:
    """Aggregated player identification result."""
    canonical_name: str
    mentions: List[EntityMention] = field(default_factory=list)
    aliases: Set[str] = field(default_factory=set)
    mention_count: int = 0

    def add_mention(self, mention: EntityMention):
        self.mentions.append(mention)
        self.aliases.add(mention.text)
        self.mention_count += 1


class EntityRecognizer:
    """
    Identifies player names and other entities in sports commentary.
    Combines spaCy NER with custom rules for improved accuracy.
    """

    # Common sports-related terms that are often misidentified as people
    SPORTS_TERMS_BLACKLIST = {
        'goal', 'score', 'point', 'basket', 'touchdown', 'home run',
        'strike', 'ball', 'out', 'safe', 'foul', 'penalty', 'timeout',
        'quarter', 'half', 'period', 'inning', 'set', 'game', 'match',
        'championship', 'playoff', 'finals', 'super bowl', 'world series',
        'mvp', 'rookie', 'veteran', 'coach', 'ref', 'referee', 'umpire',
    }

    # Title patterns that often precede names
    TITLE_PATTERNS = [
        r'\b(Mr|Mrs|Ms|Dr|Coach|Captain|Sir)\.\s*',
    ]

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize the entity recognizer.

        Args:
            model_name: spaCy model to use (en_core_web_sm, en_core_web_md, etc.)
        """
        self.model_name = model_name
        self._nlp = None
        self._known_players: Dict[str, Set[str]] = {}  # canonical -> aliases

    @property
    def nlp(self):
        """Lazy load spaCy model."""
        if self._nlp is None:
            if not SPACY_AVAILABLE:
                raise RuntimeError("spaCy is not installed")
            try:
                self._nlp = spacy.load(self.model_name)
            except OSError:
                # Model not downloaded, use blank model
                self._nlp = spacy.blank("en")
        return self._nlp

    def register_known_players(self, players: List[Dict[str, any]]):
        """
        Register known players for improved recognition.

        Args:
            players: List of player dicts with 'name' and optional 'aliases'
        """
        for player in players:
            name = player.get('name', '')
            aliases = set(player.get('aliases', []))
            aliases.add(name)

            # Add common variations
            if ' ' in name:
                parts = name.split()
                aliases.add(parts[-1])  # Last name
                aliases.add(parts[0])   # First name

            self._known_players[name] = aliases

    def identify_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None
    ) -> List[EntityMention]:
        """
        Identify named entities in text.

        Args:
            text: Text to analyze
            entity_types: Filter to specific types (PERSON, ORG, etc.)

        Returns:
            List of EntityMention objects
        """
        if entity_types is None:
            entity_types = ['PERSON']

        mentions = []

        # Use spaCy NER
        doc = self.nlp(text)

        for ent in doc.ents:
            if ent.label_ in entity_types:
                # Filter out blacklisted terms
                if ent.text.lower() in self.SPORTS_TERMS_BLACKLIST:
                    continue

                # Get sentence context
                sentence = self._get_sentence_for_span(doc, ent.start, ent.end)

                mention = EntityMention(
                    text=ent.text,
                    start=ent.start_char,
                    end=ent.end_char,
                    label=ent.label_,
                    sentence=sentence,
                    confidence=0.8  # Base confidence for spaCy
                )
                mentions.append(mention)

        # Also check for known players that spaCy might have missed
        mentions.extend(self._find_known_players(text, doc))

        return mentions

    def _get_sentence_for_span(self, doc: Doc, start: int, end: int) -> str:
        """Get the sentence containing a span."""
        for sent in doc.sents:
            if sent.start <= start < sent.end:
                return sent.text
        return ""

    def _find_known_players(self, text: str, doc: Doc) -> List[EntityMention]:
        """Find mentions of known players that NER might have missed."""
        mentions = []
        found_spans = set()

        for canonical_name, aliases in self._known_players.items():
            for alias in aliases:
                if len(alias) < 3:  # Skip very short aliases
                    continue

                pattern = re.compile(r'\b' + re.escape(alias) + r'\b', re.IGNORECASE)

                for match in pattern.finditer(text):
                    # Skip if this span was already found
                    span_key = (match.start(), match.end())
                    if span_key in found_spans:
                        continue
                    found_spans.add(span_key)

                    # Get sentence context
                    sentence = ""
                    for sent in doc.sents:
                        if sent.start_char <= match.start() < sent.end_char:
                            sentence = sent.text
                            break

                    mention = EntityMention(
                        text=match.group(),
                        start=match.start(),
                        end=match.end(),
                        label='PERSON',
                        sentence=sentence,
                        confidence=0.95  # High confidence for known players
                    )
                    mentions.append(mention)

        return mentions

    def group_mentions_by_player(
        self,
        mentions: List[EntityMention]
    ) -> Dict[str, IdentifiedPlayer]:
        """
        Group entity mentions into distinct players.
        Handles name variations and aliases.

        Args:
            mentions: List of entity mentions

        Returns:
            Dict mapping canonical names to IdentifiedPlayer objects
        """
        players: Dict[str, IdentifiedPlayer] = {}
        name_to_canonical: Dict[str, str] = {}

        # First, map known player aliases to canonical names
        for canonical, aliases in self._known_players.items():
            for alias in aliases:
                name_to_canonical[alias.lower()] = canonical

        for mention in mentions:
            mention_lower = mention.text.lower()

            # Check if this maps to a known player
            canonical = name_to_canonical.get(mention_lower)

            if canonical is None:
                # Try to find if this is a partial match (last name)
                for known_canonical, aliases in self._known_players.items():
                    for alias in aliases:
                        if mention_lower == alias.lower():
                            canonical = known_canonical
                            break
                    if canonical:
                        break

            if canonical is None:
                # New player - use the mention text as canonical name
                canonical = self._normalize_name(mention.text)

            # Create or update player entry
            if canonical not in players:
                players[canonical] = IdentifiedPlayer(canonical_name=canonical)

            players[canonical].add_mention(mention)
            name_to_canonical[mention_lower] = canonical

        return players

    def _normalize_name(self, name: str) -> str:
        """Normalize a player name to a canonical form."""
        # Remove titles
        for pattern in self.TITLE_PATTERNS:
            name = re.sub(pattern, '', name)

        # Title case
        name = name.strip().title()

        return name


# Singleton instance with default model
entity_recognizer = EntityRecognizer()
