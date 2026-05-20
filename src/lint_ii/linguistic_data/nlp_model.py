import json
import warnings
from pathlib import Path

import spacy
from spacy.language import Language

from lint_ii import LiNT_II_Exception
from lint_ii.linguistic_data import LINGUISTIC_DATA_PATH
from lint_ii.linguistic_data.wordlists import PATH_NOUNS_SEM_TYPES

noun_list_version = PATH_NOUNS_SEM_TYPES.stem

try:
    print('Loading Dutch language model from spaCy... ', end='')
    NLP_MODEL : Language = spacy.load('nl_core_news_lg')
    model_version = NLP_MODEL.meta['version']
    print('✓ nl_core_news_lg')
except OSError:
    raise LiNT_II_Exception('LiNT-II requires the spaCy model "nl_core_news_lg"; download the model by running: `python -m spacy download nl_core_news_lg`')


coef_path = LINGUISTIC_DATA_PATH / 'coefficients.json'
all_available_models = json.loads(coef_path.read_text(encoding='utf8'))

for model in all_available_models:
    if (
        model['model_version'] == model_version
        and model['noun_list'] == noun_list_version
    ):
        COEFFICIENTS = {key:vals['coef'] for key, vals in model['coefficients'].items()}
        break
else:
    raise LiNT_II_Exception(f'No coefficients available for spaCy model version {model_version} and noun list version {noun_list_version}.\nFor more details see: https://github.com/vanboefer/lint_ii/tree/main/regression_data_and_results')


if model_version != '3.7.0':
    warnings.warn(
        f"Loaded model version {model_version}. "
        "LiNT-II is most accurate with spaCy 3.7.\n"
        "For more details see: https://github.com/vanboefer/lint_ii/tree/main/regression_data_and_results"
    )