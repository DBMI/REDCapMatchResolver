"""
Module: contains class REDCapMatchResolver
used to create/use a SQLite database from
CRC-reviewed match reports.
"""
import glob
import os
import sqlite3
from sqlite3 import Connection
from typing import Union

import pandas  # type: ignore[import]
from redcaputilities.directories import ensure_output_path_exists
from redcaputilities.logging import setup_logging

from .redcap_report_reader import CrcReview, REDCapReportReader


class REDCapMatchResolver:
    """
    Creates a SQLite database from stacks of match reports reviewed by CRCs.
    Allows other code to ask "has this match already been reviewed?" so that
    we're not asking the CRCs about the same patients over and over.
    """

    def __init__(self, db_filename: str = "temp_matches_database.db"):
        self.__log = setup_logging(log_filename="redcap_match_resolver.log")
        self.__database_fields_list = []  # type: ignore[var-annotated]
        self.__dataframe_fields_list = []  # type: ignore[var-annotated]
        self.__redcap_reader = REDCapReportReader()

        self._build_required_fields()
        self.__conn = self._setup_db(db_filename=db_filename)

    def _build_required_fields(self) -> None:
        fields_list = [
            "MRN",
            "FIRST",
            "LAST",
            "DOB",
            "ADDR_CALCULATED",
            "PHONE_CALCULATED",
        ]

        #   Ensure all expected fields are present.
        for field in fields_list:
            epic_field = "EPIC_" + field
            self.__database_fields_list.append(epic_field.lower())
            self.__dataframe_fields_list.append(epic_field)

            redcap_field = "REDCAP_" + field
            self.__database_fields_list.append(redcap_field.lower())
            self.__dataframe_fields_list.append(redcap_field)

        self.__database_fields_list.append("crc_decision")
        self.__dataframe_fields_list.append("CRC_DECISION")

    def _build_decision_table(self, conn: sqlite3.Connection) -> bool:
        """Creates & populates table that translates

        Returns
        -------
        success : bool
        """
        if not isinstance(conn, sqlite3.Connection):
            raise TypeError("Argument 'conn' is not a sqlite3.Connection object.")

        if not self._create_decisions_table(conn):  # pragma: no cover
            self.__log.error("Unable to create 'decisions' table.")
            raise RuntimeError("Unable to create 'decisions' table.")

        cur = conn.cursor()

        #   We want these values to exactly equal those in the CrcReview enum class.
        insert_sql = """INSERT INTO decisions(decision) VALUES('MATCH')"""
        cur.execute(insert_sql)
        insert_sql = """INSERT INTO decisions(decision) VALUES('NO_MATCH')"""
        cur.execute(insert_sql)
        insert_sql = """INSERT INTO decisions(decision) VALUES('NOT_SURE')"""
        cur.execute(insert_sql)
        conn.commit()
        return True

    def _create_connection(self, db_filename: str) -> sqlite3.Connection:
        """Initializes a SQLite database at the desired location.

        Parameters
        ----------
        db_filename : str Name of file to be created.

        Returns
        -------
        connection : sqlite3.Connection object
        """

        if (
            not isinstance(db_filename, str) or len(db_filename) == 0
        ):  # pragma: no cover
            self.__log.error("Input 'db_filename' is not the expected string.")
            raise TypeError("Input 'db_filename' is not the expected string.")

        ensure_output_path_exists(db_filename)

        # pylint: disable=logging-fstring-interpolation
        try:
            conn = sqlite3.connect(db_filename)

            if not isinstance(conn, sqlite3.Connection):
                self.__log.error(
                    "Unable to establish connection to {db_filename}.",
                    extra={"db_filename": db_filename},
                )
                raise RuntimeError(
                    f"Unable to establish connection to '{db_filename}'."
                )
        except sqlite3.Error as database_error:  # pragma: no cover
            self.__log.exception(
                "Unable to open file {db_filename} because {database_error}.",
                extra={
                    "db_filename": db_filename,
                },
            )
            raise database_error

        return conn

    def _create_decisions_table(
        self, conn: Union[sqlite3.Connection, None] = None
    ) -> bool:
        """Creates the table that translates integer codes to text like 'Same' or 'Not Same'.

        Returns
        -------
        success : bool
        """
        if not isinstance(conn, sqlite3.Connection):
            raise TypeError("Argument 'conn' is not a sqlite3.Connection object.")

        if not self._is_connected(conn=conn):  # pragma: no cover
            self.__log.error(
                "Called '_create_decisions_table' method but database is not connected."
            )
            raise RuntimeError(
                "Called '_create_decisions_table' method but database is not connected."
            )

        if not self._drop_decisions_table(conn=conn):  # pragma: no cover
            self.__log.error('Unable to drop "decisions" table.')
            raise RuntimeError('Unable to drop "decisions" table.')

        create_table_sql = """ CREATE TABLE IF NOT EXISTS decisions (
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    decision text NOT NULL
                                );"""

        # pylint: disable=logging-fstring-interpolation
        try:
            database_cursor = conn.cursor()
            database_cursor.execute(create_table_sql)
            conn.commit()
            success = True
        except sqlite3.Error as database_error:  # pragma: no cover
            self.__log.exception(
                "Unable to run 'create_table_sql' because {database_error}."
            )
            raise database_error

        return success

    def _create_matches_table(self, conn: sqlite3.Connection) -> bool:
        """Creates an empty 'matches' table in the database.

        Returns
        -------
        success : bool
        """

        if not isinstance(conn, sqlite3.Connection):
            raise TypeError("Argument 'conn' is not a sqlite3.Connection object.")

        if not self._is_connected(conn=conn):  # pragma: no cover
            self.__log.error(
                "Called '_create_matches_table' method but database is not connected."
            )
            raise RuntimeError(
                "Called '_create_matches_table' method but database is not connected."
            )

        if not self._drop_matches_table(conn=conn):  # pragma: no cover
            self.__log.error('Unable to drop "matches" table.')
            raise RuntimeError('Unable to drop "matches" table.')

        create_table_sql = """ CREATE TABLE IF NOT EXISTS matches (
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    epic_mrn integer NOT NULL,
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

        # pylint: disable=logging-fstring-interpolation
        try:
            database_cursor = conn.cursor()
            database_cursor.execute(create_table_sql)
            conn.commit()
            success = True
        except sqlite3.Error as database_error:  # pragma: no cover
            self.__log.exception(
                "Unable to run 'create_table_sql' because {database_error}."
            )
            raise database_error

        return success

    def _drop_decisions_table(self, conn: sqlite3.Connection) -> bool:
        """Drops decisions table so it can be created fresh.

        Returns
        -------
        success : bool
        """
        if not isinstance(conn, sqlite3.Connection):
            raise TypeError("Argument 'conn' is not a sqlite3.Connection object.")

        if not self._is_connected(conn=conn):  # pragma: no cover
            self.__log.error(
                "Called '_drop_decisions_table' method but database is not connected."
            )
            raise RuntimeError(
                "Called 'drop_decisions_table' method but database is not connected."
            )

        drop_table_sql = """ DROP TABLE IF EXISTS decisions; """

        # pylint: disable=logging-fstring-interpolation
        try:
            database_cursor = conn.cursor()
            database_cursor.execute(drop_table_sql)
            conn.commit()
            success = True
        except sqlite3.Error as database_error:  # pragma: no cover
            self.__log.exception(
                "Unable to run 'drop_decisions_table' because {database_error}."
            )
            raise database_error

        return success

    def _drop_matches_table(self, conn: sqlite3.Connection) -> bool:
        """Drops matches table so it can be created fresh.

        Returns
        -------
        success : bool
        """
        if not isinstance(conn, sqlite3.Connection):
            raise TypeError("Argument 'conn' is not a sqlite3.Connection object.")

        if not self._is_connected(conn=conn):  # pragma: no cover
            self.__log.error(
                "Called '_drop_matches_table' method but database is not connected."
            )
            raise RuntimeError(
                "Called '_drop_matches_table' method but database is not connected."
            )

        drop_table_sql = """ DROP TABLE IF EXISTS matches; """

        # pylint: disable=logging-fstring-interpolation
        try:
            database_cursor = conn.cursor()
            database_cursor.execute(drop_table_sql)
            conn.commit()
            success = True
        except sqlite3.Error as database_error:  # pragma: no cover
            self.__log.exception(
                "Unable to run 'drop_matches_table' because {database_error}."
            )
            raise database_error

        return success

    def _insert_report(self, report_df: pandas.DataFrame = None) -> bool:
        """Inserts the report's DataFrame as a row in the database.

        Parameters
        ----------
        report_df : pandas.DataFrame

        Returns
        -------
        success : bool
        """
        if not isinstance(report_df, pandas.DataFrame):  # pragma: no cover
            self.__log.error("Input 'df' is not a pandas.DataFrame.")
            raise TypeError("Input 'df' is not a pandas.DataFrame.")

        if not self._is_connected(conn=None):  # pragma: no cover
            self.__log.error(
                "Called '_insert_report' method but database is not connected."
            )
            raise RuntimeError(
                "Called '_insert_report' method but database is not connected."
            )

        #   Ensure all expected fields are present.
        for field in self.__dataframe_fields_list:
            if field not in report_df.columns:
                report_df[field] = None

        all_database_fields_string = ",".join(self.__database_fields_list)
        insert_sql = (
            " INSERT INTO matches("
            + all_database_fields_string
            + ") VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?); "
        )
        cur = self.__conn.cursor()

        for index in range(len(report_df)):
            values_list = []

            for dataframe_field in [
                name for name in self.__dataframe_fields_list if name != "CRC_DECISION"
            ]:
                values_list.append(report_df[dataframe_field][index])

            if (
                "CRC_DECISION" not in report_df.columns
                or report_df["CRC_DECISION"] is None
                or report_df["CRC_DECISION"][index] is None
                or report_df["CRC_DECISION"][index] == "None"
            ):
                #   Then there's no point in inserting this row into the database.
                continue

            crc_decision_string = report_df["CRC_DECISION"][index]
            crc_decision_code = self._translate_crc_decision(crc_decision_string)
            values_list.append(str(crc_decision_code))

            # pylint: disable=logging-fstring-interpolation
            try:
                cur.execute(insert_sql, values_list)
                self.__conn.commit()
            except sqlite3.Error as database_error:  # pragma: no cover
                self.__log.exception(
                    "Error in running table insert method because {database_error}."
                )
                raise database_error

        return True

    def _is_connected(self, conn: Union[sqlite3.Connection, None] = None) -> bool:
        """Tests to ensure we've already created the '.__conn' property.

        Returns
        -------
        success : bool
        """
        if not isinstance(conn, sqlite3.Connection):
            conn = self.__conn

        return conn is not None and isinstance(conn, Connection)

    def lookup_potential_match(self, match_block: str) -> CrcReview:
        """Lookup this potential match in the database.
           Have CRCs already reviewed this pair?

        Parameters
        ----------
        match_block : str   Multi-line block of text giving both REDCap and Epic patient info.

        Returns
        -------
        decision : CrcReview Reports whether CRCs said match, no match (or not sure).
        """
        if not self._is_connected(conn=None):  # pragma: no cover
            self.__log.error(
                "Called 'lookup_potential_match' method but database is not connected."
            )
            raise RuntimeError(
                "Called 'lookup_potential_match' method but database is not connected."
            )

        if not isinstance(match_block, str) or len(match_block) == 0:
            self.__log.error("Input 'match_block' is not the expected str.")
            raise TypeError("Input 'match_block' is not the expected str.")

        if not self._reader_ready():  # pragma: no cover
            self.__log.error("REDCapReader object isn't ready.")
            raise RuntimeError("REDCapReader object isn't ready.")

        match_df = self.__redcap_reader.read_text(block_txt=match_block)

        if not isinstance(match_df, pandas.DataFrame):  # pragma: no cover
            self.__log.error("Unable to read text block.")
            raise RuntimeError("Unable to read text block.")

        if not all(item in match_df.columns for item in self.__dataframe_fields_list):
            self.__log.error("Text block does not contain required fields.")
            raise RuntimeError("Text block does not contain required fields.")

        # pylint: disable=line-too-long
        query_sql = (
            "SELECT decision FROM matches "
            + "JOIN decisions on matches.crc_decision = decisions.id"
            + " WHERE"
            + " matches.epic_mrn = ?"
            + " AND matches.redcap_mrn = ?"
            + " AND matches.epic_first = ?"
            + " AND matches.redcap_first = ?"
            + " AND matches.epic_last = ?"
            + " AND matches.redcap_last = ?"
            + " AND (matches.epic_dob = ? OR matches.epic_dob ISNULL)"
            + " AND (matches.redcap_dob = ? OR matches.redcap_dob ISNULL)"
            + " AND (matches.epic_addr_calculated = ? OR matches.epic_addr_calculated IS NULL)"
            + " AND (matches.redcap_addr_calculated = ? OR matches.redcap_addr_calculated IS NULL)"
            + " AND (matches.epic_phone_calculated = ? OR matches.epic_phone_calculated IS NULL)"
            + " AND (matches.redcap_phone_calculated = ? OR matches.redcap_phone_calculated IS NULL);"
        )
        cur = self.__conn.cursor()

        for index in range(len(match_df)):
            values_list = [
                match_df["EPIC_MRN"][index],
                match_df["REDCAP_MRN"][index],
                match_df["EPIC_FIRST"][index],
                match_df["REDCAP_FIRST"][index],
                match_df["EPIC_LAST"][index],
                match_df["REDCAP_LAST"][index],
                match_df["EPIC_DOB"][index],
                match_df["REDCAP_DOB"][index],
                match_df["EPIC_ADDR_CALCULATED"][index],
                match_df["REDCAP_ADDR_CALCULATED"][index],
                match_df["EPIC_PHONE_CALCULATED"][index],
                match_df["REDCAP_PHONE_CALCULATED"][index],
            ]

            # pylint: disable=logging-fstring-interpolation
            try:
                cur.execute(query_sql, values_list)
                rows = cur.fetchall()

                if rows:
                    #   We allow for multiple hits from the database.
                    #   If any of them report MATCH, we'll go with that.
                    crc_review_objects = (
                        CrcReview.convert(r) for r in rows if r is not None
                    )
                    return CrcReview(max(crc_review_objects))

                return CrcReview(CrcReview.NOT_SURE)
            except sqlite3.Error as database_error:  # pragma: no cover
                self.__log.exception(
                    "Error in running table query method because {database_error}."
                )
                raise database_error

        return CrcReview(CrcReview.NOT_SURE)

    def read_reports(self, import_folder: str) -> bool:
        """Read all the report files & imports into db.

        Parameters
        ----------
        import_folder : str

        Returns
        -------
        success : bool
        """
        if not self._reader_ready():  # pragma: no cover
            self.__log.error("Unable to create REDCapReportReader object.")
            raise RuntimeError("Unable to create REDCapReportReader object.")

        if not isinstance(import_folder, str) or len(import_folder) == 0:
            raise TypeError("Argument 'import_folder' is not the expected string.")

        reports_directory = os.path.join(import_folder, "*_patient_report.txt")

        for file in glob.glob(reports_directory):
            report_df = self.__redcap_reader.read_file(report_filename=file)

            # pylint: disable=logging-fstring-interpolation
            if not isinstance(report_df, pandas.DataFrame):  # pragma: no cover
                self.__log.error(
                    "Unable to read {report_file}.", extra={"report_file": file}
                )
                raise TypeError(f"Unable to read '{file}'.")

            insert_success = self._insert_report(report_df)

            if not insert_success:  # pragma: no cover
                self.__log.error("Unable to insert into db.")
                raise RuntimeError("Unable to insert into db.")

        return True

    def _reader_ready(self) -> bool:
        """Tests to see if REDCapReportReader object was properly instantiated.

        Returns
        -------
        ready : bool
        """
        return self.__redcap_reader is not None and isinstance(
            self.__redcap_reader, REDCapReportReader
        )

    def _setup_db(self, db_filename: str) -> sqlite3.Connection:
        """Initializes database by:
            1) Creating connection
            2) Creating & populating the decisions table.
            3) Creating the matches table.

        Parameters
        ----------
        db_filename : str Name of file to be created.

        Returns
        -------
        connection : sqlite3.Connection object

        """
        if not isinstance(db_filename, str) or len(db_filename) == 0:
            raise TypeError("Input 'db_filename' is not the expected string.")

        connection = self._create_connection(db_filename=db_filename)

        if not self._build_decision_table(connection) or not self._create_matches_table(
            connection
        ):
            self.__log.error(
                "Unable to establish connection to {db_filename}.",
                extra={"db_filename": db_filename},
            )
            raise RuntimeError(f"Unable to establish connection to '{db_filename}'.")

        return connection

    def _translate_crc_decision(self, crc_enum: str) -> int:
        """Converts CrcReview string into integer, using 'decisions' table.

        Returns
        -------
        id : int
        """

        if not self._is_connected():  # pragma: no cover
            self.__log.error(
                "Called '_translate_crc_decision' method but database is not connected."
            )
            raise RuntimeError(
                "Called '_translate_crc_decision' method but database is not connected."
            )

        if not isinstance(crc_enum, str) or len(crc_enum) == 0:  # pragma: no cover
            self.__log.error('Input "crc_review" is not a string')
            raise TypeError('Input "crc_review" is not a string.')

        #   Strip off the 'CrcReview.' part.
        crc_enum_payload = crc_enum.replace("CrcReview.", "")
        query_sql = " SELECT id FROM decisions WHERE decision = (?); "
        cur = self.__conn.cursor()

        # pylint: disable=logging-fstring-interpolation
        try:
            cur.execute(query_sql, [crc_enum_payload])
            rows = cur.fetchall()
            return int(rows[0][0])
        except sqlite3.Error as database_error:  # pragma: no cover
            self.__log.exception(
                "Error in running 'decisions' table query because {database_error}."
            )
            raise database_error
