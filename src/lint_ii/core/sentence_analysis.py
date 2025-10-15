
from operator import itemgetter
from functools import cached_property
from typing import Any, TypedDict
import statistics

from spacy.tokens import Doc, Span

from lint_ii.core.preprocessor import preprocess_text
from lint_ii.core.lint_scorer import LintScorer
from lint_ii.core.word_features import WordFeatures


class SDLInfo(TypedDict):
    token: str
    dep_length: int
    head: str


class SentenceAnalysis:
    """Sentence-level readability analysis."""

    def __init__(
        self,
        doc: Doc|Span,
    ) -> None:
        self.doc = doc

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.doc}')"

    @classmethod
    def from_text(
        cls,
        text: str,
    ) -> 'SentenceAnalysis':
        from lint_ii.linguistic_data.nlp_model import NLP_MODEL
        clean_text = preprocess_text(text)
        doc = NLP_MODEL(clean_text)
        return cls(doc)

    @cached_property
    def word_features(self) -> list[WordFeatures]:
        """Linguistic features for each token in the sentence."""
        return [WordFeatures(token) for token in self.doc]

    @cached_property
    def sdls(self) -> list[SDLInfo]:
        """The dependency length (number of intervening tokens) between a token and its syntactic head, for each token in the sentence."""
        return [
            {
                'token': feat.text,
                'dep_length': feat.dep_length,
                'head': feat.head.text,
            }
            for feat in self.word_features
        ]

    @property
    def concrete_nouns(self) -> list[str]:
        """All concrete nouns in the sentence."""
        return [
            feat.text for feat in self.word_features
            if feat.is_concrete
        ]

    @property
    def abstract_nouns(self) -> list[str]:
        """All abstract nouns in the sentence."""
        return [
            feat.text for feat in self.word_features
            if feat.is_abstract
        ]

    @property
    def undefined_nouns(self) -> list[str]:
        """All undefined nouns in the sentence."""
        return [
            feat.text for feat in self.word_features
            if feat.is_undefined
        ]

    @property
    def unknown_nouns(self) -> list[str]:
        """All unknown nouns in the sentence."""
        return [
            feat.text for feat in self.word_features
            if feat.is_unknown
        ]

    @property
    def content_words(self) -> list[str]:
        """All content words (excluding adverbs) in the sentence."""
        return [
            feat.text for feat in self.word_features
            if feat.is_content_word_excl_adv
        ]

    @property
    def finite_verbs(self) -> list[str]:
        """All finite verbs in the sentence."""
        return [
            feat.text for feat in self.word_features
            if feat.is_finite_verb
        ]

    @cached_property
    def mean_log_word_frequency(self) -> float:
        """Mean log word frequency for the sentence."""
        frequencies = [
            freq
            for feat in self.word_features
            if (freq := feat.word_frequency) is not None
        ]
        return statistics.mean(frequencies) if frequencies else 0

    @cached_property
    def max_sdl(self) -> int:
        """Maximum dependency length in the sentence."""
        values = {sdl['dep_length'] for sdl in self.sdls}
        return max(values, default=0)

    def count_content_words_excluding_adverbs(self) -> int:
        """Count content words (excluding adverbs) in the sentence."""
        return sum(feat.is_content_word_excl_adv for feat in self.word_features)

    def count_clauses(self) -> int:
        """Count clauses (= finite verbs) in the sentence."""
        finite_verb_counts = sum(feat.is_finite_verb for feat in self.word_features)
        return finite_verb_counts if finite_verb_counts > 0 else 1

    @cached_property
    def content_words_per_clause(self) -> float:
        """Number of content words (excluding adverbs) per clause."""
        content_count = self.count_content_words_excluding_adverbs()
        clause_count = self.count_clauses()
        return content_count / clause_count

    @cached_property
    def proportion_of_concrete_nouns(self) -> float:
        """Proportion of concrete nouns out of all nouns in the sentence."""
        n_concrete_nouns = len(self.concrete_nouns)
        n_abstract_nouns = len(self.abstract_nouns)
        total_nouns = n_concrete_nouns + n_abstract_nouns
        if total_nouns == 0:
            return 0
        return n_concrete_nouns / total_nouns

    def calculate_lint_score(self) -> float:
        """Calculate LiNT readability score for the sentence."""
        return LintScorer.calculate_lint_score(
            freq_log = self.mean_log_word_frequency,
            max_sdl = self.max_sdl,
            content_words_per_clause = self.content_words_per_clause,
            proportion_concrete = self.proportion_of_concrete_nouns,
        )

    def get_difficulty_level(self) -> int:
        """Get difficulty level for the sentence."""
        return LintScorer.get_difficulty_level(self.calculate_lint_score())

    def get_top_n_least_frequent(self, n: int = 5) -> list[tuple[str, float]]:
        """Get the top n least frequent words in the sentence."""
        frequencies = {
            feat.text:freq
            for feat in self.word_features
            if (freq := feat.word_frequency) is not None
        }
        return sorted(frequencies.items(), key=itemgetter(1))[:n]

    def get_detailed_analysis(self, n: int = 5) -> dict[str, Any]:
        """Get detailed analysis for the sentence."""
        return {
            'text': self.doc.text,
            'score': self.calculate_lint_score(),
            'level': self.get_difficulty_level(),
            'top_n_least_freq_words': self.get_top_n_least_frequent(n=n),
            'mean_log_word_frequency': self.mean_log_word_frequency,
            'concrete_nouns': self.concrete_nouns,
            'abstract_nouns': self.abstract_nouns,
            'undefined_nouns': self.undefined_nouns,
            'unknown_nouns': self.unknown_nouns,
            'max_sdl': self.max_sdl,
            'sdls': self.sdls,
            'content_words_per_clause': self.content_words_per_clause,
            'content_words': self.content_words,
            'finite_verbs': self.finite_verbs,
        }
