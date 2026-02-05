from functools import cached_property
from typing import Any, TypedDict
import statistics

from lint_ii.core.preprocessor import preprocess_text
from lint_ii.core.word_features import WordFeatures
from lint_ii.core.sentence_analysis import SentenceAnalysis
from lint_ii.core.lint_scorer import LintScorer
from lint_ii.core.sentence_analysis import SentenceAnalysis, SentenceAnalysisDict

from lint_ii.visualization.html import LintIIVisualizer


class DocumentStatsDict(TypedDict):
    sentence_count: int
    document_lint_score: float | None
    document_difficulty_level: int | None
    min_lint_score: float | None
    max_lint_score: float | None


class ReadabilityAnalysisDict(TypedDict):
    sentences: list[SentenceAnalysisDict]
    document_lint_score: float | None
    document_difficulty_level: int | None
    sentence_count: int
    min_lint_score: float | None
    max_lint_score: float | None


class ReadabilityAnalysis(LintIIVisualizer):
    """
    Document-level readability analysis for Dutch texts using the LiNT-II formula.

    This class analyzes documents by aggregating sentence-level features and 
    computing readability scores based on four linguistic features: word frequency, 
    syntactic dependency length, content words per clause, and proportion of concrete nouns.

    Parameters
    ----------
    sentences : list[SentenceAnalysis]
        List of sentence-level analysis objects. Each sentence must be a 
        SentenceAnalysis instance containing linguistic features and metadata.

    Attributes & Properties
    -----------------------
    sentences : list[SentenceAnalysis]
        The input sentence analyses.
    word_features : list[WordFeatures]
        Flattened list of all word features across sentences.
    concrete_nouns : list[WordFeatures]
        All concrete nouns in the document.
    abstract_nouns : list[WordFeatures]
        All abstract nouns in the document.
    undefined_nouns : list[WordFeatures]
        All undefined nouns in the document (have both a concrete and an abstract meaning).
    mean_log_word_frequency : float | None
        Document-level mean log frequency of content words (excluding proper nouns).
        Returns None if there are no frequencies on the sentence-level. Cached property.
    mean_max_sdl : float | None
        Mean of maximum syntactic dependency lengths across sentences.
        Returns None if there are no SDLs on the sentence-level. Cached property.
    mean_content_words_per_clause : float | None
        Mean content words per clause across sentences.
        Returns None if there are no content words / clause on the sentence-level. Cached property.
    proportion_of_concrete_nouns : float | None
        Proportion of concrete nouns out of the total nouns in the document.
        Nouns of type `unknown` (not in the list) are excluded from the totals count.
        Returns None if totals are 0, i.e. there are no nouns or only `unknown` nouns in the sentence. Cached property.
    lint : LintScorer
        LintScorer object that contains the score (lint.score) and the difficulty level (lint.level) for the document. Cached property.
    lint_scores_per_sentence : list[float]
        Individual LiNT scores for each sentence in the document. Cached property.
    min_lint_score : float | None
        Lowest sentence-level score in the document.
        Returns None if there are no sentence-level scores. Cached property.
    max_lint_score : float | None
        Highest sentence-level score in the document.
        Returns None if there are no sentence-level scores. Cached property.

    Methods
    -------
    from_text(text: str) -> ReadabilityAnalysis
        Create analysis from text string. Preprocesses text and applies spaCy NLP pipeline.
    calculate_document_stats() -> DocumentStatsDict
        Generate summary statistics including sentence count, mean/min/max scores.
    get_detailed_analysis() -> dict[str, Any]
        Return comprehensive analysis with both document and sentence-level details.
    as_dict() -> ReadabilityAnalysisDict
        Serialize analysis to dictionary format (used in the LiNT-II visualizer).

    Examples
    --------
    >>> from lint_ii import ReadabilityAnalysis
    >>> text = "Jip zit bij de kapper. Knip, knap, zegt de schaar."
    >>> analysis = ReadabilityAnalysis.from_text(text)
    >>> analysis.lint.score
    21.9
    >>> analysis.lint.level
    1
    >>> stats = analysis.calculate_document_stats()
    >>> stats['sentence_count']
    2

    See Also
    --------
    SentenceAnalysis : Sentence-level readability analysis
    WordFeatures : Token-level linguistic feature extraction
    LintScorer : LiNT scoring algorithms
    """

    def __init__(self, sentences: list[SentenceAnalysis]) -> None:
        self.sentences = sentences

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({[repr(s.doc) for s in self.sentences]})"

    @classmethod
    def from_text(
        cls,
        text: str,
    ) -> 'ReadabilityAnalysis':
        """
        Create analysis from text string:
        (a) Load spaCy model
        (b) Pre-process text (clean-up) and create spaCy Doc object
        (c) Apply sentence-level readability analysis on each sentence in the Doc
        """
        from lint_ii.linguistic_data.nlp_model import NLP_MODEL
        clean_text = preprocess_text(text)
        doc = NLP_MODEL(clean_text)
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
    def concrete_nouns(self) -> list[WordFeatures]:
        """Bag of concrete nouns for the document."""
        return [
            noun
            for sentence in self.sentences
            for noun in sentence.concrete_nouns
        ]

    @property
    def abstract_nouns(self) -> list[WordFeatures]:
        """Bag of abstract nouns for the document."""
        return [
            noun
            for sentence in self.sentences
            for noun in sentence.abstract_nouns
        ]
    
    @property
    def undefined_nouns(self) -> list[WordFeatures]:
        """Bag of undefined nouns for the document."""
        return [
            noun
            for sentence in self.sentences
            for noun in sentence.undefined_nouns
        ]

    @cached_property
    def mean_log_word_frequency(self) -> float | None:
        """
        Mean log word frequency for the document.
        Returns None if there are no frequencies on the sentence-level.
        """
        frequencies = [
            freq
            for feat in self.word_features
            if (freq := feat.word_frequency) is not None
        ]
        if not frequencies:
            return None
        return statistics.mean(frequencies)

    @cached_property
    def mean_max_sdl(self) -> float | None:
        """
        Mean value of sentence-level maximum dependency lengths.
        Returns None if there are no SDLs on the sentence-level.
        """
        sdls = [s.max_sdl for s in self.sentences if s.max_sdl is not None]
        if not sdls:
            return None
        return statistics.mean(sdls)

    @cached_property
    def mean_content_words_per_clause(self) -> float | None:
        """
        Mean value of sentence-level content words per clause.
        Returns None if there are no content words / clause on the sentence-level.
        """
        content_words_per_clause = [
            s.content_words_per_clause
            for s in self.sentences
            if s.content_words_per_clause is not None
        ]
        if not content_words_per_clause:
            return None
        return statistics.mean(content_words_per_clause)

    @cached_property
    def proportion_of_concrete_nouns(self) -> float | None:
        """
        Proportion of concrete nouns out of the total nouns in the document.
        Nouns of type `unknown` (not in the list) are excluded from the totals count.
        Returns None if totals are 0, i.e. there are no nouns or only `unknown` nouns in the sentence.
        """
        n_concrete_nouns = len(self.concrete_nouns)
        n_abstract_nouns = len(self.abstract_nouns)
        n_undefined_nouns = len(self.undefined_nouns)
        total_nouns = n_concrete_nouns + n_abstract_nouns + n_undefined_nouns
        if total_nouns == 0:
            return None
        return n_concrete_nouns / total_nouns

    @cached_property
    def lint(self) -> LintScorer:
        return LintScorer(
            freq_log = self.mean_log_word_frequency,
            max_sdl = self.mean_max_sdl,
            content_words_per_clause = self.mean_content_words_per_clause,
            proportion_concrete = self.proportion_of_concrete_nouns,
        )

    @cached_property
    def lint_scores_per_sentence(self) -> list[float]:
        return [
            sent.lint.score
            for sent in self.sentences
            if sent.lint.score is not None
        ]

    @cached_property
    def min_lint_score(self) -> float | None:
        """
        Lowest sentence-level score in the document.
        Returns None if there are no sentence-level scores.
        """
        return min(self.lint_scores_per_sentence, default=None)

    @cached_property
    def max_lint_score(self) -> float | None:
        """
        Highest sentence-level score in the document.
        Returns None if there are no sentence-level scores.
        """
        return max(self.lint_scores_per_sentence, default=None)

    def calculate_document_stats(self) -> DocumentStatsDict:
        """
        Statistics on a document level (sentence count, document LiNT score, document difficulty level, min LiNT score, max LiNT score).
        """
        return {
            'sentence_count': len(self.sentences),
            'document_lint_score': self.lint.score,
            'document_difficulty_level': self.lint.level,
            'min_lint_score': self.min_lint_score,
            'max_lint_score': self.max_lint_score,
        }
    
    def get_detailed_analysis(self, n: int = 5) -> dict[str, Any]:
        """Get detailed readability analysis per sentence in the document."""
        return {
            'document_stats': self.calculate_document_stats(),
            'sentence_stats': [
                sent.get_detailed_analysis(n=n)
                for sent in self.sentences
            ],
        }

    def as_dict(self) -> ReadabilityAnalysisDict:
        doc_stats = self.calculate_document_stats()
        return {
            'sentences': [sent.as_dict() for sent in self.sentences],
            'document_lint_score': doc_stats['document_lint_score'],
            'document_difficulty_level': doc_stats['document_difficulty_level'],
            'sentence_count': doc_stats['sentence_count'],
            'min_lint_score': doc_stats['min_lint_score'],
            'max_lint_score': doc_stats['max_lint_score'],
        }
