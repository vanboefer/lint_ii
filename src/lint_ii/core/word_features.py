from functools import cached_property
from typing import TypedDict, NotRequired

from spacy.tokens import Token
from wordfreq import zipf_frequency

from lint_ii import linguistic_data
from lint_ii.linguistic_data import SuperSemTypes


class WordFeaturesDict(TypedDict):
    text: str
    word_frequency: NotRequired[float]
    dep_length: NotRequired[int]
    super_sem_type: NotRequired[str]
    punct_placement: NotRequired[str]


class WordFeatures:
    """Linguistic features for individual words."""

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
    def _NOUN_DATA(self) -> dict[str, dict[str, str|bool]]:
        import lint_ii.linguistic_data.wordlists as wordlists
        return wordlists.NOUN_DATA

    @property
    def _FREQ_DATA(self) -> dict[str, float]:
        import lint_ii.linguistic_data.wordlists as wordlists
        return wordlists.FREQ_DATA

    @property
    def _MANNER_ADVERBS(self) -> dict[str, dict[str, str|bool]]:
        import lint_ii.linguistic_data.wordlists as wordlists
        return wordlists.MANNER_ADVERBS

    @property
    def text(self) -> str:
        return self.token.lower_

    @property
    def head(self) -> Token:
        """
        Head of the token.

        Special cases:
        =============
        - Conjunctions: If a token is in a conjunction then the head of the last conjunct is taken recursively from the first. This is necessary since spaCy considers the first conjunct as the head of the second (which we consider incorrect).
        """
        current_token = self.token
        while current_token.dep_ == 'conj':
            current_token = current_token.head
        return current_token.head

    @cached_property
    def word_frequency(self) -> float|None:
        """Word frequency from the SUBTLEX-NL corpus."""
        if not self.is_content_word_excl_propn:
            return None

        text = self.text
        # because PROPN was filtered out above here we only get NOUN
        if self.is_noun and linguistic_data.WORD_FREQ_COMPOUND_ADJUSTMENT:
            text = self._NOUN_DATA.get(text, {}).get('head', text)

        zero_count_freq = 1.359228547196266  # log10(1 / total_count * 1e9)
        return self._FREQ_DATA.get(text, zero_count_freq) 

    @property
    def dep_length(self) -> int:
        """
        Dependency length (number of intervening tokens) between a word and its syntactic head. The dep_length is 0 if the words are adjacent.

        Special cases:
        =============
        - Punctuation: (a) punctuation marks are not counted as intervening tokens, (b) for a punctuation mark, the dependency length is always 0.
        - Conjunctions: If a token is in a conjunction then the head of the second conjunct is taken from the first. This is necessary since spaCy considers the first conjunct as the head of the second (which we consider incorrect).
        """
        if self.token.dep_ == 'punct':
            return 0

        span = sorted([self.token.i, self.head.i])
        part = self.token.doc[slice(*span)]

        dep_length = len([t for t in part if t.dep_ != 'punct']) - 1
        return dep_length if dep_length >= 0 else 0

    @property
    def is_content_word_excl_propn(self) -> bool:
        """Check if word is a content word, excluding proper nouns."""
        return self.token.pos_ in ["NOUN", "VERB", "ADJ", "ADV"]

    @property
    def is_content_word_excl_adv(self) -> bool:
        """
        Check if word is a content word.
        Adverbs are excluded except for manner adverbs.
        """
        return (
            self.token.pos_ in ["NOUN", "PROPN", "VERB", "ADJ"]
            or self.token.text in self._MANNER_ADVERBS
        )

    @property
    def is_noun(self) -> bool:
        """Check if word is a noun."""
        return self.token.pos_ in ["NOUN", "PROPN"]

    @property
    def is_finite_verb(self) -> bool:
        """Check if word is a finite verb."""
        return "WW|pv" in self.token.tag_

    @property
    def super_sem_type(self) -> SuperSemTypes|None:
        if not self.is_noun:
            return None

        result = self._NOUN_DATA.get(self.text, {}).get('super_sem_type')

        if result is None:
            return SuperSemTypes('unknown')

        return SuperSemTypes(result)

    @property
    def is_abstract(self) -> bool:
        return self.super_sem_type == SuperSemTypes.ABSTRACT

    @property
    def is_concrete(self) -> bool:
        return self.super_sem_type == SuperSemTypes.CONCRETE

    @property
    def is_undefined(self) -> bool:
        return self.super_sem_type == SuperSemTypes.UNDEFINED

    @property
    def is_unknown(self) -> bool:
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
