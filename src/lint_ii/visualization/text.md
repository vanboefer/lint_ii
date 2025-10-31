
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
- Hover on word stats: freq < 3 is considered low

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

### Word Frequency

#### Why word frequencies?

Words that are not common in spoken language tend to be less familiar to people and therefore more difficult to process and understand. We can estimate how familiar a certain word is by measuring its frequency, i.e. counting its occurences in a big text corpus (dataset).

#### Choice of corpus

LiNT-II calculates word frequencies from [SUBTLEX-NL (Keuleers et al. 2010)](https://link.springer.com/article/10.3758/brm.42.3.643): a corpus of Dutch subtitles, which contains about 40 million words. This corpus was chosen for the original LiNT after elaborate analysis and consideration; for details, please refer to [T-Scan manual](https://raw.githubusercontent.com/CentreForDigitalHumanities/tscan/master/docs/tscanhandleiding.pdf) and [Pander Maat \& Dekker 2016](https://lint.hum.uu.nl/assets/pander-maat-en-dekker-2016.pdf).

For LiNT-II, we also experimented with using frequencies from [wordfreq](https://github.com/rspeer/wordfreq) instead of SUBTLEX-NL. The [wordfreq](https://github.com/rspeer/wordfreq) corpus is a lot bigger and contains multiple genres: SUBTLEX-NL, OpenSubtitles, Wikipedia, NewsCrawl, GlobalVoices, Web text (OSCAR), Twitter. However, [wordfreq](https://github.com/rspeer/wordfreq) frequencies gave worse results when [fitting the model]() on comprehension data. This suggests that SUBTLEX-NL might be a better approximation of spoken language than a bigger corpus that contains a lot of written language like news and Wikipedia.

It is important to note that any corpus captures language use only partially. Since the SUBTLEX-NL corpus is based on Dutch subtitles for English-speaking shows, some words that are common in a Dutch-speaking context might be a lot less frequent there (e.g., *fietser* "cyclist"). In addition, the shows are from the years 2000-2010; new words from the last 15 years (*Instagram*, *covid*) are not in the corpus. Additional corrections were applied to address some of these issues, as described [below](#corrections-and-exceptions).

#### What do the values mean?

We calculate the frequencies on a Zipf scale ([Van Heuven et al. 2014](https://journals.sagepub.com/doi/full/10.1080/17470218.2013.850521)):

```
Zipf value = log₁₀(frequency per billion words)
```

A Zipf value of 1 means that a word appears once per 100 million words, a Zipf value of 2 means that a word appears once per 10 million words, a Zipf value of 3 means that a word appears once per million words, and so on. 

In line with the original LiNT and [Van Heuven et al. 2014](https://journals.sagepub.com/doi/full/10.1080/17470218.2013.850521), we consider words with a Zipf value **smaller than 3 as "uncommon"**; these words appear in the SUBTLEX-NL corpus less than 1000 times per billion words (less than once per million words). Examples: *afdwaling*: 1.66, *napraterij*: 1.66.

#### Corrections and exceptions

- We calculate word frequencies only for [content words](#definitions), since function words are generally frequent (for example, *dat*: 7.34, *de*: 7.38, *en*: 7.14) and do not contribute to the diffuculty of the text. From the content words, we exclude proper nouns (names of people, places, etc.) since their frequency does not influence the difficulty of the text.
- For transparent compounds (e.g., *duwboot* "towboat"), we use the frequency of the base word (*boot* "boat"), rather than the frequency of the compound as a whole. Previous research shows that this provides a better estimate of word difficulty; for more details, see [Pander Maat \& Dekker 2016](https://lint.hum.uu.nl/assets/pander-maat-en-dekker-2016.pdf).
- As mentioned above, some words that are missing or infrequent in the SUBTLEX-NL corpus are actually pretty common in the spoken language. This includes new words that entered the Dutch language after 2010 (*appen* "to send a message on WhatsApp"), and words that are common in a Dutch-speaking context but might be not common in English-speaking TV shows (*knutselen* "to craft", *fietser* "cyclist"). To address the most obvious discrepancies of this sort in the corpus, the makers of the original LiNT manually created a list of words that should be skipped when calculating frequencies. So instead of incorrectly getting a low frequency, these words don't get any frequency value at all, and so do not mistakenly affect the difficulty score. For more details on how this was done, see the [T-Scan manual](https://raw.githubusercontent.com/CentreForDigitalHumanities/tscan/master/docs/tscanhandleiding.pdf).

### Syntactic Dependency Length (SDL)

### Content Words per Clause

### Proportion of Concrete Nouns

## Scores and Diffculty Levels