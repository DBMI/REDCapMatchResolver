"""
Module: contains class REDCapMatchResolver
used to create/use a SQLite database from
human-reviewed match reports.
"""

import glob
import os
import sqlite3
from datetime import datetime
from itertools import repeat
from logging import Logger
from sqlite3 import Connection

import pandas  # type: ignore[import]
from redcaputilities.directories import ensure_output_path_exists
from redcaputilities.logging import patient_data_directory

from redcapmatchresolver.redcap_report_reader import DecisionReview, REDCapReportReader
from redcapmatchresolver.redcap_report_writer import REDCapReportWriter


class REDCapMatchResolver:
    """
    Creates a SQLite database from stacks of human-reviewed match reports.
    Allows other code to ask "has this match already been reviewed?" so that
    we're not asking reviewers about the same patients over and over.
    """

    def __init__(self, log: Logger, connection: sqlite3.Connection = None):
        self.__log: Logger = log

        self.__database_fields_list: list = []  # type: ignore[var-annotated]
        self.__dataframe_fields_list: list = []  # type: ignore[var-annotated]
        self.__redcap_reader: REDCapReportReader = REDCapReportReader()
        self.__redcap_writer: REDCapReportWriter = REDCapReportWriter()

        self.__build_required_fields()
        self.__connection: sqlite3.Connection

        if isinstance(connection, sqlite3.Connection):
            self.__connection = connection
        else:
            #   Create our own.
            db_filename = os.path.join(
                patient_data_directory(), "redcap", "temp_matches_database.db"
            )

            self.__connection: sqlite3.Connection = self.__create_connection(
                db_filename=db_filename
            )

        # Now create the required tables.
        if (
            not self.__init_decisions_table() or not self.__init_matches_table()
        ):  # pragma: no cover
            self.__log.error("Unable to build required database tables.")
            raise RuntimeError("Unable to build required database tables.")

    def add_possible_wobbler(self, match_summary: str) -> bool:
        """Allows external code to tell us to add this object as a wobbler--if it qualifies.

        Parameters
        ----------
        match_summary : str

        Returns
        -------
        success : bool
        """
        previous_decision: DecisionReview = self.lookup_potential_match(match_summary)

        if previous_decision == DecisionReview.NOT_SURE:
            #  Then it's NOT already in our database, so request a review.
            self.__redcap_writer.add_match(match_summary)

        return True

    def __build_required_fields(self) -> None:
        #   Ensure all expected fields are present.
        self.__database_fields_list.append("PAT_ID")
        self.__dataframe_fields_list.append("PAT_ID")

        self.__database_fields_list.append("study_id")
        self.__dataframe_fields_list.append("study_id")

        #   Tack on the decision.
        self.__database_fields_list.append("decision_code")
        self.__dataframe_fields_list.append("DECISION")

    def __create_connection(self, db_filename: str) -> sqlite3.Connection:
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
            connection = sqlite3.connect(db_filename)

            if not isinstance(connection, sqlite3.Connection):  # pragma: no cover
                self.__log.error(
                    "Unable to establish connection to {db_filename}.",
                    extra={"db_filename": db_filename},
                )
                raise RuntimeError(
                    f"Unable to establish connection to '{db_filename}'."
                )
        except (
            sqlite3.IntegrityError,
            sqlite3.InternalError,
        ) as database_error:  # pragma: no cover
            self.__log.exception(
                "Unable to open file {db_filename} because {database_error}.",
                extra={"db_filename": db_filename, "database_error": database_error},
            )
            raise database_error

        return connection

    def __create_decisions_table(self) -> bool:
        """Creates the table that translates integer codes to text like 'Same' or 'Not Same'.

        Returns
        -------
        success : bool
        """

        if not self.__is_connected():  # pragma: no cover
            self.__log.error(
                "Called '__create_decisions_table' method but database is not connected."
            )
            raise RuntimeError(
                "Called '__create_decisions_table' method but database is not connected."
            )

        if not self.__drop_decisions_table():  # pragma: no cover
            self.__log.error('Unable to drop "decisions" table.')
            raise RuntimeError('Unable to drop "decisions" table.')

        create_table_sql = """ CREATE TABLE IF NOT EXISTS decisions (
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    decision text NOT NULL,
                                    score integer);"""

        # pylint: disable=logging-fstring-interpolation
        try:
            database_cursor: sqlite3.Cursor = self.__connection.cursor()
            database_cursor.execute(create_table_sql)
            self.__connection.commit()
            success: bool = True
        except (
            sqlite3.IntegrityError,
            sqlite3.InternalError,
        ) as database_error:  # pragma: no cover
            self.__log.exception(
                "Unable to run 'create_table_sql' because {database_error}.",
                extra={"database_error": database_error},
            )
            raise database_error

        return success

    def __drop_decisions_table(self) -> bool:
        """Drops decisions table so it can be created fresh.

        Returns
        -------
        success : bool
        """
        if not self.__is_connected():  # pragma: no cover
            self.__log.error(
                "Called '__drop_decisions_table' method but database is not connected."
            )
            raise RuntimeError(
                "Called 'drop_decisions_table' method but database is not connected."
            )

        drop_table_sql: str = """ DROP TABLE IF EXISTS decisions; """

        # pylint: disable=logging-fstring-interpolation
        try:
            database_cursor: sqlite3.Cursor = self.__connection.cursor()
            database_cursor.execute(drop_table_sql)
            self.__connection.commit()
            success: bool = True
        except (
            sqlite3.IntegrityError,
            sqlite3.InternalError,
        ) as database_error:  # pragma: no cover
            self.__log.exception(
                "Unable to run 'drop_decisions_table' because {database_error}.",
                extra={"database_error": database_error},
            )
            raise database_error

        return success

    def __drop_matches_table(self) -> bool:
        """Drops matches table so it can be created fresh.

        Returns
        -------
        success : bool
        """
        if not self.__is_connected():  # pragma: no cover
            self.__log.error(
                "Called '__drop_matches_table' method but database is not connected."
            )
            raise RuntimeError(
                "Called '__drop_matches_table' method but database is not connected."
            )

        drop_table_sql = """ DROP TABLE IF EXISTS matches; """

        # pylint: disable=logging-fstring-interpolation
        try:
            database_cursor: sqlite3.Cursor = self.__connection.cursor()
            database_cursor.execute(drop_table_sql)
            self.__connection.commit()
            success: bool = True
        except (
            sqlite3.IntegrityError,
            sqlite3.InternalError,
        ) as database_error:  # pragma: no cover
            self.__log.exception(
                "Unable to run 'drop_matches_table' because {database_error}.",
                extra={"database_error": database_error},
            )
            raise database_error

        return success

    def __init_decisions_table(self) -> bool:
        """Creates & populates table that translates integer codes to text like 'Same' or 'Not Same'.

        Returns
        -------
        success : bool
        """
        if not self.__create_decisions_table():  # pragma: no cover
            self.__log.error("Unable to create 'decisions' table.")
            raise RuntimeError("Unable to create 'decisions' table.")

        #   We want these values to exactly equal those in the DecisionReview enum class.
        cursor: sqlite3.Cursor = self.__connection.cursor()
        insert_sql = """INSERT INTO decisions(decision, score)
                        VALUES
                            ('MATCH', 10),
                            ('NO_MATCH', 0),
                            ('NOT_SURE', NULL);"""
        cursor.execute(insert_sql)
        self.__connection.commit()
        return True

    def __init_matches_table(self) -> bool:
        """Creates an empty 'matches' table in the database.

        Returns
        -------
        success : bool
        """

        if not self.__is_connected():  # pragma: no cover
            self.__log.error(
                "Called '__init_matches_table' method but database is not connected."
            )
            raise RuntimeError(
                "Called '__init_matches_table' method but database is not connected."
            )

        if not self.__drop_matches_table():  # pragma: no cover
            self.__log.error('Unable to drop "matches" table.')
            raise RuntimeError('Unable to drop "matches" table.')

        create_table_sql: str = """ CREATE TABLE IF NOT EXISTS matches (
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    PAT_ID varchar NOT NULL,
                                    study_id integer NOT NULL,
                                    decision_code int
                                );"""

        # pylint: disable=logging-fstring-interpolation
        try:
            database_cursor: sqlite3.Cursor = self.__connection.cursor()
            database_cursor.execute(create_table_sql)
            self.__connection.commit()
            success = True
        except (
            sqlite3.IntegrityError,
            sqlite3.InternalError,
        ) as database_error:  # pragma: no cover
            self.__log.exception(
                "Unable to run 'create_table_sql' because {database_error}.",
                extra={"database_error": database_error},
            )
            raise database_error

        return success

    def __insert_report(self, report_df: pandas.DataFrame = None) -> None:
        """Inserts the report's DataFrame as a row in the database.

        Parameters
        ----------
        report_df : pandas.DataFrame
        """
        if not isinstance(report_df, pandas.DataFrame):  # pragma: no cover
            self.__log.error("Input 'df' is not a pandas.DataFrame.")
            raise TypeError("Input 'df' is not a pandas.DataFrame.")

        if not self.__is_connected():  # pragma: no cover
            self.__log.error(
                "Called '__insert_report' method but database is not connected."
            )
            raise RuntimeError(
                "Called '__insert_report' method but database is not connected."
            )

        #   Ensure all expected fields are present.
        for field in self.__dataframe_fields_list:
            if field not in report_df.columns:
                report_df[field] = None

        all_database_fields_string: str = ",".join(self.__database_fields_list)
        num_fields: int = len(self.__database_fields_list)
        question_marks_list: list = list(repeat("?", num_fields))
        question_marks: str = ",".join(question_marks_list)
        insert_sql: str = (
            " INSERT INTO matches("
            + all_database_fields_string
            + ") VALUES("
            + question_marks
            + "); "
        )
        cur: sqlite3.Cursor = self.__connection.cursor()

        for index in range(len(report_df)):
            values_list: list = []

            for dataframe_field in [
                name for name in self.__dataframe_fields_list if name != "DECISION"
            ]:
                values_list.append(report_df[dataframe_field][index])

            if (
                "DECISION" not in report_df.columns
                or report_df["DECISION"] is None
                or report_df["DECISION"][index] is None
                or report_df["DECISION"][index] == "None"
            ):
                #   Then there's no point in inserting this row into the database.
                continue

            decision_string: str = report_df["DECISION"][index]
            decision_code = self.__translate_decision(decision_string)
            values_list.append(str(decision_code))

            # pylint: disable=logging-fstring-interpolation
            try:
                cur.execute(insert_sql, values_list)
                self.__connection.commit()
            except (
                sqlite3.IntegrityError,
                sqlite3.InternalError,
            ) as database_error:  # pragma: no cover
                # We won't raise this error, because there could be something
                # wrong with the text report & we don't want to kill the whole process.
                self.__log.exception(
                    "Error in running table insert method because {database_error}.",
                    extra={"database_error": database_error},
                )

    def insert_reviewed_reports(self) -> bool:
        """Insert the human-reviewed matches (from text files read by REDCapMatchResolver)
        into the SQLite3 database's `resolved` table.

        Returns
        -------
        success : bool
        """
        match_result: bool = self.__insert_reviewed_match_reports()
        no_match_result: bool = self.__insert_reviewed_no_match_reports()
        return match_result and no_match_result

    def __insert_reviewed_match_reports(self) -> bool:
        """Insert the human-reviewed matches scored as 'MATCH'
        into the SQLite3 database's `resolved` table.

        Returns
        -------
        success : bool
        """
        sql: str = """
            INSERT INTO resolved (PAT_ID, study_id, score)
                SELECT DISTINCT m.PAT_ID, m.study_id, d.score
                FROM matches m
                LEFT JOIN resolved res
                    ON m.PAT_ID = res.PAT_ID
                   AND m.study_id = res.study_id
                JOIN decisions d
                    ON m.decision_code = d.id
                   AND d.decision = 'MATCH'
                WHERE
                    res.score IS NULL
                 OR res.score < 10;
        """

        self.__log.debug("Inserting human-reviewed matches into resolved table.")

        #   Run query & convert to DataFrame.
        cursor = self.__connection.cursor()
        cursor.execute(sql)
        self.__connection.commit()
        cursor.close()
        return True

    def __insert_reviewed_no_match_reports(self) -> bool:
        """Insert the human-reviewed matches scored as 'NO_MATCH'
        into the SQLite3 database's `resolved` table.

        Returns
        -------
        success : bool
        """
        sql: str = """
            INSERT INTO resolved (PAT_ID, study_id, score)
                SELECT DISTINCT m.PAT_ID, m.study_id, d.score
                FROM matches m
                LEFT JOIN resolved res
                    ON m.PAT_ID = res.PAT_ID
                   AND m.study_id = res.study_id
                JOIN decisions d
                    ON m.decision_code = d.id
                   AND d.decision = 'NO_MATCH'
                WHERE
                    res.score IS NULL
                 OR res.score < 10;
        """

        self.__log.debug("Inserting human-reviewed matches into resolved table.")

        #   Run query & convert to DataFrame.
        cursor = self.__connection.cursor()
        cursor.execute(sql)
        self.__connection.commit()
        cursor.close()
        return True

    def __is_connected(self) -> bool:
        """Tests to ensure we've already created the '.__conn' property.

        Returns
        -------
        success : bool
        """
        return self.__connection is not None and isinstance(
            self.__connection, Connection
        )

    def lookup_potential_match(self, match_block: str) -> DecisionReview:
        """Lookup this potential match in the database.
           Have CRCs already reviewed this pair?

        Parameters
        ----------
        match_block : str   Multi-line block of text giving both REDCap and Epic patient info.

        Returns
        -------
        decision : DecisionReview Reports whether CRCs said match, no match (or not sure).
        """
        if not self.__is_connected():  # pragma: no cover
            self.__log.error(
                "Called 'lookup_potential_match' method but database is not connected."
            )
            raise RuntimeError(
                "Called 'lookup_potential_match' method but database is not connected."
            )

        if not isinstance(match_block, str) or len(match_block) == 0:
            self.__log.error("Input 'match_block' is not the expected str.")
            raise TypeError("Input 'match_block' is not the expected str.")

        if not self.__reader_ready():  # pragma: no cover
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
            + "JOIN decisions on matches.decision_code = decisions.id"
            + " WHERE"
            + " matches.PAT_ID = ?"
            + " AND matches.study_id = ?"
        )
        cur = self.__connection.cursor()

        for index in range(len(match_df)):
            values_list = [
                match_df["PAT_ID"][index],
                match_df["study_id"][index],
            ]

            # pylint: disable=logging-fstring-interpolation
            try:
                cur.execute(query_sql, values_list)
                rows = cur.fetchall()

                if rows:
                    #   We allow for multiple hits from the database.
                    #   If any of them report MATCH, we'll go with that.
                    crc_review_objects = (
                        DecisionReview.convert(r) for r in rows if r is not None
                    )
                    return DecisionReview(max(crc_review_objects))

                return DecisionReview(DecisionReview.NOT_SURE)
            except (
                sqlite3.IntegrityError,
                sqlite3.InternalError,
            ) as database_error:  # pragma: no cover
                self.__log.exception(
                    "Error in running table query method because {database_error}.",
                    extra={"database_error": database_error},
                )
                raise database_error

    def read_reports(self, import_folder: str) -> bool:
        """Read all the report files & imports into db.

        Parameters
        ----------
        import_folder : str

        Returns
        -------
        success : bool
        """
        if not self.__reader_ready():  # pragma: no cover
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

            self.__insert_report(report_df)

        return True

    def __reader_ready(self) -> bool:
        """Tests to see if REDCapReportReader object was properly instantiated.

        Returns
        -------
        ready : bool
        """
        return isinstance(self.__redcap_reader, REDCapReportReader)

    def report_wobblers(self, new_reports_directory: str) -> tuple:
        """Allows external code to request we write a report on whatever wobblers we've identified.

        Parameters
        ----------
        new_reports_directory : str

        Returns
        -------
        package : tuple containing (num_wobblers: int, filename_created: str)
        """

        if not isinstance(new_reports_directory, str):
            raise TypeError("Argument 'new_reports_directory' is not the expected str.")

        num_wobblers: int = self.__redcap_writer.num_reports()
        self.__log.info(f"Number of wobbler cases: {num_wobblers}.")

        now: str = datetime.today().strftime("%Y%m%d_%H%M%S")
        filename: str = os.path.join(new_reports_directory, now + "_patient_report.txt")
        ensure_output_path_exists(filename)

        if num_wobblers > 0:
            #   Returns tuple of (success: bool, filename_actually_created: str)
            package: tuple = self.__redcap_writer.write(filename)

            if (
                isinstance(package, tuple)
                and len(package) > 1
                and isinstance(package[0], bool)
                and package[0]
                and isinstance(package[1], str)
            ):
                filename_created: str = package[1]
                self.__log.debug(f"Successfully created file '{filename_created}'.")
                return num_wobblers, filename_created
            else:
                self.__log.exception(
                    "***Unable to create file {file_name}. ***",
                    extra=dict(file_name=filename),
                )
                return num_wobblers, ""

        return num_wobblers, ""

    def __translate_decision(self, decision_enum: str) -> int:
        """Converts DecisionReview string into integer, using 'decisions' table.

        Returns
        -------
        id : int
        """

        if not self.__is_connected():  # pragma: no cover
            self.__log.error(
                "Called '__translate_decision' method but database is not connected."
            )
            raise RuntimeError(
                "Called '__translate_decision' method but database is not connected."
            )

        if (
            not isinstance(decision_enum, str) or len(decision_enum) == 0
        ):  # pragma: no cover
            self.__log.error('Input "crc_review" is not a string')
            raise TypeError('Input "crc_review" is not a string.')

        #   Strip off the 'DecisionReview.' part.
        decision_enum_payload = decision_enum.replace("DecisionReview.", "")
        query_sql = " SELECT id FROM decisions WHERE decision = (?); "
        cur = self.__connection.cursor()

        # pylint: disable=logging-fstring-interpolation
        try:
            cur.execute(query_sql, [decision_enum_payload])
            rows = cur.fetchall()
            return int(rows[0][0])
        except (
            sqlite3.IntegrityError,
            sqlite3.InternalError,
        ) as database_error:  # pragma: no cover
            self.__log.exception(
                "Error in running 'decisions' table query because {database_error}.",
                extra={"database_error": database_error},
            )
            raise database_error
