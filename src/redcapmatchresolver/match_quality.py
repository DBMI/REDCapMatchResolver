"""
Module: contains MatchQuality class.
"""

from enum import Enum


class MatchQuality(Enum):
    """Various quality of matches (in terms of any particular field)"""

    IGNORED = -10
    MATCHED_NOPE = -1
    MATCHED_NULL = 0
    MATCHED_EXACT = 1
    MATCHED_CASE_INSENSITIVE = 2
    MATCHED_ALPHA_NUM = 3
    MATCHED_SUBSTRING = 4
    MATCHED_FUZZY = 5
    MATCHED_CALCULATED = 6

    @classmethod
    def convert(cls, match_str: str):
        """Create MatchQuality object from a string.

        Parameters
        ----------
        match_str : str

        Returns
        -------
        match : MatchQuality object
        """
        if match_str is None:
            raise TypeError("Input 'match_str' is not the expected string.")

        if not isinstance(match_str, str):
            raise TypeError("Input 'match_str' is not the expected string.")

        match = MatchQuality.MATCHED_NULL

        if "ignored" in match_str.lower():
            match = MatchQuality.IGNORED

        if "nope" in match_str.lower():
            match = MatchQuality.MATCHED_NOPE

        if "exact" in match_str.lower():
            match = MatchQuality.MATCHED_EXACT

        if "case_insensitive" in match_str.lower():
            match = MatchQuality.MATCHED_CASE_INSENSITIVE

        if "alpha_num" in match_str.lower():
            match = MatchQuality.MATCHED_ALPHA_NUM

        if "substring" in match_str.lower():
            match = MatchQuality.MATCHED_SUBSTRING

        if "fuzzy" in match_str.lower():
            match = MatchQuality.MATCHED_FUZZY

        if "calculated" in match_str.lower():
            match = MatchQuality.MATCHED_CALCULATED

        return match

    def good_enough(self) -> bool:
        """We'll consider all these quality of matches as "good enough" to
        say the fields are equal.

        Returns
        -------
        good_enough : bool
        """
        if not self:  # pragma: no cover
            return False

        return self.value > 0

    def ignored(self) -> bool:
        """Allows external code to test if the special case of "IGNORED" is true.

        Returns
        -------
        ignored : bool
        """
        if not self:  # pragma: no cover
            return False

        return self == MatchQuality.IGNORED

    def __str__(self) -> str:  # pylint: disable = too-many-return-statements
        if self == MatchQuality.IGNORED:
            return "ignored"

        if self == MatchQuality.MATCHED_EXACT:
            return "exact"

        if self == MatchQuality.MATCHED_NULL:
            return "null"

        if self == MatchQuality.MATCHED_CASE_INSENSITIVE:
            return "lower"

        if self == MatchQuality.MATCHED_ALPHA_NUM:
            return "alphanum"

        if self == MatchQuality.MATCHED_FUZZY:
            return "fuzzy"

        if self == MatchQuality.MATCHED_CALCULATED:
            return "calculated"

        if self == MatchQuality.MATCHED_SUBSTRING:
            return "substring"

        return "-"
