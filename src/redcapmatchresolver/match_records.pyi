from typing import List, NamedTuple, Union

import pandas
from redcapduplicatedetector.match_quality import MatchQuality

class MatchTuple(NamedTuple):
    bool: bool
    summary: str

class CommonField:
    def __init__(self, common_name: str, epic_field: str, redcap_field: str) -> None:
        self.__common_name: str
        self.__epic_field: str
        self.__redcap_field: str
        ...
    def common_name(self) -> str: ...
    def epic_field(self) -> str: ...
    def epic_field_present(self, field_name: str) -> bool: ...
    def redcap_field(self) -> str: ...
    def redcap_field_present(self, field_name: str) -> bool: ...

class MatchRecord:
    COMMON_FIELDS: List[CommonField]
    FORMAT: str
    SCORE_FIELDS: List[str]

    def __init__(self, row: pandas.Series) -> None:
        self.__score: int
        self.__record: dict = {}
        ...
    @staticmethod
    def as_alphanum(string: str) -> str: ...
    def __build_dictionary(self, row: pandas.Series) -> None:
        pass
    @staticmethod
    def evaluate_single_variable(
        epic_value: str, redcap_value: str
    ) -> MatchQuality: ...
    def __init_summary(self, aliases: list = ...) -> str:
        pass
    def is_match(
        self, exact: bool = ..., criteria: int = ..., aliases: list = ...
    ) -> MatchTuple: ...
    def mrns_match(self) -> bool: ...
    def names_match(self) -> bool: ...
    def pat_id(self) -> str: ...
    def score(self) -> int: ...
    def __score_record(self) -> None:
        pass
    def __select_best_phone(self, row: pandas.Series) -> None:
        pass
    def use_aliases(self, aliases: list) -> None: ...

class MatchVariable:
    def __init__(
        self,
        epic_value: str,
        redcap_value: str,
        match_quality: Union[MatchQuality, int, None] = ...,
    ) -> None:
        self.__epic_value: str
        self.__redcap_value: str
        self.__match_quality: MatchQuality
        ...
    def assign_match_quality(self, match_quality: Union[MatchQuality, int]) -> None: ...
    def epic_value(self) -> str: ...
    def __evaluate(self) -> None: ...
    def good_enough(self) -> bool: ...
    def match_quality(self) -> MatchQuality: ...
    def redcap_value(self) -> str: ...
    def summarize_match(self, common_name: str) -> str: ...
