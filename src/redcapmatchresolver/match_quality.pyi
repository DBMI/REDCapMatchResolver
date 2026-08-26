from enum import Enum
from typing import Any

class MatchQuality(Enum):
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
    def convert(cls: Any, match_str: str) -> Any: ...
    def good_enough(self) -> bool: ...
    def ignored(self) -> bool: ...
