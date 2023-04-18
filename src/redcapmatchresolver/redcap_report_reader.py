"""
Module: contains class REDCapReportReader
used to parse a reviewed list of patient matches.
"""
from __future__ import annotations

import collections
import io
import os
import re
from enum import Enum

import pandas  # type: ignore[import]
from redcaputilities.logging import setup_logging

ReportLine = collections.namedtuple(
    "ReportLine", ["name", "epic_value", "redcap_value"]
)


class CrcReason(Enum):  # pylint: disable=too-few-public-methods
    """
    Why did the CRC decide two records are NOT the same patient?
    """

    FAMILY = 1
    SAME_ADDRESS = 2
    PARENT_CHILD = 3
    OTHER = 4

    @classmethod
    def convert(cls, decision: str) -> CrcReason:
        """Allow us to create a CrcReason object from a string.

        Parameters
        ----------
        decision : str  String like "NOT Same: Parent & child"

        Returns
        -------
        object : CrcReason object
        """
        if not isinstance(decision, str) or len(decision) == 0:
            raise TypeError("Input 'decisions' is not the expected string.")

        if "family members" in decision.lower():
            return CrcReason(CrcReason.FAMILY)

        if "same address" in decision.lower():
            return CrcReason(CrcReason.SAME_ADDRESS)

        if "parent" in decision.lower():
            return CrcReason(CrcReason.PARENT_CHILD)

        return CrcReason(CrcReason.OTHER)


class CrcReview(Enum):  # pylint: disable=too-few-public-methods
    """
    What did the CRC decide?
    Are these patient records from the same person or not?
    """

    # We want these numerically ordered so that the MATCH is highest, etc.
    # That way if we have one entry "MATCH" and one "NO_MATCH", the max is "MATCH".
    MATCH = 3
    NO_MATCH = 2
    NOT_SURE = 1

    @classmethod
    def convert(cls, decisions: str | list | tuple) -> CrcReview | list:
        """Allow us to create a CrcReview object from a string.

        Parameters
        ----------
        decisions : str  String like "MATCH" or "NO_MATCH"
                          -- OR --
                         list or tuple

        Returns
        -------
        object : CrcReview object or a list of such objects.
        """
        if decisions is None:
            raise TypeError(
                "Input 'decisions' is not the expected string, list or tuple."
            )

        if isinstance(decisions, list):
            decision_list = []

            for this_decision in decisions:
                decision_list.append(CrcReview.convert(this_decision))

            return decision_list

        if isinstance(decisions, tuple) and len(decisions) == 1:
            return CrcReview.convert(decisions[0])

        if not isinstance(decisions, str):
            raise TypeError("Input 'decisions' is not the expected string.")

        if decisions == "MATCH":
            return CrcReview(CrcReview.MATCH)

        if decisions == "NO_MATCH":
            return CrcReview(CrcReview.NO_MATCH)

        return CrcReview(CrcReview.NOT_SURE)

    def __eq__(self, other: object) -> bool:
        """Defines the == method."""
        if isinstance(other, CrcReview):
            same = self.value == other.value
            return same
        else:
            return NotImplemented

    def __gt__(self, other: object) -> bool:
        """Defines the > method."""
        if isinstance(other, CrcReview):
            more_than = self.value > other.value
            return more_than
        else:
            return NotImplemented

    def __lt__(self, other: object) -> bool:
        """Defines the < method."""
        if isinstance(other, CrcReview):
            less_than = self.value < other.value
            return less_than
        else:
            return NotImplemented


class REDCapReportReader:  # pylint: disable=too-few-public-methods
    """
    Parses formatted patient report.
    """

    __separator = "------"

    def __init__(self) -> None:
        self.__log = setup_logging(log_filename="redcap_report_reader.log")
        self.__report_contents = []  # type: ignore[var-annotated]
        self.__row_index = 0

    def __at_end(self) -> bool:
        """Are we at the END of the report?"""
        return self.__row_index >= len(self.__report_contents) - 1

    @staticmethod
    def __break_into_pieces(data_line: str) -> list:
        pieces = re.split(r"\s{2,}", data_line)

        # Get rid of empty strings.
        pieces[:] = [piece for piece in pieces if piece]
        return pieces

    @staticmethod
    def convert_nulls(value: str) -> str | None:
        """Turn strings that SAY 'NULL' into Python Nones that will become NULL db values.

        Parameters
        ----------
        value : str String to be converted.

        Returns
        -------
        value_converted : str or None
        """
        if not isinstance(value, str) or len(value) == 0:
            return None

        if value.upper() == "NULL":
            return None

        return value

    @staticmethod
    def _find_column(data_line: str, keyword: str) -> int:
        """Which column contains the keyword?

        Parameters
        ----------
        data_line : str Line from the report
        keyword : Desired keyword (like 'Epic Val')

        Returns
        -------
        index : int zero-based index of where in line the keyword appears.
        """
        pieces = REDCapReportReader.__break_into_pieces(data_line)

        if any(piece == keyword for piece in pieces):
            return pieces.index(keyword)

        raise RuntimeError(f"Unable to find '{keyword}' in line.")

    def __next_line(self) -> str | None:
        """Get the next line in the report, or None if no more available.

        Returns
        -------
        line : str (or None, if we're at the report end.)
        """
        if self.__at_end():
            return None

        self.__row_index += 1
        return str(self.__report_contents[self.__row_index])

    def __open_file(self, report_filename: str) -> None:
        """Handles opening the input file.

        Parameters
        ----------
        report_filename : str Full path to location of report.
        """
        # pylint: disable=logging-fstring-interpolation
        if os.path.exists(report_filename):
            #   Open as FILE.
            with open(file=report_filename, encoding="utf-8") as file_obj:
                # Read all the lines into a list.
                self.__report_contents = file_obj.readlines()
        else:
            self.__log.error(
                "Unable to find file {report_filename}.",
                extra={"report_filename": report_filename},
            )
            raise FileNotFoundError(f"Unable to find file '{report_filename}'.")

    def __open_text(self, block_txt: str) -> None:
        """Handles opening the input text block.

        Parameters
        ----------
        block_txt : str Multi-line block of text.
        """
        #   Open block of text AS IF it were a file.
        with io.StringIO(block_txt) as text_block:
            # Read all the lines into a list.
            self.__report_contents = text_block.readlines()

    @staticmethod
    def __parse_line(data_line: str, epic_index: int, redcap_index: int) -> ReportLine:
        """Reads a line like 'C_MRN   123    456' and returns the ReportLine named tuple
        with fields 'name': 'MRN', 'epic_value': 123, 'redcap_value': 456.

        Parameters
        ----------
        data_line : str   Entire report row
        epic_index : int Index of which column contains the Epic value
        redcap_index : int Index of which column contains the REDCap value

        Returns
        -------
        report_line_obj : ReportLine named tuple
        """
        pieces = REDCapReportReader.__break_into_pieces(data_line)
        variable_name = pieces[0].replace("C_", "").strip()

        epic_value = None
        redcap_value = None

        if epic_index < len(pieces):
            epic_value = pieces[epic_index]

        if redcap_index < len(pieces):
            redcap_value = pieces[redcap_index]

        return ReportLine(
            name=variable_name, epic_value=epic_value, redcap_value=redcap_value
        )

    def __read(self) -> pandas.DataFrame:
        """Parses the report & forms a pandas DataFrame from the text."""
        reviewed_matches = None
        match_index = 0

        #   Must be reset at every read.
        self.__row_index = 0

        next_line = self.__next_line()

        while True:
            #   Search through to the start of the next match pair.
            while next_line is not None and "Epic Val" not in next_line:
                next_line = self.__next_line()

            if next_line is None:
                break

            #   Figure out which column holds Epic, RedCap values.
            epic_index = REDCapReportReader._find_column(next_line, "Epic Val")
            redcap_index = REDCapReportReader._find_column(next_line, "RedCap Val")

            #   Initialize dictionary for this match.
            match_dict = {}

            #   Read/parse each row, staying alert for a new '------' line,
            #   meaning we've passed through to the end of the match.
            while (
                next_line is not None
                and REDCapReportReader.__separator not in next_line
            ):
                next_line = self.__next_line()

                if (
                    not isinstance(next_line, str)
                    or len(next_line) == 0
                    or REDCapReportReader.__separator in next_line
                ):
                    break

                this_line = REDCapReportReader.__parse_line(
                    data_line=next_line,
                    epic_index=epic_index,
                    redcap_index=redcap_index,
                )

                #   Don't insert strings that SAY 'NULL'.
                #   Convert to actual NULL value.
                match_dict["EPIC_" + this_line.name] = REDCapReportReader.convert_nulls(
                    this_line.epic_value
                )
                match_dict[
                    "REDCAP_" + this_line.name
                ] = REDCapReportReader.convert_nulls(this_line.redcap_value)

            #   Did we get here because we ran out of data?
            if not isinstance(next_line, str) or len(next_line) == 0:
                break

            #   Read "Same/Not Same" lines.
            crc_decision, crc_reason = self.__read_crc_decision()

            match_dict["CRC_DECISION"] = str(crc_decision)
            this_row_df = pandas.DataFrame(match_dict, index=[match_index])
            match_index += 1

            if reviewed_matches is None:
                reviewed_matches = this_row_df
            else:
                reviewed_matches = pandas.concat([reviewed_matches, this_row_df])

            #   Start reading next match report.
            next_line = self.__next_line()

        return reviewed_matches

    def __read_crc_decision(self) -> tuple:
        """From where we are in the report, find the "Same" or "Not Same" sections
        and figure out which one is checked.

        Returns
        -------
        decision, reason : tuple containing CrcReview, CrcReason objects
        """
        # https://fsymbols.com/signs/tick/
        positive_marks = r".xXyY✓✔√✅❎☒☑✕✗✘✖❌"
        crc_decision = None
        crc_reason = None

        #   We assume we've just read the final separator in this section
        #   and the Same/Not Same lines are close by.
        decision_line = self.__next_line()

        while (
            decision_line is not None
            and isinstance(decision_line, str)
            and "Same" not in decision_line
        ):
            decision_line = self.__next_line()

        if not isinstance(decision_line, str) or len(decision_line) == 0:
            return crc_decision, crc_reason

        #   Parse what we've found so far.
        same_checked = any(elem in decision_line for elem in positive_marks)

        if same_checked:
            crc_decision = CrcReview.MATCH
            return crc_decision, crc_reason

        #   Continue reading & until we find a  checkmark or the next separator line.
        decision_line = self.__next_line()

        while (
            decision_line is not None
            and isinstance(decision_line, str)
            and REDCapReportReader.__separator not in decision_line
            and not any(elem in decision_line for elem in positive_marks)
        ):
            decision_line = self.__next_line()

        #   Did we run out of lines before finding a checkmark?
        if (
            not isinstance(decision_line, str)
            or REDCapReportReader.__separator in decision_line
        ):
            return crc_decision, crc_reason

        #   Then we must have found a "NOT Same:" line checked.
        crc_decision = CrcReview.NO_MATCH
        crc_reason = CrcReason.convert(decision_line)
        return crc_decision, crc_reason

    def read_file(self, report_filename: str) -> pandas.DataFrame:
        """Lets user specify we are to open a FILE.

        Parameters
        ----------
        """
        if not isinstance(report_filename, str) or len(report_filename) == 0:
            raise TypeError("Argument 'report_filename' is not the expected str.")

        self.__open_file(report_filename=report_filename)
        return self.__read()

    def read_text(self, block_txt: str) -> pandas.DataFrame:
        """Lets user specify we are to open a BLOCK of TEXT."""
        if not isinstance(block_txt, str) or len(block_txt) == 0:
            raise TypeError("Argument 'block_txt' is not the expected str.")

        self.__open_text(block_txt=block_txt)
        return self.__read()


if __name__ == "__main__":
    pass
