class LintScorer:
    """LiNT-II scoring functionality."""

    @staticmethod
    def calculate_lint_score(
        freq_log: float,
        max_sdl: int,
        content_words_per_clause: float,
        proportion_concrete: float,
    ) -> float:
        """
        Calculate LiNT readability score using the formula.

        The weights that are currently used in the formula are from the original LiNT implementation where the features were extracted with T-Scan. TO DO: redo the regression analysis and adjust the weights to fit the new implementation.

        Args:
            freq_log: Average log word frequency of all content words (excluding names)
            max_sdl: Maximum syntactic dependency length
            content_words_per_clause: Content words (excluding adverbs) per clause
            proportion_concrete: Proportion of concrete nouns out of all nouns

        Returns:
            LiNT score (0-100, higher = more difficult, less readable)
        """
        score = (
            3.204
            + (15.845 * freq_log)
            - (1.331 * max_sdl)
            - (3.829 * content_words_per_clause)
            + (13.096 * proportion_concrete)
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
