from functools import cached_property
from typing import TypedDict

from spacy.tokens import Token
from wordfreq import zipf_frequency

from lint_ii.linguistic_data import SuperSemTypes


class WordFeaturesDict(TypedDict):
    text: str
    word_frequency: float | None
    dep_length: int
    is_content_word_excl_propn: bool
    is_content_word_excl_adv: bool
    is_noun: bool
    is_finite_verb: bool
    super_sem_type: str | None
    is_abstract: bool
    is_concrete: bool
    is_undefined: bool
    is_unknown: bool


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

    @cached_property
    def text(self) -> str:
        return self.token.lower_

    @cached_property
    def word_frequency(self) -> float|None:
        """Word frequency using zipf scale."""
        if not self.is_content_word_excl_propn:
            return None
        freq = zipf_frequency(self.text, "nl")
        return freq if freq > 0 else 1.3555 # Default frequency for unknown words

    @property
    def dep_length(self) -> int:
        """
        Dependency length (number of intervening tokens) between a word and its syntactic head. The dep_length is 0 if the words are adjacent.
        """
        if self.token.dep_ in ["punct"]:
            return 0
        raw_len = self.token.head.i - self.token.i
        if raw_len == 0:
            return 0
        return int(abs(self.token.head.i - self.token.i) - 1)

    @property
    def is_content_word_excl_propn(self) -> bool:
        """Check if word is a content word, excluding proper nouns."""
        return self.token.pos_ in ["NOUN", "VERB", "ADJ", "ADV"]

    @property
    def is_content_word_excl_adv(self) -> bool:
        """Check if word is a content word, excluding adverbs."""
        return self.token.pos_ in ["NOUN", "PROPN", "VERB", "ADJ"]

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
        import lint_ii.linguistic_data.wordlists as wordlists
        if not self.is_noun:
            return None

        result = wordlists.noun_to_super_sem_type.get(self.text)

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

    def as_dict(self) -> WordFeaturesDict:
        return {
            'text': self.text,
            'word_frequency': self.word_frequency,
            'dep_length': self.dep_length,
            'is_content_word_excl_propn': self.is_content_word_excl_propn,
            'is_content_word_excl_adv': self.is_content_word_excl_adv,
            'is_noun': self.is_noun,
            'is_finite_verb': self.is_finite_verb,
            'super_sem_type': self.super_sem_type.value if self.super_sem_type else None,
            'is_abstract': self.is_abstract,
            'is_concrete': self.is_concrete,
            'is_undefined': self.is_undefined,
            'is_unknown': self.is_unknown,
        }
