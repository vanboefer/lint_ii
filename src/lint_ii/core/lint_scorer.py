from functools import cached_property


class LintScorer:
    """
    LiNT-II scoring algorithm for Dutch text readability assessment.

    This class implements the LiNT-II readability formula, which combines four 
    linguistic features to produce a readability score and a difficulty level. 
    
    The formula's coefficients were estimated using a linear regression model fitted on
    empirical reading comprehension data from Dutch highschool students.

    The formula returns None if one of the four feature values is None.

    Parameters
    ----------
    freq_log : float | None
        Mean log word frequency of content words (excluding proper nouns); calculated either on sentence-level or on document-level.
    max_sdl : int | float | None
        Maximum syntactic dependency length. For sentence-level scoring, this is 
        the longest distance between a word and its syntactic head in that 
        sentence. For document-level scoring, this is the mean of the maximum SDL 
        values across all sentences.
    content_words_per_clause : float | None
        Average number of content words per clause. Higher values indicate denser information.
    proportion_concrete : float | None
        Proportion of concrete nouns out of the total nouns; calculated either on sentence-level or on document-level.
    
    Attributes & Properties
    -----------------------
    COEFFICIENTS : dict[str, float]
        Regression coefficients for the LiNT-II formula:
        - constant: Intercept term
        - freq_log: Weight for mean log word frequency
        - max_sdl: Weight for maximum syntactic dependency length
        - content_words_per_clause: Weight for content words per clause
        - proportion_concrete: Weight for proportion of concrete nouns
    score : float | None
        LiNT-II score readability score (0-100). Higher scores indicate more difficult, less readable text. Scores are clamped to the [0, 100] range.
        Returns None if the guardrail requirements are not met, i.e. if one of the four feature values is None.
    level : int | None
        LiNT-II difficulty level, from 1 (easiest) to 4 (most difficult):
            - Level 1 [0-34): Easy text, 14% of adults struggle to understand
            - Level 2 [34-46): Moderate text, 29% of adults struggle to understand
            - Level 3 [46-58): Difficult text, 53% of adults struggle to understand
            - Level 4 [58-100]: Very difficult text, 78% of adults struggle
    Notes
    -----
    The LiNT-II formula computes readability as:

    .. code-block:: text

        raw score = constant 
                  + (coefficient_freq * mean_log_word_frequency)
                  + (coefficient_sdl * max_syntactic_dependency_length)
                  + (coefficient_cwc * content_words_per_clause)
                  + (coefficient_concrete * proportion_concrete_nouns)

        LiNT-II score = 100 - clamp(raw_score, 0, 100)

    Higher scores indicate more difficult texts.

    **Difficulty Level Interpretation**:

    ========  =========  =======================================
    Level     Range      Adults Struggling to Understand
    ========  =========  =======================================
    1 (easy)  [0-34)     14%
    2         [34-46)    29%
    3         [46-58)    53%
    4 (hard)  [58-100]   78%
    ========  =========  =======================================

    Examples
    --------
    >>> from lint_ii.core.lint_scorer import LintScorer
    >>> lint_ii = LintScorer(
    ...     freq_log = 5.2,
    ...     max_sdl = 3,
    ...     content_words_per_clause = 4.5,
    ...     proportion_concrete = 0.6
    ... )
    >>> lint_ii.score
    21.020445599999988
    >>> lint_ii.level
    1

    See Also
    --------
    ReadabilityAnalysis : Document-level readability analysis
    SentenceAnalysis : Sentence-level readability analysis
    """

    COEFFICIENTS = {
        'constant': -4.20782,
        'freq_log': 17.283729,
        'max_sdl': -1.624415,
        'content_words_per_clause': -2.536780,
        'proportion_concrete': 16.001231,
    }

    def __init__(
        self,
        freq_log: float | None,
        max_sdl: int | float | None,
        content_words_per_clause: float | None,
        proportion_concrete: float | None,
    ) -> None:
        """
        Parameters
        ----------
        freq_log : float | None
            Mean log word frequency of content words (excluding proper nouns); calculated either on sentence-level or on document-level.
        max_sdl : int | float | None
            Maximum syntactic dependency length. For sentence-level scoring, this is 
            the longest distance between a word and its syntactic head in that 
            sentence. For document-level scoring, this is the mean of the maximum SDL 
            values across all sentences.
        content_words_per_clause : float | None
            Average number of content words per clause. Higher values indicate denser information.
        proportion_concrete : float | None
            Proportion of concrete nouns out of the total nouns; calculated either on sentence-level or on document-level.
        """
        self.freq_log = freq_log
        self.max_sdl = max_sdl
        self.content_words_per_clause = content_words_per_clause
        self.proportion_concrete = proportion_concrete

    @cached_property
    def score(self) -> float | None:
        if self._meets_guard_rail_requirements:
            return self._calculate_lint_score()
        return None

    @cached_property
    def level(self) -> int | None:
        if self._meets_guard_rail_requirements:
            return self._get_difficulty_level()
        return None

    @property
    def _meets_guard_rail_requirements(self):
        features = [
            self.freq_log,
            self.max_sdl,
            self.content_words_per_clause,
            self.proportion_concrete,
        ]
        return all(f is not None for f in features)

    def _calculate_lint_score(self) -> float:
        """
        Calculate LiNT-II readability score using the formula.

        Returns
        -------
        float
            LiNT readability score (0-100). Higher scores indicate more difficult, 
            less readable text. Scores are clamped to the [0, 100] range.
        """
        result = (
            + self.COEFFICIENTS['constant']
            + self.COEFFICIENTS['freq_log'] * self.freq_log
            + self.COEFFICIENTS['max_sdl'] * self.max_sdl
            + self.COEFFICIENTS['content_words_per_clause'] * self.content_words_per_clause
            + self.COEFFICIENTS['proportion_concrete'] * self.proportion_concrete
        )
        score = min(100.0, max(0.0, 100 - result))
        return score

    def _get_difficulty_level(self) -> int:
        """
        Convert LiNT-II score to difficulty level.

        Returns
        -------
        int
            Difficulty level from 1 (easiest) to 4 (most difficult):
            
            - Level 1 [0-34): Easy text, 14% of adults struggle to understand
            - Level 2 [34-46): Moderate text, 29% of adults struggle to understand
            - Level 3 [46-58): Difficult text, 53% of adults struggle to understand
            - Level 4 [58-100]: Very difficult text, 78% of adults struggle
        """
        if self.score < 34:
            level = 1
        elif self.score < 46:
            level = 2
        elif self.score < 58:
            level = 3
        else:
            level = 4

        return level