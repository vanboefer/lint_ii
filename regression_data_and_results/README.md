# Linear Regression: Data and Results

LiNT-II readability score is calculated with the following formula:

```
LiNT-II score = 

  100 - (
      - 4.30
      + (17.31 * word frequency)
      - (1.62  * syntactic dependency length)
      - (2.54  * content words per clause)
      + (15.95 * proportion concrete nouns)
  )
```

The formula's coefficients were estimated using a linear regression model fitted on empirical reading comprehension data collected by [Kleijn (2018)](https://lint.hum.uu.nl/assets/kleijn-2018.pdf). The data comprises of 120 texts (which are in fact 60 texts in two versions), which were administered as cloze tests (fill-in masked words) to 2,753 Dutch secondary school students with various reading skills.

The **dependent variable** for the linear regression is the mean proportion of correct answers in the cloze test per text (adjusted to the reading skills of the participants). The **independent variables** are the four text features: word frequency, syntactic dependency length, content words per clause, proportion concrete nouns.

## Version variations

SpaCy models are tightly coupled to the version they were trained with. This means that `nl_core_news_lg 3.7` might output different feature values than `nl_core_news_lg 3.8`. This in turn affects the linear regression: both the R<sup>2</sup> metric and the coefficients.

In addition, the version of the [noun list](https://github.com/vanboefer/lint_ii/blob/main/src/lint_ii/linguistic_data/data/nouns_sem_types_20260420.parquet) (which is used for semantic type classification and compound information) also affects the values of the features and consequently the regression results.

The above formula is based on the following versions:
- Model: `nl_core_news_lg 3.7` (spaCy 3.7)
- Noun list: [nouns_sem_types_20260420.parquet](https://github.com/vanboefer/lint_ii/blob/main/src/lint_ii/linguistic_data/data/nouns_sem_types_20260420.parquet)

This combination results in **adjusted R<sup>2</sup> = 0.74**, meaning that the model explains 74% of the variance in the comprehension data.

Following users' requests, we decided to relax the version requirements in order to accommodate  broader usability of the LiNT-II package. However, note that spaCy 3.8 results in lower R<sup>2</sup> values:

Model version | Noun list version | Adjusted R<sup>2</sup> 
--- | --- | ---
3.7.0 | nouns_sem_types_20251118 | **0.74**
3.7.0 | nouns_sem_types_20260420 | **0.74**
3.8.0 | nouns_sem_types_20251118 | 0.73
3.8.0 | nouns_sem_types_20260420 | 0.72

Therefore, 

- **We recommend using spaCy 3.7**, if possible.
- The latest version of the noun list is always loaded automatically; if you want to override this, remove the undesired version from your [data directory](https://github.com/vanboefer/lint_ii/tree/main/src/lint_ii/linguistic_data/data).
- The appropriate coefficients will be used based on the automatically recognized versions in your installation.

## Reproducibility

For transparency and reproducibility, we include in this directory:
- Comprehension data: `parquet` files with the values for both the dependent and the independent variables for each version we tested. The files contain the calculated feature values and the mean proportion of correct answers in the cloze test per text. They do not contain the texts. The full dataset (including the texts) is available upon request via DANS: [*Leesbaarheidsindex voor het Nederlands*](https://ssh.datastations.nl/dataset.xhtml?persistentId=doi:10.17026/dans-z4y-gbmq).
- Regression overview: `json` file with the full results of the linear regression per each version we tested.
