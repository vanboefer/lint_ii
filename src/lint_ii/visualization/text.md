
# **LiNT-II**: readability assessment for Dutch

## Table of contents
1. [Introduction](#introduction)
2. [Demo](#demo)
3. [LiNT and LiNT-II](#lint-and-lint-ii)
4. [Linguistic Features](#linguistic-features)
5. [Scores and Diffculty Levels](#scores-and-diffculty-levels)

## Introduction

- **LiNT-II** analyzes Dutch text readability using four linguistic features: word frequency, syntactic dependency length, information density (number content words per clause), and proportion of concrete vs abstract nouns. [*Read more*](#linguistic-features)
- **LiNT-II** outputs a readability score between 0-100; the higher the score is, the more difficult the text is. The scores can be mapped to four difficulty levels: a text of Level 1 is understandable for about 85\% of adult Dutch readers, while a text of Level 4 is understandable for about 18\% of adult Dutch readers. [*Read more*](#scores-and-diffculty-levels)
- **LiNT-II** scores and levels are based on an empirical comprehension study, where understanding of different texts was assessed using a *cloze test* (fill-in missing words). The study involved 120 texts; 2700 Dutch high-school students participated. [*Read more*](#lint-and-lint-ii)
- For code and usage, please refer to the [GitHub repo](https://github.com/vanboefer/lint_ii).

## Demo

Select one of the 4 texts below to see the detailed LiNT-II analysis:

- The upper bar shows the score and difficulty level for the whole document.
- Click on ∑ (right-upper corner) to see additional document-level statistics.
- On the text itself, you can see the difficulty level per sentence; hover above it to see additional sentence-level statistics.
- Hover above each word to see the word-level linguistic features, like word frequency, semantic type, etc. To understand the features and how they are calculated, see [Linguistic Features](#linguistic-features).

**Notes for the design**:
- Upper bar: sentences, document score, document level
- Hover on sent stats: OK
- Hover on word stats: freq tier in the original LiNT:
    - erg laag < 1.5 (minder dan 32 keer voor per miljard woorden)
    - 1.5 <= laag <= 3 (tussen de 32 en 1000 keer voor per miljard woorden)

## LiNT and LiNT-II

### Background and motivation

**LiNT-II** is a new implementation of the original **LiNT** (*Leesbaar­heids­instrument voor Nederlandse Teksten*) tool. 

The original LiNT utilizes the legacy NLP pipeline [T-Scan](https://github.com/CentreForDigitalHumanities/tscan) to extract linguistic features from text; this software is difficult to install and to run and is therefore not suitable for many use cases.

LiNT-II is a modern Python package, with [spaCy](https://spacy.io/) under the hood. It can be easily installed with [`pip`](https://pypi.org/project/pip/), and integrated into other software; it is fast and therefore suitable for production setups.

In order to preserve the scientific integrity, we worked in close collaboration with Henk Pander Maat, one of the researchers who developed the original LiNT.

### Original LiNT

The first version of LiNT was developed in the NWO project *Toward a validated reading level tool for Dutch* (2012-2017). Later versions were developed in the *Digital Humanities Lab* of Utrecht University.

More details about the original LiNT can be found on:

- [LiNT (Utrecht University)](https://lint.hum.uu.nl/home)
- [LiNT (Gebruiker Centraal)](https://www.gebruikercentraal.nl/hulpmiddelen/lint-leesbaarheidsinstrument-voor-nederlandse-teksten/)

The research on which LiNT is based, including the empirical comprehension study and the development of the model, is described in:

- [PhD thesis of Suzanne Kleijn (2018)](https://lint.hum.uu.nl/assets/kleijn-2018.pdf) (English)
- [Pander Maat et al. 2023](https://www.aup-online.com/content/journals/10.5117/TVT2023.3.002.MAAT) (Dutch)

### LiNT-II

In LiNT-II, the linguistic analysis of the text is done with [spaCy](https://spacy.io/), instead of the original [T-Scan](https://github.com/CentreForDigitalHumanities/tscan). This includes, for example, splitting the text into sentences and tokens, tagging the part-of-speech of each token (noun, verb, etc.), and parsing the syntactic structure of the sentence. We use the spaCy model [`nl_core_news_lg`](https://spacy.io/models/nl#nl_core_news_lg).

Doing the linguistic analysis with a different software affects the values of the [linguistic features](#linguistic-features). Therefore, we fitted a **new model** on the comprehension data that was collected for the original LiNT. The new model leads to a new [LiNT-II formula](#scores-and-diffculty-levels) for calculating the readability score, which is different from the original LiNT formula.

## Linguistic Features

The readability score of LiNT-II is calculated based on 4 features:

Feature | Description
--- | ---
**word frequency** | Mean word frequency of all the content words in the text (excluding proper nouns). <br>➡ Less frequent words make a text more difficult.
**syntactic dependency length** | Syntactic dependency length (SDL) is the number of words between a syntactic head and its dependent (e.g., verb-subject). We take the biggest SDL in each sentence, and calculate their mean value for the whole text. <br>➡ Bigger SDL's make a text more difficult.
**content words per clause** | Mean number of content words per clause. <br>➡ Larger number of content words indicates dense information and makes a text more difficult.
**proportion concrete nouns** | Mean proportion of concrete nouns out of all the nouns in the text. <br>➡ Smaller proportion of concrete nouns (i.e. many abstract nouns) makes a text more difficult.

#### Definitions

- ***Content words*** are words that possess semantic content and contribute to the meaning of the sentence. In this library content words are defined based on their [part-of-speech (POS)](https://universaldependencies.org/u/pos/): nouns (NOUN), proper nouns (PROPN), lexical verb (VERB), adjective (ADJ), adverb (ADV).
- ***Clause***: A clause is a group of words that contains a subject and a verb, functioning as a part of a sentence. In this library, the number of clauses is determined by the number of finite verbs (= verbs that show tense) in the sentence.

## Scores and Diffculty Levels