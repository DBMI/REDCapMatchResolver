"""
Module: contains class REDCapMatchResolver
used to create/use a SQLite database from
CRC-reviewed match reports.
"""
import glob
import logging
import os
import sqlite3
from sqlite3 import Connection
import pandas
from .utilities import Utilities
from .redcap_report_reader import CrcReview, REDCapReportReader


class REDCapMatchResolver:
    """
    Creates a SQLite database from stacks of match reports reviewed by CRCs.
    Allows other code to ask "has this match already been reviewed?" so that
    we're not asking the CRCs about the same patients over and over.
    """

    def __init__(self, db_filename: str = "temp_matches_database.db"):
        Utilities.setup_logging()
        self.__log = logging.getLogger(__name__)
        self.__conn = None
        self.__database_fields_list = []
        self.__dataframe_fields_list = []
        self.__redcap_reader = REDCapReportReader()

        self._build_required_fields()
        self._setup_db(db_filename=db_filename)

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

    def _build_decision_table(self) -> bool:
        """Creates & populates table that translates

        Returns
        -------
        success : bool
        """
        if not self._create_decisions_table():  # pragma: no cover
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

    def _create_connection(self, db_filename: str = None) -> bool:
        """Initializes a SQLite database at the desired location.

        Parameters
        ----------
        db_filename : str Name of file to be created.

        Returns
        -------
        success : boolean
        """

        if db_filename is None or not isinstance(db_filename, str):  # pragma: no cover
            self.__log.error("Input 'db_filename' is not the expected string.")
            raise TypeError("Input 'db_filename' is not the expected string.")

        Utilities.ensure_output_path(db_filename)

        # pylint: disable=logging-fstring-interpolation
        try:
            self.__conn = sqlite3.connect(db_filename)
            success = self.__conn is not None and isinstance(self.__conn, Connection)
        except sqlite3.Error as database_error:  # pragma: no cover
            self.__log.error(
                f"Unable to open file '{db_filename}'"
                + f" because '{str(database_error)}'."
            )
            raise database_error

        return success

    def _create_decisions_table(self) -> bool:
        """Creates the table that translates integer codes to text like 'Same' or 'Not Same'.

        Returns
        -------
        success : bool
        """
        if not self._is_connected():  # pragma: no cover
            self.__log.error(
                "Called '_create_decisions_table' method but database is not connected."
            )
            raise RuntimeError(
                "Called '_create_decisions_table' method but database is not connected."
            )

        if not self._drop_decisions_table():  # pragma: no cover
            self.__log.error('Unable to drop "decisions" table.')
            raise RuntimeError('Unable to drop "decisions" table.')

        create_table_sql = """ CREATE TABLE IF NOT EXISTS decisions (
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    decision text NOT NULL
                                );"""

        # pylint: disable=logging-fstring-interpolation
        try:
            database_cursor = self.__conn.cursor()
            database_cursor.execute(create_table_sql)
            self.__conn.commit()
            success = True
        except sqlite3.Error as database_error:  # pragma: no cover
            self.__log.error(
                f"Unable to run 'create_table_sql' because '{str(database_error)}'."
            )
            raise

        return success

    def _create_matches_table(self) -> bool:
        """Creates an empty 'matches' table in the database.

        Returns
        -------
        success : bool
        """
        if not self._is_connected():  # pragma: no cover
            self.__log.error(
                "Called '_create_matches_table' method but database is not connected."
            )
            raise RuntimeError(
                "Called '_create_matches_table' method but database is not connected."
            )

        if not self._drop_matches_table():  # pragma: no cover
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
            database_cursor = self.__conn.cursor()
            database_cursor.execute(create_table_sql)
            self.__conn.commit()
            success = True
        except sqlite3.Error as database_error:  # pragma: no cover
            self.__log.error(
                f"Unable to run 'create_table_sql' because '{str(database_error)}'."
            )
            raise database_error

        return success

    def _drop_decisions_table(self) -> bool:
        """Drops decisions table so it can be created fresh.

        Returns
        -------
        success : bool
        """
        if not self._is_connected():  # pragma: no cover
            self.__log.error(
                "Called '_drop_decisions_table' method but database is not connected."
            )
            raise RuntimeError(
                "Called 'drop_decisions_table' method but database is not connected."
            )

        drop_table_sql = """ DROP TABLE IF EXISTS decisions; """

        # pylint: disable=logging-fstring-interpolation
        try:
            database_cursor = self.__conn.cursor()
            database_cursor.execute(drop_table_sql)
            self.__conn.commit()
            success = True
        except sqlite3.Error as database_error:  # pragma: no cover
            self.__log.error(
                f"Unable to run 'drop_decisions_table' because '{str(database_error)}'."
            )
            raise database_error

        return success

    def _drop_matches_table(self) -> bool:
        """Drops matches table so it can be created fresh.

        Returns
        -------
        success : bool
        """
        if not self._is_connected():  # pragma: no cover
            self.__log.error(
                "Called '_drop_matches_table' method but database is not connected."
            )
            raise RuntimeError(
                "Called '_drop_matches_table' method but database is not connected."
            )

        drop_table_sql = """ DROP TABLE IF EXISTS matches; """

        # pylint: disable=logging-fstring-interpolation
        try:
            database_cursor = self.__conn.cursor()
            database_cursor.execute(drop_table_sql)
            self.__conn.commit()
            success = True
        except sqlite3.Error as database_error:  # pragma: no cover
            self.__log.error(
                f"Unable to run 'drop_matches_table' because '{str(database_error)}'."
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
        if report_df is None or not isinstance(
            report_df, pandas.DataFrame
        ):  # pragma: no cover
            self.__log.error("Input 'df' is not a pandas.DataFrame.")
            raise TypeError("Input 'df' is not a pandas.DataFrame.")

        if not self._is_connected():  # pragma: no cover
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
                self.__log.error(
                    f"Error in running table insert method because '{str(database_error)}'."
                )
                raise database_error

        return True

    def _is_connected(self) -> bool:
        """Tests to ensure we've already created the '.__conn' property.

        Returns
        -------
        success : bool
        """
        return self.__conn is not None and isinstance(self.__conn, Connection)

    def lookup_potential_match(self, match_block: str = None) -> CrcReview:
        """Lookup this potential match in the database.
           Have CRCs already reviewed this pair?

        Parameters
        ----------
        match_block : str   Multi-line block of text giving both REDCap and Epic patient info.

        Returns
        -------
        decision : CrcReview Reports whether CRCs said match, no match (or not sure).
        """
        if not self._is_connected():  # pragma: no cover
            self.__log.error(
                "Called 'lookup_potential_match' method but database is not connected."
            )
            raise RuntimeError(
                "Called 'lookup_potential_match' method but database is not connected."
            )

        if match_block is None or not isinstance(match_block, str):
            self.__log.error("Input 'match_block' is not the expected str.")
            raise TypeError("Input 'match_block' is not the expected str.")

        if not self._reader_ready():  # pragma: no cover
            self.__log.error("REDCapReader object isn't ready.")
            raise RuntimeError("REDCapReader object isn't ready.")

        match_df = self.__redcap_reader.read_text(block_txt=match_block)

        if match_df is None or not isinstance(
            match_df, pandas.DataFrame
        ):  # pragma: no cover
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
                    return max(CrcReview.convert(rows))

                return CrcReview.NOT_SURE
            except sqlite3.Error as database_error:  # pragma: no cover
                self.__log.error(
                    f"Error in running table query method because '{str(database_error)}'."
                )
                raise database_error

    def read_reports(self, import_folder: str = None) -> bool:
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

        reports_directory = os.path.join(import_folder, "*_patient_report.txt")

        for file in glob.glob(reports_directory):
            report_df = self.__redcap_reader.read_file(report_filename=file)

            # pylint: disable=logging-fstring-interpolation
            if report_df is None or not isinstance(
                report_df, pandas.DataFrame
            ):  # pragma: no cover
                self.__log.error(f"Unable to read '{file}'.")
                raise TypeError(f"Unable to read '{file}'.")

            insert_success = self._insert_report(report_df)

            if not insert_success:  # pragma: no cover
                self.__log.error("Unable to insert into db.")
                raise RuntimeError("Unable to insert into db.")

        return True

    def _reader_ready(self) -> None:
        """Tests to see if REDCapReportReader object was properly instantiated.

        Returns
        -------
        ready : bool
        """
        return self.__redcap_reader is not None and isinstance(
            self.__redcap_reader, REDCapReportReader
        )

    def _setup_db(self, db_filename: str = None) -> bool:
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
        return (
            self._create_connection(db_filename=db_filename)
            and self._build_decision_table()
            and self._create_matches_table()
        )

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

        if crc_enum is None or not isinstance(crc_enum, str):  # pragma: no cover
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
            return rows[0][0]
        except sqlite3.Error as database_error:  # pragma: no cover
            self.__log.error(
                f"Error in running 'decisions' table query because '{str(database_error)}'."
            )
            raise database_error