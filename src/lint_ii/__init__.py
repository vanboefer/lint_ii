"""
lint_ii
-------

LiNT-II is a readability assessment tool for Dutch. The library (a) calculates a readability score for a text using the LiNT-formula, and (b) provides an analysis per sentence, based on the 4 features that are used in the formula.

The four linguistic features of LiNT-II are:
- word frequency
- proportion of concrete nouns
- syntactic dependency length
- number of content words per clause

For more information about the features and the scientific research behind LiNT-II, please refer to the `README.md`.

## Example of use

```python
from pathlib import Path
import spacy
from lint_ii import ReadabilityAnalysis

abstract_nouns = Path('abstract_nouns.txt').read_text().split('\n')
nlp_model = spacy.load("nl_core_news_sm")

doc = ReadabilityAnalysis.from_text(
    "De Oudegracht is het sfeervolle hart van de stad. In de middeleeuwen was het hier een drukte van belang met de aan- en afvoer van goederen. Nu is het een prachtige plek om te winkelen en te lunchen of te dineren in de oude stadskastelen.",
    nlp_model,
    abstract_nouns,
)

doc.get_detailed_analysis()
```
>>> {'document_stats': {'sentence_count': 3,
  'mean_lint_score': 48.48971527777778,
  'min_lint_score': 34.28665000000001,
  'max_lint_score': 61.28863750000001},
  'sentence_scores': [
   {'text': 'De Oudegracht is het sfeervolle hart van de stad.',
   'score': 34.28665000000001,
   'level': 2,
   'top_n_least_freq_words': [('sfeervolle', 3.21),
    ('hart', 5.2),
    ('stad', 5.68)],
   'concrete_nouns': ['Oudegracht', 'stad'],
   'max_sdl': 4,
   'sdls': {...},
   'content_words': ['Oudegracht', 'sfeervolle', 'hart', 'stad']},
   {...}]
}
"""

from lint_ii.core.readability_analysis import ReadabilityAnalysis
