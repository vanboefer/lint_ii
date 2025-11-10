# **LiNT-II**: readability assessment for Dutch

[![License: EUPL v1.2](https://img.shields.io/badge/License-EUPL%20v1.2-blue.svg)](LICENSE)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

## Table of contents
1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [What is LiNT-II?](#what-is-lint-ii)
4. [References and Credits](#references-and-credits)

## Introduction

**LiNT-II** is a readability assessment tool for Dutch. The library (a) calculates a readability score for a text using the LiNT-II formula, and (b) provides an analysis per sentence, based on the 4 features that are used in the formula.

**LiNT-II** is a new implementation of the original **LiNT** tool (see [here](#original-lint)). There are two differences between **LiNT** and **LiNT-II**:

- The **NLP tools** used to extract linguistic features from the text. LiNT has [T-Scan](https://github.com/CentreForDigitalHumanities/tscan) under the hood, while LiNT-II uses [spaCy](https://spacy.io/).
- The **coefficients** (weights) used in the formula. Since the features are calculated differently, the coefficients are also different.

For more information, please refer to ['What is LiNT-II?'](#what-is-lint-ii) and [LiNT-II documentation]().

## Quick Start

### Installation

```bash
pip install lint_ii
python -m spacy download nl_core_news_lg
```
### Usage in Python

#### Create `ReadabilityAnalysis` object from text

```python
>>> from lint_ii import ReadabilityAnalysis

>>> text = "De Oudegracht is het sfeervolle hart van de stad. In de middeleeuwen was het hier een drukte van belang met de aan- en afvoer van goederen. Nu is het een prachtige plek om te winkelen en te lunchen of te dineren in de oude stadskastelen."

>>> ra = ReadabilityAnalysis.from_text(text)
Loading Dutch language model from spaCy... ✓ nl_core_news_lg
```

**NOTE**: LiNT-II can process plain text or markdown. Other formats (e.g.. html) or very "unclean" text might produce inaccurate results due to segmentation issues.

#### Get LiNT-II scores

You can see the score for the whole document and/or per sentence:

```python
>>> ra.document_lint_score
48.924787870674514

>>> ra.lint_scores_per_sentence
[31.068428969266677, 48.322685595433335, 69.87164005804999]
```

#### Get detailed analysis

For a detailed analysis, use the `get_detailed_analysis()` method:

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

#### Visualization in Jupyter Notebook

[...TBA...]

## What is LiNT-II?

**LiNT-II** is a Python implementation of **LiNT** (*Leesbaar­heids­instrument voor Nederlandse Teksten*), a readability assessment tool that analyzes Dutch texts and estimates their difficulty.

LiNT-II outputs a readability score based on 4 features:

Feature | Description
--- | ---
**word frequency** | Mean word frequency of all the content words in the text (excluding proper nouns). <br>➡ Less frequent words make a text more difficult.
**syntactic dependency length** | Syntactic dependency length (SDL) is the number of words between a syntactic head and its dependent (e.g., verb-subject). We take the biggest SDL in each sentence, and calculate their mean value for the whole text. <br>➡ Bigger SDL's make a text more difficult.
**content words per clause** | Mean number of content words per clause. <br>➡ Larger number of content words indicates dense information and makes a text more difficult.
**proportion concrete nouns** | Mean proportion of concrete nouns out of all the nouns in the text. <br>➡ Smaller proportion of concrete nouns (i.e. many abstract nouns) makes a text more difficult.

#### Definitions

- ***Content words*** are words that possess semantic content and contribute to the meaning of the sentence. In this library content words are defined based on their [part-of-speech (POS)](https://universaldependencies.org/u/pos/): nouns (NOUN), proper nouns (PROPN), lexical verb (VERB), adjective (ADJ), adverb (ADV).
- ***Clause***: A clause is a group of words that contains a subject and a verb, functioning as a part of a sentence. In this library, the number of clauses is determined by the number of finite verbs (= verbs that show tense) in the sentence.

### LiNT-II score

The readability score is calculated based on the following formula:

```
LiNT-II score = 

  100 - (
      - 5.16
      + (16.13 * word frequency)
      - (1.28  * syntactic dependency length)
      - (3.52  * content words per clause)
      + (16.26 * proportion concrete nouns)
  )
```

The formula's coefficients were estimated using a linear regression model fitted on empirical reading comprehension data from highschool students.

For more information about the empirical study (done for the original LiNT), please refer to the sources listed in [Original LiNT](#original-lint).

For more information about the LiNT-II model, please refer to the [LiNT-II documentation]().

### Difficulty levels

LiNT-II scores are mapped to 4 difficulty levels. For each level, it is estimated how many adult Dutch readers have difficulty understanding texts on this level.

Score | Difficulty level | Proportion of adults who have diffuculty understanding this level
--- | --- | ---
0-34 | 1 | 15%
35-46 | 2 | 31%
47-60 | 3 | 55%
60-100 | 4 | 82%

For more information about how this estimation was done for the original LiNT, please refer to the sources listed in [Original LiNT](#original-lint).

For more information about how the estimation was adapted for LiNT-II, please refer to the [LiNT-II documentation]().

## References and Credits

### LiNT-II

LiNT-II was developed by [Jenia Kim](https://www.linkedin.com/in/jeniakim/) (Hogeschool Utrecht, VU Amsterdam), in collaboration with [Henk Pander Maat](https://www.uu.nl/medewerkers/HLWPanderMaat) (Utrecht University).

If you use this library, please cite as follows:

```
@software{lint_ii,
  author = {Kim, Jenia and Pander Maat, Henk},
  title = {{LiNT-II: readability assessment for Dutch}},
  year = {2025},
  url = {https://github.com/vanboefer/lint_ii},
  version = {1.0.0},
  note = {Python package}
}
```

- Special thanks to [Antal van den Bosch](https://www.uu.nl/staff/APJvandenBosch) (Utrecht University) for setting up and facilitating the collaboration.
- Special thanks to [Lawrence Vriend](https://github.com/lcvriend) for his work on the **LiNT-II Visualizer** and other help with the code.
- The code for LiNT-II was inspired by a spaCy implementation of LiNT by the City of Amsterdam: [alletaal-lint](https://github.com/Amsterdam/alletaal-lint).

### Original LiNT

The first version of LiNT was developed in the NWO project *Toward a validated reading level tool for Dutch* (2012-2017). Later versions were developed in the *Digital Humanities Lab* of Utrecht University.

More details about the original LiNT can be found on:

- [LiNT (Utrecht University)](https://lint.hum.uu.nl/home)
- [LiNT (Gebruiker Centraal)](https://www.gebruikercentraal.nl/hulpmiddelen/lint-leesbaarheidsinstrument-voor-nederlandse-teksten/)

The readability research on which LiNT is based is described in the [PhD thesis of Suzanne Kleijn](https://lint.hum.uu.nl/assets/kleijn-2018.pdf) (English) and in [Pander Maat et al. 2023](https://www.aup-online.com/content/journals/10.5117/TVT2023.3.002.MAAT) (Dutch). Please cite as follows:

```
@article{pander2023lint,
  title={{LiNT}: een leesbaarheidsformule en een leesbaarheidsinstrument},
  author={Pander Maat, Henk and Kleijn, Suzanne and Frissen, Servaas},
  journal={Tijdschrift voor Taalbeheersing},
  volume={45},
  number={1},
  pages={2--39},
  year={2023},
  publisher={Amsterdam University Press Amsterdam}
}
```

```
@phdthesis{kleijn2018clozing,
  title={Clozing in on readability: How linguistic features affect and predict text comprehension and on-line processing},
  author={Kleijn, Suzanne},
  year={2018},
  school={Utrecht University}
}
```
