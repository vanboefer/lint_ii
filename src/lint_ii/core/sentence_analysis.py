
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

    Attributes & Properties
    -----------------------
    doc : Doc | Span
        The input spaCy sentence object.
    word_features : list[WordFeatures]
        Linguistic features for each token in the sentence. Cached property.
    sent_length : int
        Number of tokens in the sentence (excluding punctuation).
    sdls : list[SDLInfo]
        Syntactic dependency length information for each token.
        Each entry contains the token text, dependency length, and and a list of token's heads. For one-word sentences, an empty list is returned. Cached property.
    max_sdl : int | None
        Maximum syntactic dependency length in the sentence. 
        If there are no SDLs (i.e. one-word sentence), returns None. Cached property.
    concrete_nouns : list[str]
        All concrete nouns in the sentence.
    abstract_nouns : list[str]
        All abstract nouns in the sentence.
    undefined_nouns : list[str]
        Nouns that have both a concrete and an abstract meaning.
    unknown_nouns : list[str]
        All unknown nouns in the sentence: not found in NOUN_DATA and could not be resolved based on entity type heuristics.
    proportion_of_concrete_nouns : float | None
        Proportion of concrete nouns out of the total nouns in the sentence.
        Nouns of type `unknown` (not in the list) are excluded from the totals count.
        Returns None if totals are 0, i.e. there are no nouns or only `unknown` nouns in the sentence. Cached property.
    pronouns : dict[int, list[str]]
        Pronouns in the sentence categorized by person (first, second, third).
    content_words : list[str]
        All content words in the sentence.
    finite_verbs : list[str]
        All finite verbs (verbs showing tense) in the sentence.
    has_passive : bool
        Indicator whether sentence has one or more passive auxiliaries. Cached property.
    passives : list[Span]
        List of passive verbal phrases. Cached property.
    has_subordinate_clause : bool
        Indicator whether sentence has one or more subordinate clauses. Cached property.
    subordinate_clauses : list[Span]
        List of subordinate clauses in the sentence. Cached property.
    content_words_per_clause : float | None
        Number of content words per clause. Returns None if there are no finite verbs in the sentence (i.e. no clause). Cached property.
    mean_log_word_frequency : float | None
        Mean log frequency of content words (excluding proper nouns).
        Returns None if there are no frequencies in the sentence, i.e. no content words or all the content words are in the SKIPLIST. Cached property.
    lint : LintScorer
        LintScorer object that contains the score (lint.score) and the difficulty level (lint.level) for the sentence. Cached property.

    Methods
    -------
    from_text(text: str) -> SentenceAnalysis
        Create analysis from text string. Preprocesses text and applies spaCy NLP pipeline.
    get_top_n_least_frequent(n: int = 5) -> list[tuple[str, float]]
        Return the n words with lowest frequency scores.
    get_detailed_analysis(n: int = 5) -> dict[str, Any]
        Return comprehensive analysis including all feature values.
    as_dict() -> SentenceAnalysisDict
        Serialize analysis to dictionary format (used in the LiNT-II visualizer).

    Notes
    -----
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
    If a noun is not found in the NOUN_DATA, we try to resolve based on named entity type: names of people and locations are set to "concrete", names of organizations are set to "abstract".

    Examples
    --------
    >>> from lint_ii import SentenceAnalysis
    >>> text = "Dit wordt een pijnlijk en haast onoverkomenlijk moment voor mij: het 
    geremde gemoed prijsgeven aan een onnozel stuk lijntjespapier."
    >>> analysis = SentenceAnalysis.from_text(text)
    >>> analysis.lint.score
    75.4232676597771
    >>> analysis.lint.level
    4
    >>> analysis.max_sdl
    7
    >>> analysis.content_words_per_clause
    10.0
    >>> analysis.get_top_n_least_frequent(3)
    [('onoverkomenlijk', 1.359228547196266), ('lijntjespapier', 1.359228547196266),('geremde', 1.9612885385242282)]

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
    def sent_length(self) -> int:
        """Number of tokens in the sentence (excluding punctuation)."""
        return len([wf for wf in self.word_features if not wf.is_punctuation])

    @cached_property
    def sdls(self) -> list[SDLInfo]:
        """
        Syntactic dependency length information for each token.
        Each entry contains the token text, dependency length, and a list of token's heads.

        Special case
        -------------
        If the sentence consists of less than 2 tokens (excluding punctuation), an empty list is returned; i.e. there are no SDL's for a one-word sentence.
        """
        if len([wf for wf in self.word_features if not wf.is_punctuation]) < 2:
            return []
        return [
            {
                'token': feat.text,
                'dep_length': feat.dep_length,
                'heads': [head.text for head in feat.heads],
            }
            for feat in self.word_features
        ]

    @cached_property
    def max_sdl(self) -> int | None:
        """
        Maximum dependency length in the sentence.
        If there are no SDLs (i.e. one-word sentence), returns None.
        """
        values = {sdl['dep_length'] for sdl in self.sdls}
        return max(values, default=None)
    
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

    @cached_property
    def proportion_of_concrete_nouns(self) -> float | None:
        """
        Proportion of concrete nouns out of the total nouns in the sentence.
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

    @property
    def pronouns(self) -> dict[int, list[str]]:
        """Pronouns in the sentence categorized by person (first, second, third)."""
        from collections import defaultdict

        dct = defaultdict(list)
        for feat in self.word_features:
            if feat.is_pronoun:
                dct[feat.pronoun_person].append(feat.text)
        return dct

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
    def has_passive(self) -> bool:
        """Indicator whether sentence has one or more passive auxiliaries."""
        return any(feat.is_passive_auxiliary for feat in self.word_features)

    @cached_property
    def passives(self) -> list[Span]:
        """List of passive verbal phrases."""
        return [
            self._get_span_of_passive_verbal_phrase(feat)
            for feat in self.word_features
            if feat.is_passive_auxiliary
        ]
    
    def _get_span_of_passive_verbal_phrase(self, feat: WordFeatures) -> Span|None:
        """Get passive verbal phrase as span from token and its heads."""
        if not feat.is_passive_auxiliary:
            return None
        
        indices = [feat.token.i]
        indices.extend(head.i for head in feat.heads)

        return feat.token.sent[min(indices):max(indices) + 1]

    @cached_property
    def has_subordinate_clause(self) -> bool:
        """
        Indicator whether sentence has one or more subordinate clauses.
        
        Loops through tokens in the sentence. Returns True if any token:
        - has a dependency label 'acl:relcl', 'advcl' or 'ccomp'
        - or has a dependency label 'acl' and:
            - is itself a finite verb
            - or has a child that is a finite verb
        """
        return any(feat.is_in_subordinate_clause for feat in self.word_features)

    @cached_property
    def subordinate_clauses(self) -> list[Span]:
        """List of subordinate clauses in the sentence."""
        return [
            self._get_span_of_subordinate_clause(feat)
            for feat in self.word_features
            if feat.is_in_subordinate_clause
        ]

    def _get_span_of_subordinate_clause(self, feat: WordFeatures) -> Span|None:
        """Get subordinate clause as span from token and its children."""
        if not feat.is_in_subordinate_clause:
            return None

        indices = [feat.token.i]
        if feat.token.children:
            indices.extend(child.i for child in feat.token.children)
        return feat.token.sent[min(indices):max(indices) + 1]

    @cached_property
    def content_words_per_clause(self) -> float | None:
        """
        Number of content words per clause.
        Returns None if there are no finite verbs in the sentence (i.e. no clause).
        """
        if not self.finite_verbs:
            return None
        return len(self.content_words) / len(self.finite_verbs)
    
    @cached_property
    def mean_log_word_frequency(self) -> float | None:
        """
        Mean log frequency of content words (excluding proper nouns) in the sentence.
        Returns None if there are no frequencies in the sentence, i.e. no content words or all the content words are in the SKIPLIST.
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
    def lint(self) -> LintScorer:
        """
        LintScorer object that contains the score and the difficulty level for the sentence.
        """
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
            'sent_length': self.sent_length,
            'max_sdl': self.max_sdl,
            'sdls': self.sdls,
            'content_words_per_clause': self.content_words_per_clause,
            'content_words': self.content_words,
            'finite_verbs': self.finite_verbs,
            'passives': self.passives,
            'subordinate_clauses': self.subordinate_clauses,
            'pronouns_first_person': self.pronouns[1],
            'pronouns_second_person': self.pronouns[2],
            'pronouns_third_person': self.pronouns[3],
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
