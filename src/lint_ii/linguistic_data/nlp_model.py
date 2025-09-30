import spacy
from spacy.language import Language

from lint_ii import LiNT_II_Exception


try:
    print('loading Dutch language model from spacy...')
    NLP_MODEL : Language = spacy.load('nl_core_news_sm')
except OSError:
    raise LiNT_II_Exception('LiNT-II requires the spacy model "nl_core_news_sm";download the model by running: `python -m spacy download nl_core_news_sm`')
