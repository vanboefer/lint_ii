
from operator import itemgetter
from functools import cached_property
from typing import Any, TypedDict
import statistics

from spacy.tokens import Doc, Span

from lint_ii.core.preprocessor import preprocess_text
from lint_ii.core.lint_scorer import LintScorer
from lint_ii.core.word_features import WordFeatures, WordFeaturesDict


class SDLInfo(TypedDict):
    token: str
    dep_length: int
    head: str


class SentenceAnalysisDict(TypedDict):
    word_features: list[WordFeaturesDict]
    lint_score: float
    difficulty_level: int
    mean_log_word_frequency: float
    max_sdl: int
    proportion_of_concrete_nouns: float
    content_words_per_clause: float


class SentenceAnalysis:
    """
    Sentence-level readability analysis for Dutch texts using the LiNT-II formula.

    This class extracts linguistic features from individual sentences and computes 
    readability scores based on word frequency, noun concreteness, syntactic dependency 
    length, and information density (content words per clause).

    Parameters
    ----------
    doc : Doc | Span
        A spaCy Doc or Span object representing a single sentence with NLP annotations 
        (tokenization, POS tags, dependencies, named entities).

    Attributes
    ----------
    doc : Doc | Span
        The input spaCy sentence object.
    word_features : list[WordFeatures]
        Linguistic features for each token in the sentence. Cached property.
    sdls : list[SDLInfo]
        Syntactic dependency length information for each token. Cached property.
        Each entry contains the token text, dependency length, and head text.
    mean_log_word_frequency : float
        Mean log frequency of content words (excluding proper nouns). Cached property.
    max_sdl : int
        Maximum syntactic dependency length in the sentence. Cached property.
    content_words_per_clause : float
        Ratio of content words (excluding adverbs) to clauses. Cached property.
    proportion_of_concrete_nouns : float
        Ratio of concrete nouns to all nouns (0.0-1.0). Cached property.
    lint_score : float
        LiNT readability score for the sentence (0-100, higher=more difficult).
        Cached property computed from sentence-level features.
    difficulty_level : int
        Difficulty level (1-4) derived from lint_score. Cached property.

    Methods
    -------
    from_text(text: str) -> SentenceAnalysis
        Create analysis from raw text string.
        Preprocesses text and applies NLP pipeline.
    calculate_lint_score() -> float
        Compute LiNT score for the sentence using extracted linguistic features.
    get_difficulty_level() -> int
        Convert LiNT score to difficulty level (1-4, where 4 = most difficult).
    count_content_words_excluding_adverbs() -> int
        Count content words excluding adverbs.
    count_clauses() -> int
        Count clauses by counting finite verbs (minimum 1).
    get_top_n_least_frequent(n: int = 5) -> list[tuple[str, float]]
        Return the n words with lowest frequency scores.
    get_detailed_analysis(n: int = 5) -> dict[str, Any]
        Return comprehensive analysis including all features and noun categorizations.
    as_dict() -> SentenceAnalysisDict
        Serialize analysis to dictionary format (used in the LiNT-II visualizer).

    Properties
    ----------
    concrete_nouns : list[str]
        All concrete nouns in the sentence.
    abstract_nouns : list[str]
        All abstract nouns in the sentence.
    undefined_nouns : list[str]
        Nouns not classified as concrete or abstract.
    unknown_nouns : list[str]
        Nouns not found in the frequency lexicon.
    content_words : list[str]
        All content words excluding adverbs (nouns, proper nouns, verbs, adjectives).
    finite_verbs : list[str]
        All finite verbs (verbs showing tense) in the sentence.

    Notes
    -----
    **Syntactic Dependency Length (SDL)**: The number of intervening tokens between 
    a word and its syntactic head.

    **Clauses**: Counted by identifying finite verbs (verbs showing tense). If no 
    finite verbs are detected, the sentence is treated as containing one clause.

    **Content words**: Nouns (NOUN), proper nouns (PROPN), lexical verbs (VERB),
    and adjectives (ADJ).

    **Noun categorization**: 
    - Concrete: Nouns referring to tangible entities (persons, animals, plants, 
    objects, substances, food, concrete events) or spatiotemporal referents (places, 
    times, measures).
    - Abstract: Nouns referring to intangible entities (abstract substances, abstract 
    events, organizations, abstract concepts).
    - Undefined: Nouns with multiple possible senses that could not be disambiguated.
    - Unknown: Nouns not in the nouns_sem_types dataset.

    Examples
    --------
    >>> from lint_ii import SentenceAnalysis
    >>> text = "Dit wordt een pijnlijk en haast onoverkomenlijk moment voor mij: het 
    geremde gemoed prijsgeven aan een onnozel stuk lijntjespapier."
    >>> analysis = SentenceAnalysis.from_text(text)
    >>> analysis.calculate_lint_score()
    82.97
    >>> analysis.get_difficulty_level()
    4
    >>> analysis.max_sdl
    2
    >>> analysis.content_words_per_clause
    10.0
    >>> analysis.get_top_n_least_frequent(3)
    [('onoverkomenlijk', 1.3555), ('lijntjespapier', 1.3555), ('geremde', 1.7)]

    See Also
    --------
    ReadabilityAnalysis : Document-level readability analysis
    WordFeatures : Token-level linguistic feature extraction
    LintScorer : Core LiNT scoring algorithms
    """

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

    @cached_property
    def lint_score(self) -> float:
        return self.calculate_lint_score()
    
    @cached_property
    def difficulty_level(self) -> int:
        return self.get_difficulty_level()

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
            'score': self.lint_score,
            'level': self.difficulty_level,
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

    def as_dict(self) -> SentenceAnalysisDict:
        return {
            'word_features': [feat.as_dict() for feat in self.word_features],
            'lint_score': self.lint_score,
            'difficulty_level': self.difficulty_level,
            'mean_log_word_frequency': self.mean_log_word_frequency,
            'max_sdl': self.max_sdl,
            'proportion_of_concrete_nouns': self.proportion_of_concrete_nouns,
            'content_words_per_clause': self.content_words_per_clause,
        }
