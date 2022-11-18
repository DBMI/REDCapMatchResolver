"""
Module: contains class REDCapMatchResolver
used to create/use a SQLite database from
CRC-reviewed match reports.
"""
import glob
import logging
import os
import pandas
import sqlite3
from sqlite3 import Connection, Error
from .utilities import Utilities
from .redcap_report_reader import REDCapReportReader


class REDCapMatchResolver:
    """
    Creates a SQLite database from stacks of match reports reviewed by CRCs.
    Allows other code to ask "has this match already been reviewed?" so that
    we're not asking the CRCs the same questions over and over.
    """
    def __init__(self):
        Utilities.setup_logging()
        self.__log = logging.getLogger(__name__)
        self.__conn = None
        self.__redcap_reader = None

    def _build_decision_table(self) -> bool:
        """Creates & populates table that translates

        Returns
        -------
        success : bool
        """
        if not self._create_decisions_table():
            self.__log.error("Unable to create 'decisions' table.")
            raise RuntimeError("Unable to create 'decisions' table.")

        cur = self.__conn.cursor()

        #   We want these values to exactly equal those in the CrcReview enum class.
        insert_sql = """INSERT INTO decisions(decision) VALUES('MATCH')"""
        cur.execute(insert_sql)
        insert_sql = """INSERT INTO decisions(decision) VALUES('NO_MATCH')"""
        cur.execute(insert_sql)
        insert_sql = """INSERT INTO decisions(decision) VALUES('NOT_SURE')"""
        cur.execute(insert_sql)
        self.__conn.commit()
        return True

    def _create_connection(self, db_filename: str = "temp_matches_database.db") -> bool:
        """ Initializes a SQLite database at the desired location.

        Parameters
        ----------
        db_filename : str Name of file to be created.

        Returns
        -------
        success : boolean
        """

        if db_filename is None or not isinstance(db_filename, str):
            self.__log.error("Input 'db_filename' is not the expected string.")
            raise TypeError("Input 'db_filename' is not the expected string.")

        Utilities.ensure_output_path(db_filename)

        try:
            self.__conn = sqlite3.connect(db_filename)
            success = self.__conn is not None and isinstance(self.__conn, Connection)
        except Error as e:
            self.__log.error(f"Unable to open file '{db_filename}' because '{str(e)}'.")
            raise e

        return success

    def _create_decisions_table(self) -> bool:
        """Creates the table that translates integer codes to text like 'Same' or 'Not Same'.

        Returns
        -------
        success : bool
        """
        if not self._is_connected():
            raise TypeError("Database is not connected.")

        if not self._drop_decisions_table():
            self.__log.error('Unable to drop "decisions" table.')
            raise RuntimeError('Unable to drop "decisions" table.')

        create_table_sql = """ CREATE TABLE IF NOT EXISTS decisions (
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    decision text NOT NULL
                                );"""

        try:
            c = self.__conn.cursor()
            c.execute(create_table_sql)
            self.__conn.commit()
            success = True
        except Error as e:
            self.__log.error(f"Unable to run 'create_table_sql' because '{str(e)}'.")
            raise e

        return success

    def _create_matches_table(self) -> bool:
        """Creates an empty 'matches' table in the database.

        Returns
        -------
        success : bool
        """
        if not self._is_connected():
            raise TypeError("Database is not connected.")

        if not self._drop_matches_table():
            self.__log.error('Unable to drop "matches" table.')
            raise RuntimeError('Unable to drop "matches" table.')

        create_table_sql = """ CREATE TABLE IF NOT EXISTS matches (
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    epic_mrn integer,
                                    redcap_mrn integer NOT NULL,
                                    epic_first text NOT NULL,
                                    redcap_first text NOT NULL,
                                    epic_last text NOT NULL,
                                    redcap_last text NOT NULL,
                                    epic_dob date,
                                    redcap_dob date,
                                    epic_addr_calculated text,
                                    redcap_addr_calculated text,
                                    epic_phone_calculated text,
                                    redcap_phone_calculated text,
                                    crc_decision text
                                );"""

        try:
            c = self.__conn.cursor()
            c.execute(create_table_sql)
            self.__conn.commit()
            success = True
        except Error as e:
            self.__log.error(f"Unable to run 'create_table_sql' because '{str(e)}'.")
            raise e

        return success

    def _drop_decisions_table(self) -> bool:
        """Drops decisions table so it can be created fresh.

        Returns
        -------
        success : bool
        """
        if not self._is_connected():
            raise TypeError("Database is not connected.")

        drop_table_sql = """ DROP TABLE IF EXISTS decisions; """

        try:
            c = self.__conn.cursor()
            c.execute(drop_table_sql)
            self.__conn.commit()
            success = True
        except Error as e:
            self.__log.error(f"Unable to run 'drop_decisions_table' because '{str(e)}'.")
            raise e

        return success

    def _drop_matches_table(self) -> bool:
        """Drops matches table so it can be created fresh.

        Returns
        -------
        success : bool
        """
        if not self._is_connected():
            raise TypeError("Database is not connected.")

        drop_table_sql = """ DROP TABLE IF EXISTS matches; """

        try:
            c = self.__conn.cursor()
            c.execute(drop_table_sql)
            self.__conn.commit()
            success = True
        except Error as e:
            self.__log.error(f"Unable to run 'drop_matches_table' because '{str(e)}'.")
            raise e

        return success

    def _insert_report(self, df: pandas.DataFrame = None) -> bool:
        """Inserts the report's DataFrame as a row in the database.

        Parameters
        ----------
        df : pandas.DataFrame

        Returns
        -------
        success : bool
        """
        if df is None or not isinstance(df, pandas.DataFrame):
            self.__log.error("Input 'df' is not a pandas.DataFrame.")
            raise TypeError("Input 'df' is not a pandas.DataFrame.")

        if not self._is_connected():
            self.__log.error("Called '_insert_report' method but database is not connected.")
            return False

        fields_list = ['MRN', 'FIRST', 'LAST', 'DOB', 'ADDR_CALCULATED', 'PHONE_CALCULATED']
        all_fields_list = []

        #   Ensure all expected fields are present.
        for field in fields_list:
            epic_field = "EPIC_" + field
            all_fields_list.append(epic_field.lower())

            if epic_field not in df.columns:
                df[epic_field] = None

            redcap_field = "REDCAP_" + field
            all_fields_list.append(redcap_field.lower())

            if redcap_field not in df.columns:
                df[redcap_field] = None

        if 'crc_decision' not in df.columns:
            df['crc_decision'] = 'CrcReview.NOT_SURE'

        all_fields_list.append('crc_decision')
        all_fields_string = ','.join(all_fields_list)
        insert_sql = " INSERT INTO matches(" +\
                     all_fields_string +\
                     ") VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?); "
        cur = self.__conn.cursor()

        for index in range(len(df)):
            crc_decision_code = self._translate_crc_decision(df['crc_decision'][index])
            values_list = [df['EPIC_MRN'][index],
                           df['REDCAP_MRN'][index],
                           df['EPIC_FIRST'][index],
                           df['REDCAP_FIRST'][index],
                           df['EPIC_LAST'][index],
                           df['REDCAP_LAST'][index],
                           df['EPIC_DOB'][index],
                           df['REDCAP_DOB'][index],
                           df['EPIC_ADDR_CALCULATED'][index],
                           df['REDCAP_ADDR_CALCULATED'][index],
                           df['EPIC_PHONE_CALCULATED'][index],
                           df['REDCAP_PHONE_CALCULATED'][index],
                           str(crc_decision_code)]

            try:
                cur.execute(insert_sql, values_list)
                self.__conn.commit()
            except Error as e:
                self.__log.error(f"Error in running table insert method because '{str(e)}'.")
                raise e

        return True

    def _is_connected(self) -> bool:
        """Tests to ensure we've already created the '.__conn' property.

        Returns
        -------
        success : bool
        """
        return self.__conn is not None and isinstance(self.__conn, Connection)

    def read_reports(self, import_folder: str = None) -> bool:
        """Read all the report files & imports into db.

        Parameters
        ----------
        import_folder : str

        Returns
        -------
        success : bool
        """
        # Create Reader object.
        self.__redcap_reader = REDCapReportReader()

        if not self._reader_ready():
            self.__log.error("Unable to create REDCapReportReader object.")
            raise RuntimeError("Unable to create REDCapReportReader object.")

        reports_directory = os.path.join(import_folder, '*_patient_report.txt')

        for file in glob.glob(reports_directory):
            df = self.__redcap_reader.read(report_filename=file)

            if df is None or not isinstance(df, pandas.DataFrame):
                self.__log.error(f"Unable to read '{file}'.")
                raise TypeError(f"Unable to read '{file}'.")

            insert_success = self._insert_report(df)

            if not insert_success:
                self.__log.error(f"Unable to insert into db.")
                raise RuntimeError(f"Unable to insert into db.")

        return True

    def _reader_ready(self) -> None:
        """Tests to see if REDCapReportReader object was properly instantiated.

        Returns
        -------
        ready : bool
        """
        return self.__redcap_reader is not None and isinstance(self.__redcap_reader, REDCapReportReader)

    def setup(self, db_filename: str = "temp_matches_database.db") -> bool:
        """Initializes database by:
            1) Creating connection
            2) Creating & populating the decisions table.
            3) Creating the matches table.

        Parameters
        ----------
        db_filename : str Name of file to be created.

        Returns
        -------
        success : boolean

        """
        return self._create_connection() and self._build_decision_table() and self._create_matches_table()

    def _translate_crc_decision(self, crc_enum: str) -> int:
        """ Converts CrcReview object into integer, using 'decisions' table.

        Returns
        -------
        id : int
        """

        if not self._is_connected():
            self.__log.error("Called '_insert_report' method but database is not connected.")
            return False

        if crc_enum is None or not isinstance(crc_enum, str):
            self.__log.error('Input "crc_review" is not a string')
            raise TypeError('Input "crc_review" is not a string.')

        #   Strip off the 'CrcReview.' part.
        crc_enum_payload = crc_enum.replace('CrcReview.', '')
        query_sql = " SELECT id FROM decisions WHERE decision = (?); "
        cur = self.__conn.cursor()

        try:
            cur.execute(query_sql, [crc_enum_payload])
            rows = cur.fetchall()
            return rows[0][0]
        except Error as e:
            self.__log.error(f"Error in running 'decisions' table query because '{str(e)}'.")
            raise e
