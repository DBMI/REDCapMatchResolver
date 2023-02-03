import sqlite3
from typing import Union

from .redcap_report_reader import CrcReview as CrcReview

class REDCapMatchResolver:
    def __init__(self, db_filename: str = ...) -> None:
        self.__dataframe_fields_list = None
        self.__database_fields_list = None
        self.__conn = None
        self.__redcap_reader = None
        self.__log = None
        ...
    def lookup_potential_match(self, match_block: str) -> CrcReview: ...
    def read_reports(self, import_folder: str) -> bool: ...
    def _is_connected(self, conn: Union[sqlite3.Connection, None]):
        pass
    def _reader_ready(self):
        pass
    def _insert_report(self, report_df):
        pass
    def _build_required_fields(self):
        pass
    def _setup_db(self, db_filename):
        pass
    def _build_decision_table(self, connection):
        pass
    def _create_connection(self, db_filename):
        pass
    def _create_matches_table(self, connection):
        pass
    def _create_decisions_table(self, conn):
        pass
    def _drop_decisions_table(self, conn):
        pass
    def _drop_matches_table(self, conn):
        pass
    def _translate_crc_decision(self, crc_decision_string):
        pass
