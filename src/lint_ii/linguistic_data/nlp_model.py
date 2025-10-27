import spacy
from spacy.language import Language

from lint_ii import LiNT_II_Exception


try:
    print('Loading Dutch language model from spaCy... ', end='')
    NLP_MODEL : Language = spacy.load('nl_core_news_lg')
    print('✓ nl_core_news_lg')
except OSError:
    raise LiNT_II_Exception('LiNT-II requires the spaCy model "nl_core_news_lg"; download the model by running: `python -m spacy download nl_core_news_lg`')
