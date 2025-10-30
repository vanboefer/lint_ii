class LintScorer:
    """LiNT-II scoring functionality."""

    COEFFICIENTS = {
        'constant': -5.15960462,
        'freq_log': 16.13411558,
        'max_sdl': -1.28483912,
        'content_words_per_clause': -3.52243722,
        'proportion_concrete': 16.25887905,
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

        Args:
            freq_log: Average log word frequency of all content words (excluding names)
            max_sdl: Maximum syntactic dependency length
            content_words_per_clause: Content words (excluding function adverbs) per clause
            proportion_concrete: Proportion of concrete nouns out of all nouns

        Returns:
            LiNT score (0-100, higher = more difficult, less readable)
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

        Args:
            score: LiNT score (0-100)

        Returns:
            Difficulty level (1-4, where 4 is most difficult)
        """
        if score <= 34:
            return 1
        elif score <= 46:
            return 2
        elif score <= 60:
            return 3
        else:
            return 4
