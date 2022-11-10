"""
Module: contains class REDCapReportReader
used to parse a reviewed list of patient matches.
"""
import collections
from enum import Enum
import logging
import os
import re
from typing import Union
import pandas
from .utilities import Utilities

ReportLine = collections.namedtuple(
    "ReportLine", ["name", "epic_value", "redcap_value"]
)


class CrcReview(Enum):  # pylint: disable=too-few-public-methods
    """
    What did the CRC decide? The same or not?
    """

    SAME = 1
    NOT_SAME = 2


class REDCapReportReader:  # pylint: disable=too-few-public-methods
    """
    Parses formatted patient report.
    """

    def __init__(self):
        Utilities.setup_logging()
        self.__log = logging.getLogger(__name__)
        self.__report_contents = None
        self.__row_index = 0

    def _at_end(self) -> bool:
        """Are we at the END of the report?"""
        return self.__row_index >= len(self.__report_contents) - 1

    @staticmethod
    def _break_into_pieces(data_line: str) -> list:
        pieces = re.split(r"\s{2,}", data_line)

        # Get rid of empty strings.
        pieces[:] = [piece for piece in pieces if piece]
        return pieces

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
        pieces = REDCapReportReader._break_into_pieces(data_line)

        if any(piece == keyword for piece in pieces):
            return pieces.index(keyword)

        raise RuntimeError(f"Unable to find '{keyword}' in line.")

    @staticmethod
    def _parse_line(data_line: str, epic_index: int, redcap_index: int) -> ReportLine:
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
        pieces = REDCapReportReader._break_into_pieces(data_line)
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

    def _next_line(self) -> Union[str, None]:
        """Get the next line in the report, or None if no more available.

        Returns
        -------
        line : str (or None, if we're at the report end.)
        """
        if self._at_end():
            return None

        self.__row_index += 1
        return self.__report_contents[self.__row_index]

    def _open(self, report_filename: str = None) -> None:
        """Handles opening the input file.

        Parameters
        ----------
        report_filename : str Full path to location of report to be read.
        """
        if report_filename is None or not isinstance(report_filename, str):
            self.__log.error("Need to know the name of the report file to be read.")
            raise TypeError("Need to know the name of the report file to be read.")

        # pylint: disable=logging-fstring-interpolation
        if not os.path.exists(report_filename):
            self.__log.error(f"Unable to find file '{report_filename}'.")
            raise FileNotFoundError(f"Unable to find file '{report_filename}'.")

        # pylint: disable=logging-fstring-interpolation
        self.__log.info(f"Initialized with report filename '{report_filename}'.")
        self.__report_contents = None
        self.__row_index = 0

        with open(file=report_filename, encoding="utf-8") as file_obj:
            #   Reads all the lines into a list.
            self.__report_contents = file_obj.readlines()

    def read(self, report_filename: str = None) -> pandas.DataFrame:
        """Parses the report & forms a pandas DataFrame from the text.

        Parameters
        ----------
        report_filename : str Full path to location of report to be read.
        """
        self._open(report_filename)
        reviewed_matches = None
        separator = "------"
        next_line = self._next_line()
        match_index = 0

        while True:
            #   Search through to the start of the next match pair.
            while next_line is not None and separator not in next_line:
                next_line = self._next_line()

            #   Do we still have data?
            if next_line is not None:
                next_line = self._next_line()

            if next_line is None:
                break

            #   Figure out which column holds Epic, RedCap values.
            epic_index = REDCapReportReader._find_column(next_line, "Epic Val")
            redcap_index = REDCapReportReader._find_column(next_line, "RedCap Val")

            #   Initialize dictionary for this match.
            match_dict = {}

            #   Read/parse each row, staying alert for a new '------' line,
            #   meaning we've passed through to the next match.
            while next_line is not None and separator not in next_line:
                next_line = self._next_line()

                if (
                    next_line is None
                    or not isinstance(next_line, str)
                    or separator in next_line
                ):
                    break

                this_line = REDCapReportReader._parse_line(
                    data_line=next_line,
                    epic_index=epic_index,
                    redcap_index=redcap_index,
                )
                match_dict["EPIC_" + this_line.name] = this_line.epic_value
                match_dict["REDCAP_" + this_line.name] = this_line.redcap_value

            #   Did we get here because we ran out of data?
            if next_line is None or not isinstance(next_line, str):
                break

            #   Read "Same/Not Same" lines.
            crc_decision = self._read_crc_decision()

            if crc_decision is None:
                #   Then there was no decision recorded.
                next_line = self._next_line()
                continue

            match_dict["crc_decision"] = str(crc_decision)
            this_row_df = pandas.DataFrame(match_dict, index=[match_index])
            match_index += 1

            if reviewed_matches is None:
                reviewed_matches = this_row_df
            else:
                reviewed_matches = pandas.concat([reviewed_matches, this_row_df])

            #   Start reading next match report.
            next_line = self._next_line()

        return reviewed_matches

    def _read_crc_decision(self) -> Union[CrcReview, None]:
        """From where we are in the report, find the "Same" or "Not Same" sections
        and figure out which one is checked.

        Returns
        -------
        decision : CrcReview object
        """
        # https://fsymbols.com/signs/tick/
        positive_marks = r".xXyY✓✔√✅❎☒☑✕✗✘✖❌"

        #   We assume we've just read the final separator in this section
        #   and the Same/Not Same lines are close.
        same_line = self._next_line()

        while (
            same_line is not None
            and isinstance(same_line, str)
            and "Same" not in same_line
        ):
            same_line = self._next_line()

        if same_line is None or not isinstance(same_line, str):
            return None

        different_line = self._next_line()

        if different_line is None or not isinstance(different_line, str):
            return None

        same_checked = any(elem in same_line for elem in positive_marks)
        different_checked = any(elem in different_line for elem in positive_marks)

        if same_checked and not different_checked:
            return CrcReview.SAME

        if not same_checked and different_checked:
            return CrcReview.NOT_SAME

        return None


if __name__ == "__main__":
    pass
