from functools import cached_property

from spacy.tokens import Token
from wordfreq import zipf_frequency


class WordFeatures:
    """Linguistic features for individual words."""

    def __init__(
        self,
        token: Token,
        abstract_nouns_list: list[str]|None = None,
    ) -> None:
        self.token = token
        self.abstract_nouns_list = [] if abstract_nouns_list is None else abstract_nouns_list

    @cached_property
    def word_frequency(self) -> float|None:
        """Word frequency using zipf scale."""
        if not self.is_content_word_excl_propn:
            return None
        freq = zipf_frequency(self.token.text, "nl")
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
    def is_abstract(self) -> bool:
        """Check if word is an abstract noun: either an abstract named entity or listed in the RBN list of abstract nouns."""
        return self.is_abstract_entity or self.is_in_abstract_nouns_list

    @property
    def is_abstract_entity(self) -> bool:
        """Check if word is an abstract named entity: ORG: organization, LANGUAGE: language, LAW: law or contract, NORP: nationality, religious or political group."""
        return self.is_noun and self.token.ent_type_ in ["ORG", "LANGUAGE", "LAW", "NORP"]

    @property
    def is_in_abstract_nouns_list(self) -> bool:
        """Check if word is listed in the RBN list of abstract nouns."""
        return self.is_noun and self.token.text in self.abstract_nouns_list
