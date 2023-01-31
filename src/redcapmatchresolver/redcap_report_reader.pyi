import pandas
from .utilities import Utilities as Utilities
from _typeshed import Incomplete
from enum import Enum
from typing import NamedTuple

class ReportLine(NamedTuple):
    name: Incomplete
    epic_value: Incomplete
    redcap_value: Incomplete

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
    def __init__(self) -> None: ...
    @staticmethod
    def convert_nulls(value: str) -> Union[str, None]: ...
    def read_file(self, report_filename: str) -> pandas.DataFrame: ...
    def read_text(self, block_txt: str) -> pandas.DataFrame: ...
