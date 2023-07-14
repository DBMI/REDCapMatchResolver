import sqlite3
from logging import Logger
from typing import Union

import pandas  # type: ignore[import]

from .redcap_report_reader import DecisionReview, REDCapReportReader

class REDCapMatchResolver:
    def __init__(self, connection: sqlite3.Connection = ...) -> None:
        self.__dataframe_fields_list: list = None
        self.__database_fields_list: list = None
        self.__connection: sqlite3.Connection = None
        self.__redcap_reader: REDCapReportReader = None
        self.__log: Logger = None
        ...
    def __build_required_fields(self) -> None:
        pass
    def __create_connection(self, db_filename: str) -> sqlite3.Connection:
        pass
    def __create_decisions_table(self) -> bool:
        pass
    def __drop_decisions_table(self) -> bool:
        pass
    def __drop_matches_table(self) -> bool:
        pass
    def __init_decision_table(self) -> bool:
        pass
    def __init_matches_table(self) -> bool:
        pass
    def __insert_report(self, report_df: pandas.DataFrame) -> None:
        pass
    def insert_reviewed_reports(self) -> bool:
        pass
    def __is_connected(self, connection: Union[sqlite3.Connection, None]) -> bool:
        pass
    def lookup_potential_match(self, match_block: str) -> DecisionReview: ...
    def read_reports(self, import_folder: str) -> bool: ...
    def __setup_db(self, db_filename: str) -> sqlite3.Connection:
        pass
    def __reader_ready(self):
        pass
    def __translate_decision(self, crc_enum: str) -> int:
        pass
