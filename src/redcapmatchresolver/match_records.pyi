from typing import List, NamedTuple, Union

import pandas
from redcap_update import REDCapUpdate
from redcapduplicatedetector.match_quality import MatchQuality

class MatchTuple(NamedTuple):
    bool: bool
    summary: str

class CommonField:
    def __init__(self, common_name: str, epic_field: str, redcap_field: str) -> None:
        self.__common_name: str = None
        self.__epic_field: str = None
        self.__redcap_field: str = None
        ...

    def common_name(self) -> str: ...
    def epic_field(self) -> str: ...
    def epic_field_present(self, field_name: str) -> bool: ...
    def redcap_field(self) -> str: ...
    def redcap_field_present(self, field_name: str) -> bool: ...

class MatchRecord:
    BONUS_SCORE_FIELDS: List[str]
    COMMON_FIELDS: List[CommonField]
    FORMAT: str
    SCORE_FIELDS: List[str]

    def __init__(
        self, row: pandas.Series, facility_addresses: list, facility_phone_numbers: list
    ) -> None:
        self.__alias = None
        self.__mrn_hx = None
        self.__pat_id = None
        self.__study_id = None
        self.__record: dict = {}
        self.__redcap_update: REDCapUpdate = None
        self.__score: int = None
        ...

    @staticmethod
    def as_alphanum(string: str) -> str: ...
    def __build_dictionary(
        self, row: pandas.Series, facility_addresses: list, facility_phone_numbers: list
    ) -> None:
        pass

    def __epic_mrn(self) -> str: ...
    def __epic_name(self):
        pass

    @staticmethod
    def evaluate_single_variable(
        epic_value: str, redcap_value: str
    ) -> MatchQuality: ...
    def __init_summary(self, aliases=None, mrn_hx=None) -> str: ...
    def is_match(
        self, exact: bool = ..., criteria: int = ..., aliases=None, mrn_hx=None
    ) -> MatchTuple: ...
    def pat_id(self) -> str: ...
    def __redcap_mrn(self) -> str: ...
    def __redcap_name(self) -> tuple: ...
    def redcap_update(self) -> REDCapUpdate: ...
    def score(self) -> int: ...
    def __score_record(self) -> None: ...
    def __select_best_phone(
        self, row: pandas.Series, facility_phone_numbers: list
    ) -> None: ...
    def __select_best_epic_name(self, row: pandas.Series) -> None: ...
    def __select_best_epic_mrn(self, row: pandas.Series) -> None: ...
    def study_id(self) -> int: ...

class MatchVariable:
    def __init__(
        self,
        epic_value: str,
        redcap_value: str,
        ignore_list=None,
    ) -> None:
        self.__epic_value = None
        self.__match_quality = None
        self.__redcap_value = None
        ...

    def assign_match_quality(self, match_quality: Union[MatchQuality, int]) -> None: ...
    def epic_value(self) -> str: ...
    def __evaluate(self, ignore_list: list) -> None: ...
    def good_enough(self) -> bool: ...
    def ignored(self) -> bool: ...
    def match_quality(self) -> MatchQuality: ...
    def redcap_value(self) -> str: ...
    def summarize_match(self, common_name: str) -> str: ...
