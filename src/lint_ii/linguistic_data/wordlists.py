from pathlib import Path

import pyarrow.parquet as pq


LINGUISTIC_DATA_PATH = Path(__file__).parent.resolve()


path_nouns_sem_types = next(LINGUISTIC_DATA_PATH.glob('nouns_sem_types_*.parquet'))
nouns_sem_types = pq.read_table(LINGUISTIC_DATA_PATH / path_nouns_sem_types)

noun_to_super_sem_type = {
    row['word']:row['super_sem_type']
    for row in nouns_sem_types.to_pylist()
}
