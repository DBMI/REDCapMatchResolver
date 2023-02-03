from enum import Enum
from typing import NamedTuple, Union

import pandas  # type: ignore[import]

class ReportLine(NamedTuple):
    name: str
    epic_value: str
    redcap_value: str

class CrcReason(Enum):
    FAMILY: int
    SAME_ADDRESS: int
    PARENT_CHILD: int
    OTHER: int
    @classmethod
    def convert(cls, decision: str) -> CrcReason: ...

class CrcReview(Enum):
    MATCH: int
    NO_MATCH: int
    NOT_SURE: int
    @classmethod
    def convert(cls, decisions: Union[str, list, tuple]) -> Union[CrcReview, list]: ...
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
    @staticmethod
    def convert_nulls(value: str) -> Union[str, None]: ...
    def read_file(self, report_filename: str) -> pandas.DataFrame: ...
    def read_text(self, block_txt: str) -> pandas.DataFrame: ...
    @classmethod
    def _break_into_pieces(cls, data_line):
        pass
    @classmethod
    def _find_column(cls, next_line, param):
        pass
    @classmethod
    def _parse_line(cls, data_line, epic_index, redcap_index):
        pass
    def _read(self):
        pass
    def _open_file(self, report_filename):
        pass
    def _open_text(self, block_txt):
        pass
    def _next_line(self):
        pass
    def _read_crc_decision(self):
        pass
    def _at_end(self):
        pass
