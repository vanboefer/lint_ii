
# **LiNT-II**: readability assessment for Dutch

## Table of contents
1. [Introduction](#introduction)
2. [Demo](#demo)
3. [LiNT and LiNT-II](#lint-and-lint-ii)
4. [Linguistic Features](#linguistic-features)
5. [Scores and Diffculty Levels](#scores-and-diffculty-levels)
6. [References and Credits](#references-and-credits)

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

- ***Content words*** are words that possess semantic content and contribute to the meaning of the sentence. In this library content words are defined based on their [part-of-speech (POS)](https://universaldependencies.org/u/pos/): nouns (NOUN), proper nouns (PROPN), lexical verbs (VERB), adjectives (ADJ), adverbs (ADV).
- ***Clause***: A clause is a group of words that contains a subject and a verb, functioning as a part of a sentence. In this library, the number of clauses is determined by the number of finite verbs (= verbs that show tense) in the sentence.

### Word Frequency

#### Why word frequencies?

Words that are not common in spoken language tend to be less familiar to people and therefore more difficult to process and understand. We can estimate how familiar a certain word is by measuring its frequency, i.e. counting its occurences in a big text corpus (dataset).

#### Choice of corpus

LiNT-II calculates word frequencies from [SUBTLEX-NL (Keuleers et al. 2010)](https://link.springer.com/article/10.3758/brm.42.3.643): a corpus of Dutch subtitles, which contains about 40 million words. This corpus was chosen for the original LiNT after elaborate analysis and consideration; for details, please refer to the [T-Scan manual](https://raw.githubusercontent.com/CentreForDigitalHumanities/tscan/master/docs/tscanhandleiding.pdf) and [Pander Maat \& Dekker 2016](https://lint.hum.uu.nl/assets/pander-maat-en-dekker-2016.pdf).

For LiNT-II, we also experimented with using frequencies from [wordfreq](https://github.com/rspeer/wordfreq) instead of SUBTLEX-NL. The [wordfreq](https://github.com/rspeer/wordfreq) corpus is a lot bigger and contains multiple genres: SUBTLEX-NL, OpenSubtitles, Wikipedia, NewsCrawl, GlobalVoices, Web text (OSCAR), Twitter. However, [wordfreq](https://github.com/rspeer/wordfreq) frequencies gave lower results when [fitting the model]() on comprehension data. This suggests that SUBTLEX-NL might be a better approximation of spoken language than a bigger corpus that contains a lot of written language like news and Wikipedia.

It is important to note that any corpus captures language use only partially. Since the SUBTLEX-NL corpus is based on Dutch subtitles for English-speaking shows, some words that are common in a Dutch-speaking context might be a lot less frequent there (e.g., *fietser* "cyclist"). In addition, the shows are from the years 2000-2010; new words from the last 15 years (*Instagram*, *covid*) are not in the corpus. Additional corrections were applied to address some of these issues, as described [below](#corrections-and-exceptions).

#### What do the values mean?

We calculate the frequencies on a Zipf scale ([Van Heuven et al. 2014](https://journals.sagepub.com/doi/full/10.1080/17470218.2013.850521)):

```
Zipf value = log₁₀(frequency per billion words)
```

A Zipf value of 1 means that a word appears once per 100 million words, a Zipf value of 2 means that a word appears once per 10 million words, a Zipf value of 3 means that a word appears once per million words, and so on. 

In line with the original LiNT and [Van Heuven et al. 2014](https://journals.sagepub.com/doi/full/10.1080/17470218.2013.850521), we consider words with a Zipf value **smaller than 3 as "uncommon"**; these words appear in the SUBTLEX-NL corpus less  than once per million words. Examples: *afdwaling*: 1.66, *napraterij*: 1.66.

The SUBTLEX-NL corpus with our calculated Zipf values can be found [here](https://github.com/vanboefer/lint_ii/blob/main/src/lint_ii/linguistic_data/data/subtlex_wordfreq.parquet).

#### Corrections and exceptions

The corrections and exceptions applied in LiNT-II are the same ones as in the original LiNT.

- We calculate word frequencies only for [content words](#definitions), since function words are generally frequent (for example, *dat*: 7.34, *de*: 7.38, *en*: 7.14) and do not contribute to the diffuculty of the text. From the content words, we exclude proper nouns (names of people, places, etc.) since their frequency does not influence the difficulty of the text.
- For transparent compounds (e.g., *duwboot* "towboat"), we use the frequency of the base word (*boot* "boat"), rather than the frequency of the compound as a whole. Previous research shows that this provides a better estimate of word difficulty; for more details, see [Pander Maat \& Dekker 2016](https://lint.hum.uu.nl/assets/pander-maat-en-dekker-2016.pdf). The compounds and their base words are identified based on a manually-annotated [list](https://github.com/vanboefer/lint_ii/blob/main/src/lint_ii/linguistic_data/data/nouns_sem_types_20251017.parquet). The list contains 123,136 compounds: 63,225 singular forms and 59,911 plural forms; for the plural forms, the base word is given in singular (for example, the base word of both *integriteitstoets* "integrity test" and *integriteitstoetsen* "integrity tests" is *toets* "test").
- As mentioned above, some words that are missing or infrequent in the SUBTLEX-NL corpus are actually pretty common in the spoken language. This includes new words that entered the Dutch language after 2010 (e.g., *appen* "to send a message on WhatsApp"), and words that are common in a Dutch-speaking context but might be not common in English-speaking TV shows (e.g., *knutselen* "to craft", *fietser* "cyclist"). To address the most obvious discrepancies of this sort in the corpus, the makers of the original LiNT manually created a list of words that should be skipped when calculating frequencies. So instead of incorrectly getting a low frequency, these words don't get any frequency value at all, and so do not mistakenly affect the difficulty score. For more details on how this was done, see the [T-Scan manual](https://raw.githubusercontent.com/CentreForDigitalHumanities/tscan/master/docs/tscanhandleiding.pdf). The list can be found [here](https://github.com/vanboefer/lint_ii/blob/main/src/lint_ii/linguistic_data/data/subtlex_wordfreq_skiplist.parquet).

### Syntactic Dependency Length (SDL)

#### Why SDL?

Syntactic dependency length (SDL) is the number of words between a syntactic head and its dependent (e.g., verb-subject). The bigger the distance between a head and its dependent is, the more difficult it is to process and understand the sentence. This phenomenon is called a [*tangconstructie*](https://nl.wikipedia.org/wiki/Tangconstructie).

#### Calculating SDLs

To calculate the SDLs in the sentence, we use the [dependency parsing](https://spacy.io/api/dependencyparser) of spaCy. The parser of the [Dutch model](https://spacy.io/models/nl#nl_core_news_lg) that we use was trained on the [Alpino UD corpus](https://github.com/UniversalDependencies/UD_Dutch-Alpino).

For each token in the sentence, we identify its head(s) and then count the number of intervening tokens between them. The head is generally taken from the spaCy parser, except for the two cases described [below](#corrections-and-exceptions-1). In each sentence, we take the longest SDL as an indicator of difficulty. For the document-level readability analysis, we take the mean of all the sentence-level max SDLs.

**Example**: In the sentence *"De Oudegracht is het sfeervolle hart van de stad."*, the longest SDL is between the subject of the sentence *Oudegracht* and the root (main predicate) of the sentence *hart*; the max SDL is 3 ( three intervening tokens *is, het, sfeervolle*).

#### Corrections and exceptions

There are three cases in which we do not follow spaCy analysis:

- Punctuation: spaCy parser considers punctuation marks as tokens and assigns a head to them. In our analysis, we override this behavior: (a) punctuation marks are not counted as intervening tokens for SDL calculation, (b) for a punctuation mark, the dependency length is always set to 0 (instead of counting the distance to the head).
- Conjunctions (1): In a conjunction relation, spaCy considers the first conjunct as the head of the second. For example, in the sentence *"Je zoekt informatie in naslagwerken via trefwoorden in de **index** of het **register**."*, where the words *index* and *register* are connected with the conjuction *of*, spaCy considers *index* as the head of *register*. We override this behavior: if a token is in a conjunction then the head of the last conjunct is taken recursively from the first, i.e. the head of both *index* and *register* is *trefwoorden* in our analysis.
- Conjunctions (2): When the main predicate of the sentence (ROOT) is in a conjunction relation, spaCy connects only the first conjunct to the subject. For example, in the sentence *"Dat geluid **klinkt** in het midden- en kleinbedrijf en moet worden **gehoord**."*, the subject *geluid* is connected to its head *klinkt* but not to *gehoord*. We override this behavior: if a token is the subject, we check whether its head (ROOT) has conjuncts. If so, we consider the conjuncts as the heads of the subject as well. In our example, this means that the subject *geluid* has two heads [*klinkt*, *gehoord*]. Since the dependency length between *geluid* and *gehoord* is bigger than the one between *geluid* and *klinkt*, we take the former into account for the SDL calculation.

These exceptions and corrections were done based on a manual analysis of a sample of 200 sentences performed by Henk Pander Maat, one of the creators of the original LiNT. He identified these 3 issues as the main systematic differences between the spaCy parser and the parser used in the original LiNT.

### Content Words per Clause

#### Why content words per clause?

A clause is a group of words that contains a subject and a verb. A simple sentence contains one clause; longer sentences may contain additional clauses, for example subordinate clauses or clauses connected with words like "and" or "because". For this metric, the number of clauses is not important; what we analyze is the number of content words in each clause.

A clause with a lot of content words is dense in information and is therefore more difficult to process and understand. For example, compare the sentence *"Ik verknalde het proefwerk."* with the sentence *"Ik verknalde het proefwerk Wiskunde gisteren bij het laatste schoolexamen."*. In both cases, the sentence contains one clause (one subject and one verb), but in the second sentence there is a lot more information, which is introduced through four extra content words (*Wiskunde, gisteren, laatste, laatste*).

#### Calculating content words per clause

We calculate the number of clauses in the sentence by counting the number of finite verbs, i.e., verbs that show tense. This is done using the spaCy fine-grained part-of-speech tag "WW|pv" (*werkwoord, persoonsvorm*).

We claculate the number of content words by counting all words that have the following [parts-of-speech (POS)](https://universaldependencies.org/u/pos/): nouns (NOUN), proper nouns (PROPN), lexical verbs (VERB), adjectives (ADJ). To these, we also add a [list of 69 manner adverbs](https://github.com/vanboefer/lint_ii/blob/main/src/lint_ii/linguistic_data/data/manner_adverbs_20251017.parquet), which we consider content words; other adverbs are not included since they are considered function words, in line with the original LiNT. For more information, see the [T-Scan manual](https://raw.githubusercontent.com/CentreForDigitalHumanities/tscan/master/docs/tscanhandleiding.pdf).

### Proportion of Concrete Nouns

#### Why concrete and abstract nouns?

Concrete nouns refer to specific, tangible items that can be perceived through the senses, like "apple" or "car". Abstract nouns, on the other hand, represent general ideas or concepts that cannot be physically touched, such as "freedom" or "happiness". Research suggests that a more concrete text is easier to understand; for example, adding examples helps understanding because examples make ideas more specific and concrete.

#### LiNT-II noun list

The [noun list](https://github.com/vanboefer/lint_ii/blob/main/src/lint_ii/linguistic_data/data/nouns_sem_types_20251017.parquet) was created for the original LiNT and further revised and updated for LiNT-II. The original annotation work was done by H. Pander Maat, N. Dekker and N. van Houten; the revisions and additions for LiNT-II were done by H. Pander Maat.

The list contains 164,458 nouns, annotated for their semantic type (e.g., "human", "place") and class ("abstract", "concrete", "undefined"); the full annotation scheme is described [below](#semantic-types-annotation). The annotations are based on an existing lexicon -- [Referentiebestand Nederlands (Martin & Maks 2005)](https://taalmaterialen.ivdnt.org/download/tstc-referentiebestand-nederlands/) -- which was expanded and revised. For more information about how the original list was created, see the [T-Scan manual](https://raw.githubusercontent.com/CentreForDigitalHumanities/tscan/master/docs/tscanhandleiding.pdf).

Descriptive statistics of the LiNT-II noun list:

- The list contains 164,458 nouns in total.
- The list contains both the **singular** and the **plural** forms of the nouns, unlike the original list, which contained singular forms only. The plural forms are needed because LiNT-II does not lemmatize the words (our experimentation with spaCy lemmatizer showed inadequate results). There are 85,762 singular forms and 78,696 plural forms in the list.
- 123,136 nouns in the list are compounds (e.g., *duwboot* "towboat"). For compounds, the base word (*boot* "boat") and the modifier (*duw* "tow") are annotated. This information is used in the word frequency feature, as described [above](#corrections-and-exceptions). For plural form compounds (N=59,911), the base word is given in singular (for example, the base word of both *integriteitstoets* "integrity test" and *integriteitstoetsen* "integrity tests" is *toets* "test").
- The distribution of semantic classes in the list is as follows:
    - concrete: 84,006
    - abstract: 77,939
    - undefined: 2,513

#### Semantic types scheme

The nouns in the list are divided into 14 semantic types (see the table below), which are in turn classified into two classes: **abstract** and **concrete**. Ambiguous words that have both an abstract and a concrete meaning are classified as **undefined**.

Semantic type | Semantic class | Examples
--- | --- | ---
human | concrete | *economiedocenten*, *assistent*
nonhuman | concrete | *sardine*, *eik*
artefact | concrete | *stoel*, *barometers*
concrete substance | concrete | *modder*, *lichaamsvloeistoffen*
food and care | concrete | *melk*, *lettertjesvermicelli*
measure | concrete | *euro*, *kwartje*
place | concrete | *amsterdam*, *voorkamer*
time | concrete | *kerstavond*, *periode*
concrete event | concrete | *ademhaling*, *stakingsacties*
miscellaneous concrete | concrete | *galblaas*, *vulkaan*
abstract substance | abstract | *fosfor*, *tumorcellen*
abstract event | abstract | *crisis*, *status-update*
organization | abstract | *nato*, *warenautoriteit*
miscellaneous abstract (nondynamic) | abstract | *motto*, *woordfrequentie*
*ambiguous words that belong to more than one type* | undefined | *steun*, *underground*

## Scores and Diffculty Levels

[...TBA..]

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
