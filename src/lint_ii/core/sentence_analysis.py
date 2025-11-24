
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
    heads: list[str]


class SentenceAnalysisDict(TypedDict):
    word_features: list[WordFeaturesDict]
    lint_score: float | None
    difficulty_level: int | None
    mean_log_word_frequency: float
    max_sdl: int | None
    proportion_of_concrete_nouns: float
    content_words_per_clause: float


class SentenceAnalysis:
    """
    Sentence-level readability analysis for Dutch texts using the LiNT-II formula.

    This class extracts linguistic features from individual sentences and computes 
    readability scores based on four linguistic features: word frequency, 
    syntactic dependency length, content words per clause, and proportion of concrete nouns.

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
        Ratio of content words to clauses. Cached property.
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
        Create analysis from raw text string. Preprocesses text and applies NLP pipeline.
    calculate_lint_score() -> float
        Compute LiNT score for the sentence using extracted linguistic features.
    get_difficulty_level() -> int
        Convert LiNT score to difficulty level (1-4, where 4 = most difficult).
    count_content_words() -> int
        Count content words.
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
        Nouns that have both a concrete and an abstract meaning.
    unknown_nouns : list[str]
        Nouns not found in NOUN_DATA.
    content_words : list[str]
        All content words.
    finite_verbs : list[str]
        All finite verbs (verbs showing tense) in the sentence.

    Notes
    -----
    **Syntactic Dependency Length (SDL)**: The number of intervening tokens between 
    a word and its syntactic head.

    **Clauses**: Counted by identifying finite verbs (verbs showing tense). If no 
    finite verbs are detected, the sentence is treated as containing one clause.

    **Content Words**: Content words are defined as follows:

    Parts of speech      | Additional corrections
    ---------------------|-----------------------------
    nouns (NOUN)         | -
    proper nouns (PROPN) | -
    lexical verbs (VERB) | exclude copulas
    adjectives (ADJ)     | exclude numerical adjectives
    adverbs (ADV)        | include only MANNER_ADVERBS list

    **Noun Categorization**: 
    The noun categorizarion is based on the annotations in NOUN_DATA:
    - Concrete: Nouns referring to tangible entities (persons, animals, plants, 
    objects, substances, food, concrete events) or spatiotemporal referents (places, 
    times, measures).
    - Abstract: Nouns referring to intangible entities (abstract substances, abstract 
    events, organizations, abstract concepts).
    - Undefined: Nouns that have both a concrete sense and an abstract sense.
    - Unknown: Nouns not in the NOUN_DATA.

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
    LintScorer : LiNT scoring algorithms
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
        """
        Create analysis from text string:
        (a) Load spaCy model
        (b) Pre-process text (clean-up) and create spaCy Doc object
        """
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
        """
        The dependency length (number of intervening tokens) 
        between a token and its syntactic head, for each token in the sentence.
        """
        if len([wf for wf in self.word_features if wf.token.pos_ != 'PUNCT']) < 2:
            return []
        return [
            {
                'token': feat.text,
                'dep_length': feat.dep_length,
                'heads': [head.text for head in feat.heads],
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
        """All content words in the sentence."""
        return [
            feat.text for feat in self.word_features
            if feat.is_content_word
        ]

    @property
    def finite_verbs(self) -> list[str]:
        """All finite verbs in the sentence."""
        return [
            feat.text for feat in self.word_features
            if feat.is_finite_verb
        ]

    @cached_property
    def mean_log_word_frequency(self) -> float | None:
        """Mean log word frequency for the sentence."""
        frequencies = [
            freq
            for feat in self.word_features
            if (freq := feat.word_frequency) is not None
        ]
        if not frequencies:
            return None
        return statistics.mean(frequencies)

    @cached_property
    def max_sdl(self) -> int | None:
        """Maximum dependency length in the sentence."""
        values = {sdl['dep_length'] for sdl in self.sdls}
        return max(values, default=None)

    @cached_property
    def content_words_per_clause(self) -> float | None:
        """Number of content words per clause."""
        if not self.finite_verbs:
            return None
        return len(self.content_words) / len(self.finite_verbs)

    @cached_property
    def proportion_of_concrete_nouns(self) -> float | None:
        """
        Proportion of concrete nouns out of all nouns in the sentence.
        Nouns of type `unknown` (not in the list) are excluded from the totals count.
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
            max_sdl = self.max_sdl,
            content_words_per_clause = self.content_words_per_clause,
            proportion_concrete = self.proportion_of_concrete_nouns,
        )

    def get_top_n_least_frequent(self, n: int = 5) -> list[tuple[str, float]]:
        """Get the top n least frequent words in the sentence."""
        frequencies = {
            feat.text:freq
            for feat in self.word_features
            if (freq := feat.word_frequency) is not None
        }
        if n == -1:
            return sorted(frequencies.items(), key=itemgetter(1))
        return sorted(frequencies.items(), key=itemgetter(1))[:n]

    def get_detailed_analysis(self, n: int = 5) -> dict[str, Any]:
        """Get detailed analysis for the sentence."""
        return {
            'text': self.doc.text,
            'score': self.lint.score,
            'level': self.lint.level,
            'mean_log_word_frequency': self.mean_log_word_frequency,
            'top_n_least_freq_words': self.get_top_n_least_frequent(n=n),
            'proportion_concrete_nouns': self.proportion_of_concrete_nouns,
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
            'lint_score': self.lint.score,
            'difficulty_level': self.lint.level,
            'mean_log_word_frequency': self.mean_log_word_frequency,
            'max_sdl': self.max_sdl,
            'proportion_of_concrete_nouns': self.proportion_of_concrete_nouns,
            'content_words_per_clause': self.content_words_per_clause,
        }
