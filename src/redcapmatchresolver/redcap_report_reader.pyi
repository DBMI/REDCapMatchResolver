from enum import Enum
from typing import NamedTuple, Union

import pandas  # type: ignore[import]

class ReportLine(NamedTuple):
    name: str
    epic_value: str
    redcap_value: str

class DecisionReason(Enum):
    RELATIVES: int
    SAME_ADDRESS: int
    PARENT_CHILD: int
    OTHER: int
    NO_INFO: int
    @classmethod
    def convert(cls, decision: str) -> DecisionReason: ...

class DecisionReview(Enum):
    MATCH: int
    NO_MATCH: int
    NOT_SURE: int
    @classmethod
    def convert(
        cls, decisions: Union[str, list, tuple]
    ) -> Union[DecisionReview, list]: ...
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
    def __break_into_pieces(cls, data_line) -> list:
        pass

    @staticmethod
    def convert_nulls(value: str) -> Union[str, None]: ...
    @classmethod
    def _find_column(cls, next_line, param) -> int:
        pass

    def __next_line(self) -> str | None:
        pass

    def __open_file(self, report_filename) -> None:
        pass

    def __open_text(self, block_txt) -> None:
        pass

    @classmethod
    def __parse_line(cls, data_line, epic_index, redcap_index) -> ReportLine:
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
