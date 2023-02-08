import sqlite3
from typing import Union

import pandas  # type: ignore[import]

from .redcap_report_reader import CrcReview as CrcReview

class REDCapMatchResolver:
    def __init__(self, db_filename: str = ...) -> None:
        self.__dataframe_fields_list = None
        self.__database_fields_list = None
        self.__conn = None
        self.__redcap_reader = None
        self.__log = None
        ...
    def __build_decision_table(self, connection: sqlite3.Connection):
        pass
    def __build_required_fields(self) -> None:
        pass
    def __create_connection(self, db_filename: str) -> sqlite3.Connection:
        pass
    def __create_decisions_table(self, connection: sqlite3.Connection) -> bool:
        pass
    def __create_matches_table(self, connection: sqlite3.Connection) -> bool:
        pass
    def __drop_decisions_table(self, connection: sqlite3.Connection) -> bool:
        pass
    def __drop_matches_table(self, connection: sqlite3.Connection) -> bool:
        pass
    def __insert_report(self, report_df: pandas.DataFrame) -> bool:
        pass
    def __is_connected(self, connection: Union[sqlite3.Connection, None]) -> bool:
        pass
    def lookup_potential_match(self, match_block: str) -> CrcReview: ...
    def read_reports(self, import_folder: str) -> bool: ...
    def __setup_db(self, db_filename: str) -> sqlite3.Connection:
        pass
    def __reader_ready(self):
        pass
    def __translate_crc_decision(self, crc_enum: str) -> int:
        pass
