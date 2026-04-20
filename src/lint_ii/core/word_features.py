from __future__ import annotations
from functools import cached_property
from typing import TypedDict, NotRequired, TYPE_CHECKING

from spacy.tokens import Token

from lint_ii import linguistic_data
from lint_ii.linguistic_data import SuperSemTypes
if TYPE_CHECKING:
    from lint_ii.core.sentence_analysis import SentenceAnalysis

class WordFeaturesDict(TypedDict):
    text: str
    pos: str
    tag: str
    word_frequency: NotRequired[float]
    dep_length: NotRequired[int]
    super_sem_type: NotRequired[str]
    punctuation: NotRequired[dict[str, str]]


class WordFeatures:
    """
    Token-level linguistic feature extraction for Dutch text analysis.

    This class wraps a spaCy Token and computes linguistic features used in the 
    LiNT-II readability analysis, including word frequency, syntactic dependency
    length, part-of-speech classification, and semantic categorization of nouns.

    Parameters
    ----------
    token : Token
        A spaCy Token object with NLP annotations (lemma, POS tag, dependencies, 
        named entity type).

    Attributes & Properties
    -----------------------
    token : Token
        The input spaCy token.
    text : str
        Lowercase form of the token.
    lemma : str
        Lowercase lemma of the token.
    word_frequency : float | None
        Word frequency from the SUBTLEX-NL corpus. Cached property.
    heads : list[Token]
        Syntactic heads of the token, with special handling for conjunctions. Cached property.
    dep_length : int
        The number of intervening tokens between the token and its syntactic head. Cached property.
    is_noun : bool
        True if token has one of the parts-of-speech: NOUN, PROPN.
    super_sem_type : SuperSemTypes | None
        Semantic type for nouns: 'concrete', 'abstract', 'undefined', or 'unknown'.
        Measurement unit symbols (e.g. km) are considered nouns as well.
    is_abstract : bool
        True if noun is semantically abstract (based on the annotations in NOUN_DATA or based on entity type heuristics).
    is_concrete : bool
        True if noun is semantically concrete (based on the annotations in NOUN_DATA or based on entity type heuristics).
    is_undefined : bool
        True if noun has both a concrete and an abstract meaning (based on the 
        annotations in NOUN_DATA).
    is_unknown : bool
        True if noun is not found in NOUN_DATA and could not be resolved based on entity type heuristics.
    is_content_word : bool
        True if token has one of the parts-of-speech: NOUN, PROPN, VERB, ADJ or is a
        manner adverb (from MANNER_ADVERBS list). Special cases: copulas and numerals 
        are excluded.
    is_content_word_excl_propn : bool
        True if token is content word but not a PROPN.
    is_finite_verb : bool
        True if token has the tag (fine-grained part-of-speech): WW|pv (verb that shows
        tense).
    is_passive_auxiliary : bool
        Indicator whether token is passive auxiliary. Cached property.
    is_in_subordinate_clause : bool
        Indicator whether token is part of a subordinate clause based on the dependency label. Cached property.
    is_pronoun : bool
        Indicator whether token is a pronoun. Cached property.
    pronoun_person : int | None
        Person of the pronoun (first, second, third). Cached property.
    is_human : bool
        Indicator whether token refers to a human. Cached property.
    is_entity_or_situation : bool
        Indicator whether word refers to entity or situation. True if token has one of the parts-of-speech: NOUN, PROPN, VERB or is a pronoun. Cached property.
    is_contextually_new : bool | None
        Indicator whether entity or situation is contextually new (i.e. did not appear in the preceding 50 tokens). Cached property.
    is_adj_mod : bool
        Indicator whether token is adjectival modifier.
    is_coordinated_constituent : bool
        Indicator whether token is a coordinated constituent.
        True if token has dependency label 'conj' and one of the following parts of speech: 'NOUN', 'PROPN', 'PRON', 'ADJ', 'NUM', 'ADV'.
        This excludes coordinated clauses.
    is_punctuation : bool
        Indicator whether token is punctuation.
    punctuation : dict[str, str] | None
        Attached punctuation to a token (used in the LiNT-II visualizer). Cached property.

    Methods
    -------
    from_text(text: str) -> WordFeatures
        Create feature extractor from a single word string.
        Note: this method is added for convenience and testing. Beware that spaCy may 
        be unable to correctly parse the word from a single word string context.
    as_dict() -> WordFeaturesDict
        Serialize features to dictionary format (used in the LiNT-II visualizer).

    Notes
    -----
    **Content Words**: Content words are defined as follows:

    Parts of speech      | Additional corrections
    ---------------------|-----------------------------
    nouns (NOUN)         | -
    proper nouns (PROPN) | -
    lexical verbs (VERB) | exclude copulas
    adjectives (ADJ)     | exclude numerals
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
    >>> from lint_ii import WordFeatures
    >>> word = WordFeatures.from_text("slaapt")
    >>> word.word_frequency
    4.756
    >>> word.is_finite_verb
    True
    >>> word.is_content_word
    True

    >>> word = WordFeatures.from_text("vrijheid")
    >>> word.super_sem_type
    <SuperSemTypes.ABSTRACT: 'abstract'>
    >>> word.is_abstract
    True

    See Also
    --------
    SentenceAnalysis : Sentence-level readability analysis
    ReadabilityAnalysis : Document-level readability analysis
    SuperSemTypes : Enum for semantic noun categorization
    """

    sentence_analysis: SentenceAnalysis | None = None

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

    # ── text, lemma ──────────────────────────────────────────────────────

    @property
    def text(self) -> str:
        return self.token.lower_

    @property
    def lemma(self) -> str:
        return self.token.lemma_.lower()

    # ── word frequency ───────────────────────────────────────────────────

    @cached_property
    def word_frequency(self) -> float | None:
        """
        Word frequency from the SUBTLEX-NL corpus.
        - Frequency is calculated for content words only.
        - For compounds listed in NOUN_DATA, the frequency of the base word is returned.
        - Unknown words (not in SUBTLEX-NL) default to 1.359 (zero count frequency).
        - Returns None for function words and proper nouns.
        - Returns None if the token or its lemma are in the SKIPLIST.
        """
        if not self.is_content_word_excl_propn:
            return None
        if self.lemma in self._FREQ_SKIPLIST or self.text in self._FREQ_SKIPLIST:
            return None

        text = self.text
        if self.is_noun and linguistic_data.WORD_FREQ_COMPOUND_ADJUSTMENT:
            text = self._NOUN_DATA.get(text, {}).get('head', text)

        zero_count_freq = 1.359228547196266  # log10(1 / total_count * 1e9)
        return self._FREQ_DATA.get(text, zero_count_freq) 

    # ── heads & dependency length ────────────────────────────────────────

    @cached_property
    def heads(self) -> list[Token]:
        """
        Syntactic heads of the token. The head is generally taken from spaCy, except for the two special cases below. 

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
        Dependency length is the number of intervening tokens between a word and its syntactic head. The dep_length is 0 if the words are adjacent.
        
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

    # ── noun semantic types ──────────────────────────────────────────────

    @property
    def is_noun(self) -> bool:
        """
        Indicator whether word is a noun.
        True if token has one of the parts-of-speech: NOUN, PROPN.
        """
        return self.token.pos_ in ["NOUN", "PROPN"]

    @property
    def super_sem_type(self) -> SuperSemTypes | None:
        """
        The semantic type of a noun.
        Measurement unit symbols (e.g. km) are considered nouns as well.
        """
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

    # ── content words ────────────────────────────────────────────────────

    @property
    def is_content_word(self) -> bool:
        """
        Indicator whether token is a content word.
        True if token has one of the parts-of-speech: NOUN, PROPN, VERB, ADJ or is a manner adverb (from MANNER_ADVERBS list).

        Special cases
        -------------
        - Numerals are excluded (sometimes tagged as ADJ)
        - Copulas are excluded (sometimes tagged as VERB)
        - Adverbs are excluded except for manner adverbs
        """
        if 'TW' in self.token.tag_: # TW = telwoord
            return False
        if self.token.dep_ == 'cop':
            return False
        return (
            self.token.pos_ in ["NOUN", "PROPN", "VERB", "ADJ"]
            or self.text in self._MANNER_ADVERBS
        )
    
    @property
    def is_content_word_excl_propn(self) -> bool:
        """Indicator whether word is a content word, excluding proper nouns."""
        return False if self.token.pos_ == 'PROPN' else self.is_content_word

    # ── finite verbs ─────────────────────────────────────────────────────

    @property
    def is_finite_verb(self) -> bool:
        """Indicator whether word is a finite verb."""
        return "WW|pv" in self.token.tag_ # WW|pv = werkwoord, persoonsvorm

    # ── passive & subordinate clause ─────────────────────────────────────

    @cached_property
    def is_passive_auxiliary(self) -> bool:
        """Indicator whether token is passive auxiliary."""
        return self.token.dep_ == 'aux:pass'

    @cached_property
    def is_in_subordinate_clause(self) -> bool:
        """
        Indicator whether token is part of a subordinate clause.
        
        Returns True if token:
        - has a dependency label 'acl:relcl', 'advcl', 'ccomp', 'csubj' or 'acl'
        - and token or one of its descendants is a verb
        
        The function uses the resolved dependency label. If a token is a conjunct the dependency label is recursively taken from its head.
        """
        subordinate_deps = ['acl:relcl', 'advcl', 'ccomp', 'csubj', 'acl']

        if self._resolved_dependency not in subordinate_deps:
            return False

        # token or one of its descendants is a verb 
        for token in self.token.subtree:
            if 'WW' in token.tag_:
                return True
        return False

    @cached_property
    def _resolved_dependency(self) -> str:
        """
        Token dependency label.
        
        If token is conjunct the dependency label is recursively taken from its head.
        """
        current_token = self.token
        while current_token.dep_ == 'conj':
            current_token = current_token.head
        return current_token.dep_

    # ── pronoun & human ──────────────────────────────────────────────────

    @cached_property
    def is_pronoun(self) -> bool:
        """Indicator whether token is a pronoun."""
        tag = self.token.tag_
        pron_types = ['|pers|', '|pr|', '|bez|']
        return 'VNW' in tag and any(i in tag for i in pron_types)

    @cached_property
    def pronoun_person(self) -> int | None:
        """Person of the pronoun (first, second, third)."""
        if not self.is_pronoun:
            return None

        for chr in self.token.tag_:
            if chr.isdigit():
                return int(chr)

    @cached_property
    def is_human(self) -> bool:
        """
        Indicator whether token refers to a human.
        Returns True if:
        - token is pronoun (excluding 'het')
        - token is an indefinite pronoun referring to humans (based on list)
        - entity type is 'PERSON'
        - lemma of the token has semantic type 'human' in NOUN_DATA list
        """
        if self.is_pronoun and self.text != 'het':
            return True
        
        indefinite_pronouns = [
            'iemand',
            'niemand',
            'elk',
            'ieder',
            'iedereen',
            'eenieder',
            'menigeen',
            'elkeen',
            'sommigen',
            'enigen',
            'anderen',
            'velen',
            'allen',
            'weinigen',
            'enkelen',
            'beiden',
        ]
        if self.token.tag_.startswith('VNW|onbep') and self.text in indefinite_pronouns:
            return True

        if not self.is_noun:
            return False

        if self.token.ent_type_ == 'PERSON':
            return True

        sem_type = self._NOUN_DATA.get(self.lemma,
        {}).get('sem_type', '')
        if sem_type == 'human':
            return True
        
        return False

    # ── entity / situation & contextual newness ──────────────────────────

    @cached_property
    def is_entity_or_situation(self) -> bool:
        """
        Indicator whether word refers to entity or situation.
        True if token has one of the parts-of-speech: NOUN, PROPN, VERB or is a pronoun.

        Special cases
        -------------
        - Copulas are excluded (sometimes tagged as VERB)
        """
        if self.token.dep_ == 'cop':
            return False
        if self.token.pos_ in ["NOUN", "PROPN", "VERB"]:
            return True
        if self.is_pronoun:
            return True
        return False

    @cached_property
    def is_contextually_new(self) -> bool | None:
        """
        Indicator whether entity or situation is contextually new (i.e. did not appear in the preceding 50 tokens).

        Special cases
        -------------
        - For pronouns we check if pronouns of the same person (1, 2, 3) appeared in the preceding 50 tokens 
        """
        if self.sentence_analysis is None:
            return None
        if self.sentence_analysis.readability_analysis is None:
            return None
        if self.token.i < 50:
            return None
        if not self.is_entity_or_situation:
            return None
        
        feats = self.sentence_analysis.readability_analysis.entities_and_situations
        context_start, context_end = self.token.i - 50, self.token.i
        context = [
            feat for feat in feats
            if context_start <= feat.token.i < context_end
        ]

        if self.is_pronoun:
            return not any(
                feat.pronoun_person == self.pronoun_person
                for feat in context
            )
        return not any(feat.lemma == self.lemma for feat in context)

    # ── modifiers & coordination ─────────────────────────────────────────

    @property
    def is_adj_mod(self) -> bool:
        """
        Indicator whether token is adjectival modifier.
        True if token has one of the following dependency labels:
        amod, nummod, nmod, nmod:poss, acl.
        """
        adj_mod_deps = [
            'amod',
            'nummod',
            'nmod',
            'nmod:poss',
            'acl',
        ]
        return self.token.dep_ in adj_mod_deps

    @property
    def is_coordinated_constituent(self) -> bool:
        """
        Indicator whether token is a coordinated constituent.
        True if token has dependency label 'conj' and one of the following parts of speech: 'NOUN', 'PROPN', 'PRON', 'ADJ', 'NUM', 'ADV'.
        This excludes coordinated clauses.
        """
        if self.token.dep_ != 'conj':
            return False
        
        included_pos = [
            'NOUN',
            'PROPN',
            'PRON',
            'ADJ',
            'NUM',
            'ADV',
        ]
        return self.token.pos_ in included_pos

    # ── punctuation ──────────────────────────────────────────────────────

    @property
    def is_punctuation(self) -> bool:
        """Indicator whether token is punctuation."""
        return self.token.is_punct

    @cached_property
    def punctuation(self) -> dict[str, str] | None:
        """Attached punctuation to a token. Used in the visualizer."""
        from collections import defaultdict

        punctuation = defaultdict(str)
        if self.token.is_punct:
            is_left_edge = self.token.i == 0
            is_right_edge = self.token.i == len(self.token.doc) - 1

            isolated = (
                (is_left_edge or self.token.nbor(-1).whitespace_)
                and (is_right_edge or self.token.whitespace_)
            )
            if isolated:
                punctuation['standalone'] = self.token.text
                return punctuation
            return None

        token = self.token
        while (
            token.i > 0
            and token.nbor(-1).is_punct
            and not token.nbor(-1).whitespace_
        ):
            token = token.nbor(-1)
            punctuation['leading'] = token.text + punctuation['leading']

        token = self.token
        while (
            token.i < len(token.doc) - 1
            and token.nbor(1).is_punct
            and not token.whitespace_
        ):
            token = token.nbor(1)
            punctuation['trailing'] += token.text

        return punctuation if punctuation else None

    # ── serialization ────────────────────────────────────────────────────

    def as_dict(self) -> WordFeaturesDict:
        result: WordFeaturesDict = {
            'text': self.text,
            'tag': self.token.tag_,
            'pos': self.token.pos_,
        }

        if (freq := self.word_frequency) is not None:
            result['word_frequency'] = freq
        if (dep := self.dep_length) > 0:
            result['dep_length'] = dep
        if (sem := self.super_sem_type) is not None:
            result['super_sem_type'] = sem.value
        if (punct := self.punctuation) is not None:
            result['punctuation'] = punct

        return result