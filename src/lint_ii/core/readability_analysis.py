from functools import cached_property
from typing import Any, TypedDict
import statistics

from lint_ii.core.word_features import WordFeatures
from lint_ii.core.lint_scorer import LintScorer
from lint_ii.core.sentence_analysis import SentenceAnalysis, SentenceAnalysisDict

from lint_ii.visualization.html import LintIIVisualizer


class DocumentStatsDict(TypedDict):
    sentence_count: int
    mean_lint_score: float
    min_lint_score: float
    max_lint_score: float


class ReadabilityAnalysisDict(TypedDict):
    sentences: list[SentenceAnalysisDict]
    level: int
    sentence_count: int
    mean_lint_score: float
    min_lint_score: float
    max_lint_score: float


class ReadabilityAnalysis(LintIIVisualizer):
    """Readability analysis for a given text."""

    def __init__(self, sentences: list[SentenceAnalysis]) -> None:
        self.sentences = sentences

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({[repr(s.doc) for s in self.sentences]})"

    @classmethod
    def from_text(
        cls,
        text: str,
    ) -> 'ReadabilityAnalysis':
        from lint_ii.linguistic_data.nlp_model import NLP_MODEL
        doc = NLP_MODEL(text)
        sentences = [
            SentenceAnalysis(sent)
            for sent in doc.sents
        ]
        return cls(sentences)

    @property
    def word_features(self) -> list[WordFeatures]:
        """Bag of word features for the document."""
        return [
            feat
            for sentence in self.sentences
            for feat in sentence.word_features
        ]

    @property
    def concrete_nouns(self) -> list[str]:
        """Bag of concrete nouns for the document."""
        return [
            noun
            for sentence in self.sentences
            for noun in sentence.concrete_nouns
        ]

    @property
    def abstract_nouns(self) -> list[str]:
        """Bag of abstract nouns for the document."""
        return [
            noun
            for sentence in self.sentences
            for noun in sentence.abstract_nouns
        ]

    @cached_property
    def lint_scores_per_sentence(self) -> list[float]:
        return [sent.calculate_lint_score() for sent in self.sentences]

    @cached_property
    def mean_log_word_frequency(self) -> float:
        """Mean log word frequency for the document."""
        frequencies = [
            freq
            for feat in self.word_features
            if (freq := feat.word_frequency) is not None
        ]
        return statistics.mean(frequencies) if frequencies else 0

    @cached_property
    def mean_max_sdl(self) -> float:
        """Mean value of sentence-level maximum dependency lengths"""
        return statistics.mean(s.max_sdl for s in self.sentences)

    @cached_property
    def mean_content_words_per_clause(self) -> float:
        """Mean value of sentence-level content words per clause"""
        return statistics.mean(
            s.content_words_per_clause
            for s in self.sentences
        )

    @cached_property
    def proportion_of_concrete_nouns(self) -> float:
        """Proportion of concrete nouns out of all nouns in the document."""
        n_concrete_nouns = len(self.concrete_nouns)
        n_abstract_nouns = len(self.abstract_nouns)
        total_nouns = n_concrete_nouns + n_abstract_nouns
        if total_nouns == 0:
            return 0
        return n_concrete_nouns / total_nouns

    def calculate_document_stats(self) -> DocumentStatsDict:
        """Calculate statistics on a document level: sentence count, mean LiNT score, min LiNT score, max LiNT score."""
        return {
            'sentence_count': len(self.sentences),
            'mean_lint_score': self.mean_lint_score,
            'min_lint_score': self.min_lint_score,
            'max_lint_score': self.max_lint_score,
        }

    @cached_property
    def mean_lint_score(self) -> float:
        return statistics.mean(self.lint_scores_per_sentence)

    @cached_property
    def min_lint_score(self) -> float:
        return min(self.lint_scores_per_sentence)

    @cached_property
    def max_lint_score(self) -> float:
        return max(self.lint_scores_per_sentence)

    @cached_property
    def difficulty_level(self) -> int:
        return LintScorer.get_difficulty_level(self.mean_lint_score)

    def get_detailed_analysis(self) -> dict[str, Any]:
        """Get detailed readability analysis per sentence in the document."""
        return {
            'document_stats': self.calculate_document_stats(),
            'sentence_stats': [
                sent.get_detailed_analysis()
                for sent in self.sentences
            ],
        }

    def as_dict(self) -> ReadabilityAnalysisDict:
        return {
            'sentences': [sent.as_dict() for sent in self.sentences],
            'level': self.difficulty_level,
            **self.calculate_document_stats(),
        }
