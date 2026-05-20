from enum import StrEnum
from pathlib import Path

LINGUISTIC_DATA_PATH = Path(__file__).parent.resolve() / 'data'
WORD_FREQ_COMPOUND_ADJUSTMENT = True

class SuperSemTypes(StrEnum):
    CONCRETE = 'concrete'
    ABSTRACT = 'abstract'
    UNDEFINED = 'undefined'
    UNKNOWN = 'unknown'