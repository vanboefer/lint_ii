from functools import cached_property
from typing import TypedDict, NotRequired

from spacy.tokens import Token

from lint_ii import linguistic_data
from lint_ii.linguistic_data import SuperSemTypes


class WordFeaturesDict(TypedDict):
    text: str
    word_frequency: NotRequired[float]
    dep_length: NotRequired[int]
    super_sem_type: NotRequired[str]
    punct_placement: NotRequired[str]


class WordFeatures:
    """
    Token-level linguistic feature extraction for Dutch text analysis.

    This class wraps a spaCy Token and computes linguistic features used in the 
    LiNT-II readability formula, including word frequency, syntactic dependency length, 
    part-of-speech classification, and semantic categorization of nouns.

    Parameters
    ----------
    token : Token
        A spaCy Token object with NLP annotations (lemma, POS tag, dependencies, 
        named entity type).

    Attributes
    ----------
    token : Token
        The input spaCy token.
    text : str
        Lowercase form of the token.
    head : Token
        Syntactic head of the token, with special handling for conjunctions.
    word_frequency : float | None
        Log frequency for content words. Cached property.
        Returns None for function words and proper nouns.
        Unknown words (not in SUBTLEX-NL) default to 1.359.
    dep_length : int
        Syntactic dependency length (number of intervening tokens between token and 
        head).
    super_sem_type : SuperSemTypes | None
        Semantic type for nouns: 'concrete', 'abstract', 'undefined', or 'unknown'.
    punct_placement : str | None
        Punctuation placement: 'embedded', 'trailing', 'leading', or 'standalone'.

    Methods
    -------
    from_text(text: str) -> WordFeatures
        Create feature extractor from a single word string.
        Note: this method is added for convenience and testing. Beware that spaCy may 
        be unable to correctly parse the word from a single word string context.
    as_dict() -> WordFeaturesDict
        Serialize features to dictionary format (used in the LiNT-II visualizer).

    Properties
    ----------
    is_content_word_excl_propn : bool
        True if token is content word but not a PROPN.
    is_content_word : bool
        True if token has one of the parts-of-speech: NOUN, PROPN, VERB, ADJ or is a
        manner adverb (from MANNER_ADVERBS list). Special cases: copulas and numerical 
        adjectives are excluded.
    is_noun : bool
        True if token has one of the parts-of-speech: NOUN, PROPN.
    is_finite_verb : bool
        True if token has the tag (fine-grained part-of-speech): WW|pv (verb that shows
        tense).
    is_abstract : bool
        True if noun is semantically abstract (based on the annotations in NOUN_DATA).
    is_concrete : bool
        True if noun is semantically concrete (based on the annotations in NOUN_DATA).
    is_undefined : bool
        True if noun has both a concrete and an abstract meaning (based on the 
        annotations in NOUN_DATA).
    is_unknown : bool
        True if noun is not found in NOUN_DATA.

    Notes
    -----
    **Word Frequency**: Uses the log frequency calculated from the SUBTLEX-NL corpus 
    (FREQ_DATA). Only content words (excluding proper nouns) get frequency scores. 
    Unknown words receive a default zero count frequency.

    **Dependency Length**: The number of tokens between a word and its syntactic head. 
    Punctuation is excluded from counting. For example:
        - "de kat": dep_length = 0 (adjacent)
        - "de gelaarsde kat": dep_length for "de" = 1

    Special handling for conjunctions: The head of coordinated elements is determined 
    by following the conjunction chain to find the true syntactic head, rather than 
    using spaCy's default behavior where the first conjunct heads the second.

    **Noun Categorization**: 
    The noun categorizarion is based on the annotations in NOUN_DATA:
    - Concrete: Nouns referring to tangible entities (persons, animals, plants, 
    objects, substances, food, concrete events) or spatiotemporal referents (places, 
    times, measures).
    - Abstract: Nouns referring to intangible entities (abstract substances, abstract 
    events, organizations, abstract concepts).
    - Undefined: Nouns that have both a concrete sense and an abstract sense.
    - Unknown: Nouns not in the NOUN_DATA.

    **Content Words**: Content words are defined as follows:

    Parts of speech      | Additional corrections
    ---------------------|-----------------------------
    nouns (NOUN)         | -
    proper nouns (PROPN) | -
    lexical verbs (VERB) | exclude copulas
    adjectives (ADJ)     | exclude numerical adjectives
    adverbs (ADV)        | include only MANNER_ADVERBS list

    **Finite Verbs**: Identified using Dutch CGN part-of-speech tags. A verb is finite 
    if its tag contains "WW|pv" (werkwoord, persoonsvorm).

    Examples
    --------
    >>> from lint_ii import WordFeatures
    >>> word = WordFeatures.from_text("slaapt")
    >>> word.word_frequency
    4.26
    >>> word.is_finite_verb
    True
    >>> word.is_content_word
    True

    >>> noun = WordFeatures.from_text("vrijheid")
    >>> noun.super_sem_type
    <SuperSemTypes.ABSTRACT: 'abstract'>
    >>> noun.is_abstract
    True

    See Also
    --------
    SentenceAnalysis : Sentence-level readability analysis
    ReadabilityAnalysis : Document-level readability analysis
    SuperSemTypes : Enum for semantic noun categorization
    """

    def __init__(
        self,
        token: Token,
    ) -> None:
        self.token = token

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.text}')"

    @classmethod
    def from_text(
        cls,
        text: str,
    ) -> 'WordFeatures':
        from lint_ii.linguistic_data.nlp_model import NLP_MODEL
        doc = NLP_MODEL(text)
        return cls(doc[0])

    @property
    def _wordlists(self):
        """Lazy-load wordlists module."""
        import lint_ii.linguistic_data.wordlists as wordlists
        return wordlists

    @property
    def _NOUN_DATA(self) -> dict[str, dict[str, str]]:
        return self._wordlists.NOUN_DATA

    @property
    def _MEASUREMENT_UNITS(self) -> list[str]:
        return self._wordlists.MEASUREMENT_UNITS

    @property
    def _FREQ_DATA(self) -> dict[str, float]:
        return self._wordlists.FREQ_DATA

    @property
    def _FREQ_SKIPLIST(self) -> list[str]:
        return self._wordlists.FREQ_SKIPLIST

    @property
    def _MANNER_ADVERBS(self) -> list[str]:
        return self._wordlists.MANNER_ADVERBS

    @property
    def text(self) -> str:
        return self.token.lower_

    @property
    def lemma(self) -> str:
        return self.token.lemma_.lower()

    @cached_property
    def word_frequency(self) -> float|None:
        """Word frequency from the SUBTLEX-NL corpus."""
        if not self.is_content_word_excl_propn:
            return None
        if self.lemma in self._FREQ_SKIPLIST or self.text in self._FREQ_SKIPLIST:
            return None

        text = self.text
        # because PROPN was filtered out above here we only get NOUN
        if self.is_noun and linguistic_data.WORD_FREQ_COMPOUND_ADJUSTMENT:
            text = self._NOUN_DATA.get(text, {}).get('head', text)

        zero_count_freq = 1.359228547196266  # log10(1 / total_count * 1e9)
        return self._FREQ_DATA.get(text, zero_count_freq) 
    
    @cached_property
    def heads(self) -> list[Token]:
        """
        Heads of the token. The head is generally taken from spaCy, except for the two special cases below. 

        Special cases
        -------------
        - Conjunctions: If a token is in a conjunction then the head of the last conjunct is taken recursively from the first. This is necessary since spaCy considers the first conjunct as the head of the second (which we consider incorrect).
        - If a token is the subject, we check whether its head (ROOT) has conjuncts. If so, we consider the conjuncts as the heads of the subject as well. For example, in the sentence 'Dat geluid klinkt in het midden- en kleinbedrijf en moet worden gehoord.', the subject 'geluid' has two heads ['klinkt', 'gehoord'].
        """
        current_token = self.token
        while current_token.dep_ == 'conj':
            current_token = current_token.head
        if current_token.dep_ == 'nsubj' and len(current_token.head.conjuncts) > 0:
            return [
                current_token.head,
                *[conj for conj in current_token.head.conjuncts]
            ]
        return [current_token.head]

    @cached_property
    def dep_length(self) -> int:
        """
        Dependency length (number of intervening tokens) between a word and its syntactic head. The dep_length is 0 if the words are adjacent.
        
        If a word has multiple heads (see the special case for subjects below), we calculate all dep_lengths and take the biggest one.

        Special cases
        -------------
        - Punctuation: (a) punctuation marks are not counted as intervening tokens, (b) for a punctuation mark, the dependency length is always 0.
        - Conjunctions: If a token is in a conjunction then the head of the last conjunct is taken recursively from the first. This is necessary since spaCy considers the first conjunct as the head of the second (which we consider incorrect).
        - If a token is the subject, we check whether its head (ROOT) has conjuncts. If so, we consider the conjuncts as the heads of the subject as well. For example, in the sentence 'Dat geluid klinkt in het midden- en kleinbedrijf en moet worden gehoord.', the subject 'geluid' has two heads ['klinkt', 'gehoord']. Since the dependency length between 'geluid' and 'gehoord' is bigger than the one between 'geluid' and 'klinkt', we return the former.
        """
        return max(self._calculate_dep_length(head) for head in self.heads)

    def _calculate_dep_length(self, head: Token) -> int:
        if self.token.dep_ == 'punct':
            return 0

        span = sorted([self.token.i, head.i])
        part = self.token.doc[slice(*span)]

        dep_length = len([t for t in part if t.dep_ != 'punct']) - 1
        return dep_length if dep_length >= 0 else 0

    @property
    def is_content_word_excl_propn(self) -> bool:
        """Indicator whether word is a content word, excluding proper nouns."""
        return False if self.token.pos_ == 'PROPN' else self.is_content_word

    @property
    def is_content_word(self) -> bool:
        """
        Indicator whether word is a content word:
        - Numerical adjectives are excluded
        - Copulas are excluded
        - Adverbs are excluded except for manner adverbs
        """
        if 'TW' in self.token.tag_:
            return False
        if self.token.dep_ == 'cop':
            return False
        return (
            self.token.pos_ in ["NOUN", "PROPN", "VERB", "ADJ"]
            or self.text in self._MANNER_ADVERBS
        )

    @property
    def is_noun(self) -> bool:
        """Indicator whether word is a noun."""
        return self.token.pos_ in ["NOUN", "PROPN"]

    @property
    def is_finite_verb(self) -> bool:
        """Indicator whether word is a finite verb."""
        return "WW|pv" in self.token.tag_

    @property
    def super_sem_type(self) -> SuperSemTypes|None:
        """The semantic type of a noun or measurement unit symbol."""
        # take nouns and 'SPEC' tokens (accounts for cm, km, etc.)
        if not self.is_noun and 'SPEC' not in self.token.tag_:
            return None
        
        if self.is_noun:
            return self._get_super_sem_type_for_noun()

        return (
            SuperSemTypes('concrete')
            if self.text in self._MEASUREMENT_UNITS
            else None
        )

    def _get_super_sem_type_for_noun(self) -> SuperSemTypes:
        """
        Get the semantic type of a noun from NOUN_DATA.

        - If the word is not on the list, try to look for the lemma (e.g., "paardje" is 
        not on the list, but its lemma "paard" is)
        - If neither word nor lemma is on the list, try to resolve based on named 
        entity type: names of people and locations are set to "concrete", names of 
        organizations are set to "abstract".
        """
        assert self.is_noun, "Token is not a noun."

        # get word from noun list
        result = self._NOUN_DATA.get(self.text)

        # if word not in list then try to resolve on lemma
        if result is None:
            result = self._NOUN_DATA.get(self.lemma)
  
        # if result was found then return the semantic type
        if result is not None:
            return SuperSemTypes(result.get('super_sem_type'))

        # if word and lemma not in list then try to resolve based on entity type
        if self.token.ent_type_ in ('PERSON', 'GPE'):
            return SuperSemTypes('concrete')
        if self.token.ent_type_ == 'ORG':
            return SuperSemTypes('abstract')
        
        # resolve as unknown if all else fails
        return SuperSemTypes('unknown')

    @property
    def is_abstract(self) -> bool:
        """Indicator whether semantic type is abstract."""
        return self.super_sem_type == SuperSemTypes.ABSTRACT

    @property
    def is_concrete(self) -> bool:
        """Indicator whether semantic type is concrete."""
        return self.super_sem_type == SuperSemTypes.CONCRETE

    @property
    def is_undefined(self) -> bool:
        """Indicator whether semantic type is undefined."""
        return self.super_sem_type == SuperSemTypes.UNDEFINED

    @property
    def is_unknown(self) -> bool:
        """Indicator whether semantic type is unknown."""
        return self.super_sem_type == SuperSemTypes.UNKNOWN

    @property
    def punct_placement(self) -> str | None:
        """Placement of punctuation relative to adjacent tokens."""
        if not self.token.is_punct:
            return None

        has_space_before = self.token.i > 0 and self.token.nbor(-1).whitespace_
        has_space_after = self.token.whitespace_

        if not has_space_before and not has_space_after:
            return 'embedded'
        elif not has_space_before:
            return 'trailing'
        elif not has_space_after:
            return 'leading'
        else:
            return 'standalone'

    def as_dict(self) -> WordFeaturesDict:
        result: WordFeaturesDict = {'text': self.text}

        if (freq := self.word_frequency) is not None:
            result['word_frequency'] = freq
        if (dep := self.dep_length) > 0:
            result['dep_length'] = dep
        if (sem := self.super_sem_type) is not None:
            result['super_sem_type'] = sem.value
        if (punct := self.punct_placement) is not None:
            result['punct_placement'] = punct

        return result
