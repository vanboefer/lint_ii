from functools import cached_property
from typing import Any
import statistics

from spacy.language import Language

from lint_ii.core.lint_scorer import LintScorer
from lint_ii.core.sentence_analysis import SentenceAnalysis


class ReadabilityAnalysis:
    """Readability analysis for a given text."""

    def __init__(self, sentences: list[SentenceAnalysis]) -> None:
        self.sentences = sentences

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({[s.doc for s in self.sentences]})"

    @classmethod
    def from_text(
        cls,
        text: str,
        nlp_model: Language,
        abstract_nouns_list: list[str]|None = None,
    ) -> 'ReadabilityAnalysis':
        doc = nlp_model(text)
        sentences = [
            SentenceAnalysis(sent, abstract_nouns_list)
            for sent in doc.sents
        ]
        return cls(sentences)

    @cached_property
    def lint_scores_per_sentence(self) -> list[float]:
        return [sent.calculate_lint_score() for sent in self.sentences]

    @cached_property
    def mean_word_frequency_log(self) -> float:
        """Mean value of sentence-level word frequencies"""
        return statistics.mean(s.mean_log_word_frequency for s in self.sentences)

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
    def mean_proportion_of_concrete_nouns(self) -> float:
        """Mean value of sentence-level proportion of concrete nouns"""
        return statistics.mean(
            s.proportion_of_concrete_nouns
            for s in self.sentences
        )

    def calculate_document_stats(self) -> dict[str, float]:
        """Calculate statistics on a document level: sentence count, mean LiNT score, min LiNT score, max LiNT score."""
        if not self.sentences:
            return {}
        return {
            'sentence_count': len(self.sentences),
            'mean_lint_score': statistics.mean(self.lint_scores_per_sentence),
            'min_lint_score': min(self.lint_scores_per_sentence),
            'max_lint_score': max(self.lint_scores_per_sentence),
        }

    def get_detailed_analysis(self) -> dict[str, Any]:
        """Get detailed readability analysis per sentence in the document."""
        return {
            'document_stats': self.calculate_document_stats(),
            'sentence_stats': [
                sent.get_detailed_analysis()
                for sent in self.sentences
            ],
        }
