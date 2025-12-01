"""
lint_ii
-------

LiNT-II is a readability assessment tool for Dutch. The library (a) calculates a readability score for a text using the LiNT-II formula, and (b) provides an analysis per sentence, based on the 4 features that are used in the formula.

The four linguistic features of LiNT-II are:
- word frequency
- proportion of concrete nouns
- syntactic dependency length
- number of content words per clause

For more information about the features and the scientific research behind LiNT-II, please refer to https://github.com/vanboefer/lint_ii.

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
>>> ra.lint.score
48.20593518603563
>>> ra.lint.level
3
>>> ra.lint_scores_per_sentence
[18.511612982419507, 54.27056340066443, 63.24402181810589]
```

## Get detailed analysis

```python
>>> detailed_analysis = ra.get_detailed_analysis()
>>> detailed_analysis.keys()
dict_keys(['document_stats', 'sentence_stats'])
>>> detailed_analysis['document_stats']
{'sentence_count': 3,
 'document_lint_score': 48.20593518603563,
 'document_difficulty_level': 3,
 'min_lint_score': 18.511612982419507,
 'max_lint_score': 63.24402181810589}
>>> detailed_analysis['sentence_stats'][0]
{'text': 'De Oudegracht is het sfeervolle hart van de stad.',
 'score': 18.511612982419507,
 'level': 1,
 'mean_log_word_frequency': 5.364349123825101,
 'top_n_least_freq_words': [('hart', 5.293120582960477),
  ('stad', 5.435577664689725)],
 'proportion_concrete_nouns': 0.5,
 'concrete_nouns': ['stad'],
 'abstract_nouns': [],
 'undefined_nouns': ['hart'],
 'unknown_nouns': ['oudegracht'],
 'max_sdl': 3,
 'sdls': [{'token': 'de', 'dep_length': 0, 'heads': ['Oudegracht']},
  {'token': 'oudegracht', 'dep_length': 3, 'heads': ['hart']},
  {'token': 'is', 'dep_length': 2, 'heads': ['hart']},
  {'token': 'het', 'dep_length': 1, 'heads': ['hart']},
  {'token': 'sfeervolle', 'dep_length': 0, 'heads': ['hart']},
  {'token': 'hart', 'dep_length': 0, 'heads': ['hart']},
  {'token': 'van', 'dep_length': 1, 'heads': ['stad']},
  {'token': 'de', 'dep_length': 0, 'heads': ['stad']},
  {'token': 'stad', 'dep_length': 2, 'heads': ['hart']},
  {'token': '.', 'dep_length': 0, 'heads': ['hart']}],
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
