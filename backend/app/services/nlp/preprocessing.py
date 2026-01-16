"""
Text preprocessing pipeline for sports commentary analysis.
Handles cleaning, normalization, and sentence segmentation.
"""

import re
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class ProcessedText:
    """Container for preprocessed text data."""
    original: str
    cleaned: str
    sentences: List[str]
    word_count: int


class TextPreprocessor:
    """Preprocesses sports commentary transcripts for NLP analysis."""

    # Common transcript artifacts to remove
    TIMESTAMP_PATTERNS = [
        r'\d{1,2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{1,2}:\d{2}:\d{2}[.,]\d{3}',  # SRT/VTT timestamps
        r'\[\d{1,2}:\d{2}(:\d{2})?\]',  # [00:00] style timestamps
        r'\(\d{1,2}:\d{2}(:\d{2})?\)',  # (00:00) style timestamps
        r'^\d+\s*$',  # Standalone numbers (SRT sequence numbers)
    ]

    # Speaker label patterns
    SPEAKER_PATTERNS = [
        r'^[A-Z][A-Z\s]+:',  # "ANNOUNCER:" style
        r'^\[[^\]]+\]:',  # "[Speaker]:" style
        r'^>>\s*',  # ">> " style
    ]

    def __init__(self):
        self._timestamp_regex = re.compile(
            '|'.join(self.TIMESTAMP_PATTERNS),
            re.MULTILINE
        )
        self._speaker_regex = re.compile(
            '|'.join(self.SPEAKER_PATTERNS),
            re.MULTILINE
        )

    def preprocess(self, text: str) -> ProcessedText:
        """
        Full preprocessing pipeline for commentary text.

        Args:
            text: Raw transcript text

        Returns:
            ProcessedText with cleaned content and metadata
        """
        original = text

        # Step 1: Remove timestamps and sequence numbers
        cleaned = self._remove_timestamps(text)

        # Step 2: Normalize speaker labels
        cleaned = self._normalize_speakers(cleaned)

        # Step 3: Clean whitespace and normalize
        cleaned = self._normalize_whitespace(cleaned)

        # Step 4: Segment into sentences
        sentences = self._segment_sentences(cleaned)

        # Step 5: Count words
        word_count = self._count_words(cleaned)

        return ProcessedText(
            original=original,
            cleaned=cleaned,
            sentences=sentences,
            word_count=word_count
        )

    def _remove_timestamps(self, text: str) -> str:
        """Remove timestamp markers from transcript."""
        # Remove SRT/VTT style timestamps
        text = self._timestamp_regex.sub('', text)

        # Remove WEBVTT header if present
        text = re.sub(r'^WEBVTT\s*\n', '', text, flags=re.MULTILINE)

        return text

    def _normalize_speakers(self, text: str) -> str:
        """
        Normalize or remove speaker labels while preserving content.
        Keeps the speaker info but normalizes format.
        """
        # Replace speaker labels with normalized format
        text = self._speaker_regex.sub('', text)
        return text

    def _normalize_whitespace(self, text: str) -> str:
        """Clean up whitespace issues."""
        # Replace multiple newlines with single newline
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Replace multiple spaces with single space
        text = re.sub(r'[ \t]+', ' ', text)

        # Strip leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)

        return text.strip()

    def _segment_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        Handles sports-specific punctuation patterns.
        """
        # Replace newlines with spaces for sentence detection
        text = text.replace('\n', ' ')

        # Simple sentence splitting on common terminators
        # More sophisticated splitting would use spaCy
        sentence_endings = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
        sentences = sentence_endings.split(text)

        # Clean and filter sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def _count_words(self, text: str) -> int:
        """Count words in text."""
        words = text.split()
        return len(words)

    def extract_mentions_context(
        self,
        text: str,
        entity: str,
        window_size: int = 50
    ) -> List[Tuple[str, int]]:
        """
        Extract text windows around mentions of an entity.

        Args:
            text: Full text to search
            entity: Entity name to find
            window_size: Number of characters on each side

        Returns:
            List of (context_text, position) tuples
        """
        contexts = []
        pattern = re.compile(re.escape(entity), re.IGNORECASE)

        for match in pattern.finditer(text):
            start = max(0, match.start() - window_size)
            end = min(len(text), match.end() + window_size)

            # Extend to word boundaries
            while start > 0 and text[start] not in ' \n':
                start -= 1
            while end < len(text) and text[end] not in ' \n':
                end += 1

            context = text[start:end].strip()
            contexts.append((context, match.start()))

        return contexts


# Singleton instance
preprocessor = TextPreprocessor()
