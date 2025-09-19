
from collections import Counter
from functools import cached_property
from typing import Any
import statistics

from spacy.tokens import Doc
from spacy.language import Language

from lint_ii.core.lint_scorer import LintScorer
from lint_ii.core.word_features import WordFeatures


class SentenceAnalysis:
    """Sentence-level readability analysis."""

    def __init__(
        self,
        doc: Doc,
        abstract_nouns_list: list[str]|None = None,
    ) -> None:
        self.doc = doc
        self.abstract_nouns_list = [] if abstract_nouns_list is None else abstract_nouns_list

    @classmethod
    def from_text(
        cls,
        text: str,
        nlp_model: Language,
        abstract_nouns_list: list[str]|None = None,
    ) -> 'SentenceAnalysis':
        doc = nlp_model(text)
        return cls(doc, abstract_nouns_list)

    @cached_property
    def word_features(self) -> list[WordFeatures]:
        """Linguistic features for each token in the sentence."""
        return [WordFeatures(token, self.abstract_nouns_list) for token in self.doc]

    @cached_property
    def sdls(self) -> dict[str, int]:
        """The dependency length (number of intervening tokens) between a token and its syntactic head, for each token in the sentence."""
        return {
            feat.token.text:{
                'dep_length': feat.dep_length,
                'head': feat.token.head.text,
            }
            for feat in self.word_features
        }

    @property
    def concrete_nouns(self) -> list[str]:
        """All concrete nouns in the sentence."""
        return [
            feat.token.text for feat in self.word_features
            if feat.is_noun and not feat.is_abstract
        ]

    @property
    def abstract_nouns(self) -> list[str]:
        """All abstract nouns in the sentence."""
        return [
            feat.token.text for feat in self.word_features
            if feat.is_noun and feat.is_abstract
        ]

    @property
    def content_words(self) -> list[str]:
        """All content words (excluding adverbs) in the sentence."""
        return [
            feat.token.text for feat in self.word_features
            if feat.is_content_word_excl_adv
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
        values = {self.sdls[sdl]['dep_length'] for sdl in self.sdls}
        return max(values, default=0)

    def count_content_words_excluding_adverbs(self) -> int:
        """Count content words (excluding adverbs) in the sentence."""
        return sum(feat.is_content_word_excl_adv for feat in self.word_features)

    def count_clauses(self) -> int:
        """Count clauses (= finite verbs) in the sentence."""
        finite_verb_counts = sum(
            feat.is_finite_verb
            for feat in self.word_features
        )
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
        n_abstract_nouns = len(self.abstract_nouns)
        total_nouns = sum(feat.is_noun for feat in self.word_features)
        if total_nouns == 0:
            return 0
        return (total_nouns - n_abstract_nouns) / total_nouns

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
        frequencies = Counter({
            feat.token.text:freq
            for feat in self.word_features
            if (freq:=feat.word_frequency) is not None
        })
        return frequencies.most_common()[:-n-1:-1]

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
            'max_sdl': self.max_sdl,
            'sdls': self.sdls,
            'content_words': self.content_words,
        }
