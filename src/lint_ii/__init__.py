"""
lint_ii
-------

LiNT-II is a readability assessment tool for Dutch. The library (a) calculates a readability score for a text using the LiNT-II formula, and (b) provides an analysis per sentence, based on the 4 features that are used in the formula.

The four linguistic features of LiNT-II are:
- word frequency
- proportion of concrete nouns
- syntactic dependency length
- number of content words per clause

For more information about the features and the scientific research behind LiNT-II, please refer to <ADD LINK TO DOCUMENTATION>.

# Example of use

## Create ReadabilityAnalysis object from text

```python
>>> from lint_ii import ReadabilityAnalysis
>>> text = "De Oudegracht is het sfeervolle hart van de stad. In de middeleeuwen was het hier een drukte van belang met de aan- en afvoer van goederen. Nu is het een prachtige plek om te winkelen en te lunchen of te dineren in de oude stadskastelen."
>>> ra = ReadabilityAnalysis.from_text(text)
Loading Dutch language model from spaCy... ✓ nl_core_news_lg
```

## Get LiNT-II scores

```python
>>> ra.document_lint_score
48.924787870674514
>>> ra.lint_scores_per_sentence
[31.068428969266677, 48.322685595433335, 69.87164005804999]
```

## Get detailed analysis

```python
>>> detailed_analysis = ra.get_detailed_analysis()
>>> detailed_analysis.keys()
dict_keys(['document_stats', 'sentence_stats'])
>>> detailed_analysis['document_stats']
{'sentence_count': 3,
 'document_lint_score': 48.924787870674514,
 'document_difficulty_level': 3,
 'min_lint_score': 31.068428969266677,
 'max_lint_score': 69.87164005804999,
 'word_freq_compound_adjustment': True}
>>> detailed_analysis['sentence_stats'][0]
{'text': 'De Oudegracht is het sfeervolle hart van de stad.',
 'score': 31.068428969266677,
 'level': 1,
 'top_n_least_freq_words': [('sfeervolle', 3.21),
  ('hart', 5.2),
  ('stad', 5.68)],
 'mean_log_word_frequency': 4.696666666666666,
 'concrete_nouns': ['stad'],
 'abstract_nouns': [],
 'undefined_nouns': ['hart'],
 'unknown_nouns': ['oudegracht'],
 'max_sdl': 3,
 'sdls': [{'token': 'de', 'dep_length': 0, 'head': 'Oudegracht'},
  {'token': 'oudegracht', 'dep_length': 3, 'head': 'hart'},
  {'token': 'is', 'dep_length': 2, 'head': 'hart'},
  {'token': 'het', 'dep_length': 1, 'head': 'hart'},
  {'token': 'sfeervolle', 'dep_length': 0, 'head': 'hart'},
  {'token': 'hart', 'dep_length': 0, 'head': 'hart'},
  {'token': 'van', 'dep_length': 1, 'head': 'stad'},
  {'token': 'de', 'dep_length': 0, 'head': 'stad'},
  {'token': 'stad', 'dep_length': 2, 'head': 'hart'},
  {'token': '.', 'dep_length': 0, 'head': 'hart'}],
 'content_words_per_clause': 4.0,
 'content_words': ['oudegracht', 'sfeervolle', 'hart', 'stad'],
 'finite_verbs': ['is']}
```
"""

from lint_ii.core.readability_analysis import ReadabilityAnalysis
from lint_ii.core.sentence_analysis import SentenceAnalysis
from lint_ii.core.word_features import WordFeatures


class LiNT_II_Exception(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
