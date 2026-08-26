from enum import Enum
from typing import NamedTuple

import pandas

class ReportLine(NamedTuple):
    name: str
    epic_value: str
    redcap_value: str

class DecisionReason(Enum):
    RELATIVES = 1
    SAME_ADDRESS = 2
    PARENT_CHILD = 3
    OTHER = 4
    NO_INFO = 5

    @classmethod
    def convert(cls, decision: str) -> DecisionReason: ...

class DecisionReview(Enum):
    MATCH = 3
    NO_MATCH = 2
    NOT_SURE = 1
    @classmethod
    def convert(cls, decisions: str | list | tuple) -> DecisionReview | list: ...
    def __eq__(self, other: object) -> bool: ...
    def __gt__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...

class REDCapReportReader:
    __separator = None

    def __init__(self) -> None:
        self.__row_index = None
        self.__report_contents = None
        self.__log = None
        ...

    def __at_end(self) -> bool:
        pass

    @classmethod
    def __break_into_pieces(cls, data_line: str) -> list:
        pass

    @staticmethod
    def convert_nulls(value: str) -> str | None: ...
    @staticmethod
    def _find_column(data_line: str, keyword: str) -> int:
        pass

    def __next_line(self) -> str | None:
        pass

    def __open_file(self, report_filename: str) -> None:
        pass

    def __open_text(self, block_txt: str) -> None:
        pass

    def __read(self) -> pandas.DataFrame:
        pass

    def __read_decision(self) -> tuple:
        pass

    def read_file(self, report_filename: str) -> pandas.DataFrame: ...
    def __read_pat_id(self) -> str:
        pass

    def __read_study_id(self) -> str:
        pass

    def read_text(self, block_txt: str) -> pandas.DataFrame: ...
