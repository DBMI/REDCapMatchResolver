import sqlite3
from logging import Logger
from typing import Union

import pandas  # type: ignore[import]

from .match_records import MatchRecord, MatchTuple
from .redcap_report_reader import DecisionReview, REDCapReportReader
from .redcap_report_writer import REDCapReportWriter

class REDCapMatchResolver:
    def __init__(self, log: Logger, connection: sqlite3.Connection = ...) -> None:
        self.__connection: sqlite3.Connection = None
        self.__database_fields_list: list = None
        self.__dataframe_fields_list: list = None
        self.__log: Logger = None
        self.__redcap_reader: REDCapReportReader = None
        self.__redcap_writer: REDCapReportWriter = None
        ...

    def add_possible_wobbler(self, match_summary: str) -> bool: ...
    def __build_required_fields(self) -> None: ...
    def __create_connection(self, db_filename: str) -> sqlite3.Connection: ...
    def __create_decisions_table(self) -> bool: ...
    def __drop_decisions_table(self) -> bool: ...
    def __drop_matches_table(self) -> bool: ...
    def __init_decisions_table(self) -> bool: ...
    def __init_matches_table(self) -> bool: ...
    def __insert_report(self, report_df: pandas.DataFrame) -> None: ...
    def insert_reviewed_reports(self) -> bool: ...
    def __insert_reviewed_match_reports(self) -> bool: ...
    def __insert_reviewed_no_match_reports(self) -> bool: ...
    def __is_connected(self) -> bool: ...
    def lookup_potential_match(self, match_block: str) -> DecisionReview: ...
    def read_reports(self, import_folder: str) -> bool: ...
    def report_wobblers(self, new_reports_directory: str) -> tuple: ...
    def __setup_db(self, db_filename: str) -> sqlite3.Connection: ...
    def __reader_ready(self) -> bool: ...
    def __translate_decision(self, crc_enum: str) -> int: ...
