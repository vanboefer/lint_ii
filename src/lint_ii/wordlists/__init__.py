from pathlib import Path
from enum import StrEnum

import pyarrow.parquet as pq


WORDLISTS_PATH = Path(__file__).parent.resolve()


path_nouns_sem_types = next(WORDLISTS_PATH.glob('nouns_sem_types_*.parquet'))
nouns_sem_types = pq.read_table(WORDLISTS_PATH / path_nouns_sem_types)

noun_to_super_sem_type = {
    row['word']:row['super_sem_type']
    for row in nouns_sem_types.to_pylist()
}


class SuperSemTypes(StrEnum):
    CONCRETE = 'concrete'
    ABSTRACT = 'abstract'
    UNDEFINED = 'undefined'
    UNKNOWN = 'unknown'
