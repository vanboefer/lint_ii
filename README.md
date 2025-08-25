# **LiNT-II**: readability assessment for Dutch

[![License: EUPL v1.2](https://img.shields.io/badge/License-EUPL%20v1.2-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## Table of contents
1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [What is LiNT-II?](#what-is-lint-ii)
4. [References and Credits](#references-and-credits)

## Introduction

**LiNT-II** is a readability assessment tool for Dutch. The library (a) calculates a readability score for a text using the LiNT-formula, and (b) provides an analysis per sentence, based on the 4 features that are used in the formula.

**LiNT-II** is a new implementation of the original **LiNT** tool (see [here](#original-lint)). There are three differences between **LiNT** and **LiNT-II**:

- The **NLP tools** used to extract linguistic features from the text. LiNT has [T-Scan](https://github.com/CentreForDigitalHumanities/tscan) under the hood, while LiNT-II uses the [spaCy](https://spacy.io/) and [wordfreq](https://github.com/rspeer/wordfreq) libraries.
- The **post-processing** done to refine the features. LiNT implements various manual corrections on top of the automated analysis (for example in how concrete and abstract nouns are defined; see the [T-Scan manual](https://raw.githubusercontent.com/CentreForDigitalHumanities/tscan/master/docs/tscanhandleiding.pdf)). LiNT-II does not apply any post-processing on the automatically extracted features.
- The **weights** of the features in the formula. *TBD*

## Quick Start

### Installation

#### Requirements

The requirements are listed in the [environment.yml](environment.yml) file. It is recommended to create a virtual environment with conda (you need to have [`miniconda`](https://www.anaconda.com/docs/getting-started/miniconda/main) installed):

```bash
conda env create -f environment.yml
conda activate lint
```
#### Dutch language model

After creating and activating the environment, you need to download the Dutch language model from spaCy:

```bash
python -m spacy download nl_core_news_sm
```

#### Abstract nouns list

You need to download and process the list of abstract nouns used in LiNT-II. Due to licensing restrictions, we cannot publish it in the repo. See instructions in the [abstract_nouns](abstract_nouns/README.md) folder.

### Usage in Python

```python
from pathlib import Path
import spacy
from lint_ii import ReadabilityAnalysis

abstract_nouns = Path('abstract_nouns.txt').read_text().split('\n')
nlp_model = spacy.load("nl_core_news_sm")

text = "De Oudegracht is het sfeervolle hart van de stad. In de middeleeuwen was het hier een drukte van belang met de aan- en afvoer van goederen. Nu is het een prachtige plek om te winkelen en te lunchen of te dineren in de oude stadskastelen."

doc = ReadabilityAnalysis.from_text(
    text,
    nlp_model,
    abstract_nouns,
)
```

#### Get LiNT scores

If you only want the scores per sentence, use the `lint_scores` property:

```python
doc.lint_scores
```

You will get a list of scores per sentence:

```python
[34.28665000000001, 49.89385833333334, 61.28863750000001]
```

#### Get detailed analysis

For a detailed analysis, use the `get_detailed_analysis()` method:

```python
doc.get_detailed_analysis()
```

You will get the mean LiNT score for the text, as well as scores and feature analysis per sentence:

```python
{'document_stats': {'sentence_count': 3,
  'mean_lint_score': 48.48971527777778,
  'min_lint_score': 34.28665000000001,
  'max_lint_score': 61.28863750000001},
  'sentence_scores': [
   {'text': 'De Oudegracht is het sfeervolle hart van de stad.',
   'score': 34.28665000000001,
   'level': 2,
   'top_n_least_freq_words': [
    ('sfeervolle', 3.21),
    ('hart', 5.2),
    ('stad', 5.68)
    ],
   'concrete_nouns': ['Oudegracht', 'stad'],
   'max_sdl': 4,
   'sdls': {...},
   'content_words': ['Oudegracht', 'sfeervolle', 'hart', 'stad']},
   {...}]
}
```

## What is LiNT-II?

**LiNT-II** is a Python implementation of **LiNT** (Leesbaar­heids­instrument voor Nederlandse Teksten), a readability assessment tool that analyzes Dutch texts and estimates their difficulty.

LiNT-II outputs a readability score per sentence based on 4 features:

Feature | Description
--- | ---
**word frequency** | Mean word frequency of all content words in the text (excluding proper nouns). Less frequent words make a text more difficult.
**proportion concrete nouns** | Proportion of concrete nouns out of all the nouns in the text. Concrete nouns are less difficult than abstract nouns.
**syntactic dependency length** | The biggest syntactic dependency length (SDL) in each sentence, averaged over all sentences in the text. SDL is calculated as the number of words between a syntactic head and its dependent (e.g., verb-subject). Bigger SDL makes a sentence more difficult.
**content words per clause** | Number of content words (excluding adverbs) per clause. Larger number of content words indicates dense information and makes a text more difficult.

#### Definitions

- ***Content words*** are words that possess semantic content and contribute to the meaning of the sentence. In this library content words are defined based on their [part-of-speech (POS)](https://universaldependencies.org/u/pos/): nouns (NOUN), proper nouns (PROPN), lexical verb (VERB), adjective (ADJ), adverb (ADV).
- ***Abstract nouns***: In this library, a noun is considered abstract if it either (a) belongs to one of the following types of named entities: ORG (organization), LANGUAGE (language), LAW (law or contract), NORP (nationality, religious or political group), or (b) is listed in the RBN list of abstract nouns (see [here](/abstract_nouns/README.md)).
- ***Clause***: A clause is a group of words that contains a subject and a verb, functioning as a part of a sentence. In this library, the number of clauses is determined by the number of finite verbs (= verbs that show tense) in the sentence.

### LiNT score

*TBD: updated weights*

The readability score is calculated based on the following formula:

```
LiNT score =

    3.204	+ 15.845 * word frequency
            + 13.096 * proportion concrete nouns
            - 1.331  * syntactic dependency length
            - 3.829  * content words per clause
```

The formula was created based on comprehension studies, in which the 4 features were identified (the features that were the most relevant for comprehension) and their weights were determined (based on a regression analysis). The correlation between the calculated score and the real comprehension score is 0.87. For more information about the research behind LiNT and LiNT-II, please refer to the sources listed in [References and Credits](#references-and-credits).

### Understanding the score

*TBD: updated analysis*

Score | Difficulty level | Proportion of adults who have diffuculty understanding this level
--- | --- | ---
0-34 | 1 | 15%
35-46 | 2 | 31%
47-60 | 3 | 55%
60-100 | 4 | 82%

For more information about how this estimation was done, please refer to the sources listed in [References and Credits](#references-and-credits).

## References and Credits

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

### LiNT-II

LiNT-II was developed by [Jenia Kim](https://www.linkedin.com/in/jeniakim/) (Hogeschool Utrecht), in collaboration with Henk Pander Maat (Utrecht University) and Antal van den Bosch (Utrecht University).

*Reference: TBD*

LiNT-II was inspired by and based on a spaCy implementation of LiNT by the City of Amsterdam: [alletaal-lint](https://github.com/Amsterdam/alletaal-lint).
