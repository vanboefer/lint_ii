# LiNT-II: licences of bundled data

LiNT-II **code** is licensed under the EUPL-1.2. However, some of the **linguistic data files** in this folder are based on third-party resources. These files are **not covered by the EUPL** and are subject to their own terms, which **do not allow commercial use** without permission from the rights holders.

| Data | Files | Source | Terms |
| --- | --- | --- | --- |
| Word frequencies | `subtlex_wordfreq.parquet` | SUBTLEX-NL | CC BY-NC-SA 4.0 |
| Noun list (semantic types) | `nouns_sem_types_*.parquet` | Partly based on the Referentiebestand Nederlands (RBN) | See below |
| Other data | `manner_adverbs_*.parquet`, `measurement_units.parquet`, `subtlex_wordfreq_skiplist.parquet` | LiNT-II authors | EUPL-1.2 |

### SUBTLEX-NL

The word frequencies are derived from SUBTLEX-NL (Keuleers, Brysbaert & New, 2010), licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). These files are distributed under the same licence. Commercial use requires permission from the SUBTLEX-NL authors (Marc Brysbaert, Ghent University).

> Keuleers, E., Brysbaert, M., & New, B. (2010). SUBTLEX-NL: A new measure for Dutch word frequency based on film subtitles. *Behavior Research Methods, 42*(3), 643–650. https://doi.org/10.3758/BRM.42.3.643

### Noun list

The noun list contains 92,757 nouns with their semantic type. It was originally based on the
Referentiebestand Nederlands (RBN), and has since been substantially extended and revised by the LiNT authors: 38,477 nouns also occur in the RBN, of which 23,240 have the same semantic type as in the RBN.

The RBN is made available by the Instituut voor de Nederlandse Taal (INT) under a non-commercial licence. We are in contact with the INT about the terms for distributing this list. **Do not use the noun list for commercial purposes**; for commercial use, please contact the [INT](https://ivdnt.org). For the latest information, see https://github.com/vanboefer/lint_ii#data-and-licensing.

> Referentiebestand Nederlands - RBN (Version 2.0.1) (2014) [Data set]. Available at the Dutch Language Institute: http://hdl.handle.net/10032/tm-a2-n2