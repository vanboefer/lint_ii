from functools import cached_property
from typing import Any, TypedDict
import statistics

from lint_ii import linguistic_data
from lint_ii.core.preprocessor import preprocess_text
from lint_ii.core.word_features import WordFeatures
from lint_ii.core.sentence_analysis import SentenceAnalysis
from lint_ii.core.lint_scorer import LintScorer
from lint_ii.core.sentence_analysis import SentenceAnalysis, SentenceAnalysisDict

from lint_ii.visualization.html import LintIIVisualizer


class DocumentStatsDict(TypedDict):
    sentence_count: int
    document_lint_score: float
    document_difficulty_level: int
    min_lint_score: float
    max_lint_score: float
    word_freq_compound_adjustment: bool


class ReadabilityAnalysisDict(TypedDict):
    sentences: list[SentenceAnalysisDict]
    document_lint_score: float
    document_difficulty_level: int
    sentence_count: int
    min_lint_score: float
    max_lint_score: float


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

    Attributes
    ----------
    sentences : list[SentenceAnalysis]
        The input sentence analyses.
    document_lint_score : float
        Overall LiNT readability score for the document (0-100, higher=more difficult).
        Cached property computed from document-level features.
    document_difficulty_level : int
        Difficulty level (1-4) derived from document_lint_score. Cached property.
    lint_scores_per_sentence : list[float]
        Individual LiNT scores for each sentence. Cached property.
    min_lint_score : float
        Lowest sentence-level score in the document. Cached property.
    max_lint_score : float
        Highest sentence-level score in the document. Cached property.

    Methods
    -------
    from_text(text: str) -> ReadabilityAnalysis
        Create analysis from text string. Preprocesses text and applies NLP 
        pipeline.
    calculate_lint_score() -> float
        Compute document LiNT score using aggregated linguistic features.
    get_difficulty_level() -> int
        Convert LiNT score to difficulty level (1-4, where 4=most difficult).
    calculate_document_stats() -> DocumentStatsDict
        Generate summary statistics including sentence count, mean/min/max scores.
    get_detailed_analysis() -> dict[str, Any]
        Return comprehensive analysis with both document and sentence-level details.
    as_dict() -> ReadabilityAnalysisDict
        Serialize analysis to dictionary format (used in the LiNT-II visualizer).

    Properties
    ----------
    word_features : list[WordFeatures]
        Flattened list of all word features across sentences.
    concrete_nouns : list[str]
        All concrete nouns found in the document.
    abstract_nouns : list[str]
        All abstract nouns found in the document.
    mean_log_word_frequency : float
        Document-level mean log frequency of content words (excluding proper nouns).
    mean_max_sdl : float
        Mean of maximum syntactic dependency lengths across sentences.
    mean_content_words_per_clause : float
        Mean content words per clause across sentences.
    proportion_of_concrete_nouns : float
        Ratio of concrete nouns to total nouns (0.0-1.0).

    Notes
    -----
    The LiNT-II formula computes readability as:

    .. code-block:: text

        raw score = constant 
                  + (coefficient_freq * mean_log_word_frequency)
                  + (coefficient_sdl * max_syntactic_dependency_length)
                  + (coefficient_cwc * content_words_per_clause)
                  + (coefficient_concrete * proportion_concrete_nouns)

        LiNT = 100 - clamp(raw_score, 0, 100)

    Higher scores indicate more difficult texts.

    Examples
    --------
    >>> from lint_ii import ReadabilityAnalysis
    >>> text = "Jip zit bij de kapper. Knip, knap, zegt de schaar."
    >>> analysis = ReadabilityAnalysis.from_text(text)
    >>> analysis.document_lint_score
    30.1
    >>> analysis.get_difficulty_level()
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
    def document_lint_score(self) -> float:
        return self.calculate_lint_score()
    
    @cached_property
    def document_difficulty_level(self) -> int:
        return self.get_difficulty_level()

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
        """Mean value of sentence-level maximum dependency lengths."""
        return statistics.mean(s.max_sdl for s in self.sentences)

    @cached_property
    def mean_content_words_per_clause(self) -> float:
        """Mean value of sentence-level content words per clause."""
        return statistics.mean(
            s.content_words_per_clause
            for s in self.sentences
        )

    @cached_property
    def proportion_of_concrete_nouns(self) -> float:
        """
        Proportion of concrete nouns out of all nouns in the document.
        Nouns of type `undefined` (have both a concrete and an abstract meaning)
        and `unknown` (not in the list) are excluded from the totals count.
        """
        n_concrete_nouns = len(self.concrete_nouns)
        n_abstract_nouns = len(self.abstract_nouns)
        total_nouns = n_concrete_nouns + n_abstract_nouns
        if total_nouns == 0:
            return 0
        return n_concrete_nouns / total_nouns

    def calculate_lint_score(self) -> float:
        """Calculate LiNT readability score for the document."""
        return LintScorer.calculate_lint_score(
            freq_log = self.mean_log_word_frequency,
            max_sdl = self.mean_max_sdl,
            content_words_per_clause = self.mean_content_words_per_clause,
            proportion_concrete = self.proportion_of_concrete_nouns,
        )

    def get_difficulty_level(self) -> int:
        """Get difficulty level for the document."""
        return LintScorer.get_difficulty_level(self.calculate_lint_score())

    def calculate_document_stats(self) -> DocumentStatsDict:
        """
        Statistics on a document level (sentence count, document LiNT score, document difficulty level,
        min LiNT score, max LiNT score) + the value of `WORD_FREQ_COMPOUND_ADJUSTMENT` (True or False).
        """
        return {
            'sentence_count': len(self.sentences),
            'document_lint_score': self.document_lint_score,
            'document_difficulty_level': self.document_difficulty_level,
            'min_lint_score': self.min_lint_score,
            'max_lint_score': self.max_lint_score,
            'word_freq_compound_adjustment': linguistic_data.WORD_FREQ_COMPOUND_ADJUSTMENT,
        }

    @cached_property
    def min_lint_score(self) -> float:
        """Lowest sentence-level score in the document."""
        return min(self.lint_scores_per_sentence)

    @cached_property
    def max_lint_score(self) -> float:
        """Highest sentence-level score in the document."""
        return max(self.lint_scores_per_sentence)

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
