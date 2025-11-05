class LintScorer:
    """
    LiNT-II scoring algorithms for Dutch text readability assessment.

    This class implements the LiNT-II readability formula, which combines four 
    linguistic features to produce a readability score and a difficulty level. 
    
    The formula's coefficients were estimated using a linear regression model fitted on
    empirical reading comprehension data from Dutch highschool students.

    Attributes
    ----------
    COEFFICIENTS : dict[str, float]
        Regression coefficients for the LiNT-II formula:
        - constant: Intercept term
        - freq_log: Weight for mean log word frequency
        - max_sdl: Weight for maximum syntactic dependency length
        - content_words_per_clause: Weight for content words per clause
        - proportion_concrete: Weight for proportion of concrete nouns

    Methods
    -------
    calculate_lint_score(freq_log, max_sdl, content_words_per_clause, proportion_concrete) -> float
        Compute LiNT-II readability score from linguistic features.
    get_difficulty_level(score) -> int
        Convert LiNT score to difficulty level (1-4).

    Notes
    -----
    The LiNT-II formula computes readability as:

    .. code-block:: text

        raw score = constant 
                  + (coefficient_freq * mean_log_word_frequency)
                  + (coefficient_sdl * max_syntactic_dependency_length)
                  + (coefficient_cwc * content_words_per_clause)
                  + (coefficient_concrete * proportion_concrete_nouns)

        LiNT = 100 - clamp(raw_score, 0, 100)

    Higher scores indicate more difficult texts.

    **Difficulty Level Interpretation**:

    ========  =====  =======================================
    Level     Range  Adults Struggling to Understand
    ========  =====  =======================================
    1 (easy)  0-34   15%
    2         35-46  31%
    3         47-60  55%
    4 (hard)  61+    82%
    ========  =====  =======================================

    Examples
    --------
    >>> from lint_ii.core.lint_scorer import LintScorer
    >>> score = LintScorer.calculate_lint_score(
    ...     freq_log = 5.2,
    ...     max_sdl = 3,
    ...     content_words_per_clause = 4.5,
    ...     proportion_concrete = 0.6
    ... )
    >>> score
    32.2
    >>> LintScorer.get_difficulty_level(score)
    1

    See Also
    --------
    ReadabilityAnalysis : Document-level readability analysis
    SentenceAnalysis : Sentence-level readability analysis
    """

    COEFFICIENTS = {
        'constant': -7.83150696,
        'freq_log': 17.05020517,
        'max_sdl': -1.33286119,
        'content_words_per_clause': -2.38774819,
        'proportion_concrete': 11.7213491,
    }

    @staticmethod
    def calculate_lint_score(
        freq_log: float,
        max_sdl: int | float,
        content_words_per_clause: float,
        proportion_concrete: float,
    ) -> float:
        """
        Calculate LiNT-II readability score using the formula.

        Parameters
        ----------
        freq_log : float
            Mean log word frequency of content words (excluding proper nouns).
            Typically ranges from 2.0 (rare words) to 7.0 (common words).
        max_sdl : int | float
            Maximum syntactic dependency length. For sentence-level scoring, this is 
            the longest distance between a word and its syntactic head in that 
            sentence. For document-level scoring, this is the mean of the maximum SDL 
            values across all sentences.
        content_words_per_clause : float
            Average number of content words (excluding adverbs, except manner 
            adverbs) per clause. Higher values indicate denser information.
        proportion_concrete : float
            Proportion of concrete nouns out of all nouns (0.0-1.0). Higher 
            values indicate more concrete language.

        Returns
        -------
        float
            LiNT readability score (0-100). Higher scores indicate more difficult, 
            less readable text. Scores are clamped to the [0, 100] range.
        """
        score = (
            + LintScorer.COEFFICIENTS['constant']
            + LintScorer.COEFFICIENTS['freq_log'] * freq_log
            + LintScorer.COEFFICIENTS['max_sdl'] * max_sdl
            + LintScorer.COEFFICIENTS['content_words_per_clause'] * content_words_per_clause
            + LintScorer.COEFFICIENTS['proportion_concrete'] * proportion_concrete
        )
        return min(100.0, max(0.0, 100 - score))

    @staticmethod
    def get_difficulty_level(score: float) -> int:
        """
        Convert LiNT score to difficulty level.

        Parameters
        ----------
        score : float
            LiNT readability score (0-100). Higher scores indicate more difficult text.

        Returns
        -------
        int
            Difficulty level from 1 (easiest) to 4 (most difficult):
            
            - Level 1 (0-34): Easy text, 15% of adults struggle
            - Level 2 (35-46): Moderate text, 31% of adults struggle
            - Level 3 (47-60): Difficult text, 55% of adults struggle
            - Level 4 (61+): Very difficult text, 82% of adults struggle
        """
        if score <= 34:
            return 1
        elif score <= 46:
            return 2
        elif score <= 60:
            return 3
        else:
            return 4
