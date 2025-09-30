from functools import cached_property

import pyarrow.compute as pc
from spacy.tokens import Token
from wordfreq import zipf_frequency

from lint_ii import wordlists


class WordFeatures:
    """Linguistic features for individual words."""

    def __init__(
        self,
        token: Token,
    ) -> None:
        self.token = token

    @cached_property
    def text(self) -> str:
        return self.token.text.lower()

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
    def super_sem_type(self) -> wordlists.SuperSemTypes:
        if not self.is_noun:
            return None

        result = wordlists.noun_to_super_sem_type.get(self.text)

        if result is None:
            return wordlists.SuperSemTypes('unknown')

        return wordlists.SuperSemTypes(result)

    @property
    def is_abstract(self) -> bool:
        return self.super_sem_type == wordlists.SuperSemTypes.ABSTRACT

    @property
    def is_concrete(self) -> bool:
        return self.super_sem_type == wordlists.SuperSemTypes.CONCRETE

    @property
    def is_undefined(self) -> bool:
        return self.super_sem_type == wordlists.SuperSemTypes.UNDEFINED

    @property
    def is_unknown(self) -> bool:
        return self.super_sem_type == wordlists.SuperSemTypes.UNKNOWN
