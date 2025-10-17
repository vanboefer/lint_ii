from pathlib import Path

import pyarrow.parquet as pq


LINGUISTIC_DATA_PATH = Path(__file__).parent.resolve() / 'data'

path_nouns_sem_types = next(LINGUISTIC_DATA_PATH.glob('nouns_sem_types_*.parquet'))
path_manner_adverbs = next(LINGUISTIC_DATA_PATH.glob('manner_adverbs_*.parquet'))

cols = ['word', 'super_sem_type', 'head']
NOUN_DATA = {
    row['word']:{k:v for k,v in row.items() if k != 'word' and v is not None}
    for row in pq.read_table(path_nouns_sem_types, columns=cols).to_pylist()
}

MANNER_ADVERBS = pq.read_table(path_manner_adverbs).to_pydict().get('adverb')
