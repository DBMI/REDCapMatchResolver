"""
Module: contains class REDCapReportReader
used to parse a reviewed list of patient matches.
"""
import collections
from enum import Enum
import io
import logging
import os
import re
from typing import List, Tuple, Union
import pandas
from .utilities import Utilities

ReportLine = collections.namedtuple(
    "ReportLine", ["name", "epic_value", "redcap_value"]
)


class CrcReview(Enum):  # pylint: disable=too-few-public-methods
    """
    What did the CRC decide? The same or not?
    """

    # We want these numerically ordered so that the MATCH is highest, etc.
    # That way if we have one entry "MATCH" and one "NO_MATCH", the max is "MATCH".
    MATCH = 3
    NO_MATCH = 2
    NOT_SURE = 1

    @classmethod
    def convert(cls, decisions: Union[str, List, Tuple] = None):
        """Allow us to create a CrcReview object from a string.

        Parameters
        ----------
        decisions : str  String like "MATCH" or "NO_MATCH"
                          -- OR --
                         List or Tuple

        Returns
        -------
        object : CrcReview object
        """
        if decisions is None:
            raise TypeError(
                "Input 'decisions' is not the expected string, list or tuple."
            )

        if isinstance(decisions, List):
            decision_list = []

            for this_decision in decisions:
                decision_list.append(CrcReview.convert(this_decision))

            return decision_list

        if isinstance(decisions, Tuple) and len(decisions) == 1:
            return CrcReview.convert(decisions[0])

        if not isinstance(decisions, str):
            raise TypeError("Input 'decisions' is not the expected string.")

        if decisions == "MATCH":
            return CrcReview.MATCH

        if decisions == "NO_MATCH":
            return CrcReview.NO_MATCH

        return CrcReview.NOT_SURE

    def __eq__(self, other) -> bool:
        """Defines the == method."""
        if isinstance(other, CrcReview):
            return self.value == other.value

        return False

    def __gt__(self, other) -> bool:
        """Defines the > method."""
        if isinstance(other, CrcReview):
            return self.value > other.value

        return False

    def __lt__(self, other) -> bool:
        """Defines the < method."""
        if isinstance(other, CrcReview):
            return self.value < other.value

        return False


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
    def convert_nulls(value: str) -> Union[str, None]:
        """Turn strings that SAY 'NULL' into Python Nones that will become NULL db values.

        Parameters
        ----------
        value : str String to be converted.

        Returns
        -------
        value_converted : str or None
        """
        if value is None or not isinstance(value, str):
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
        pieces = REDCapReportReader._break_into_pieces(data_line)

        if any(piece == keyword for piece in pieces):
            return pieces.index(keyword)

        raise RuntimeError(f"Unable to find '{keyword}' in line.")

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

    def _open_file(self, report_filename: str = None) -> None:
        """Handles opening the input file.

        Parameters
        ----------
        report_filename : str Full path to location of report.
        """
        if report_filename is None or not isinstance(report_filename, str):
            self.__log.error("Need to know the name of the report file to be read.")
            raise TypeError("Need to know the name of the report file to be read.")

        # pylint: disable=logging-fstring-interpolation
        if os.path.exists(report_filename):
            #   Open as FILE.
            with open(file=report_filename, encoding="utf-8") as file_obj:
                # Read all the lines into a list.
                self.__report_contents = file_obj.readlines()
        else:
            self.__log.error(f"Unable to find file '{report_filename}'.")
            raise FileNotFoundError(f"Unable to find file '{report_filename}'.")

    def _open_text(self, block_txt: str = None) -> None:
        """Handles opening the input text block.

        Parameters
        ----------
        block_txt : str Multi-line block of text.
        """
        if block_txt is None or not isinstance(block_txt, str):
            self.__log.error("Need to supply the text block to be read.")
            raise TypeError("Need to supply the text block to be read.")

        #   Open block of text AS IF it were a file.
        with io.StringIO(block_txt) as text_block:
            # Read all the lines into a list.
            self.__report_contents = text_block.readlines()

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

    def _read(self) -> pandas.DataFrame:
        """Parses the report & forms a pandas DataFrame from the text."""
        reviewed_matches = None
        separator = "------"
        match_index = 0

        #   Must be reset at every read.
        self.__row_index = 0

        next_line = self._next_line()

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

                #   Don't insert strings that SAY 'NULL'.
                #   Convert to actual NULL value.
                match_dict["EPIC_" + this_line.name] = REDCapReportReader.convert_nulls(
                    this_line.epic_value
                )
                match_dict[
                    "REDCAP_" + this_line.name
                ] = REDCapReportReader.convert_nulls(this_line.redcap_value)

            #   Did we get here because we ran out of data?
            if next_line is None or not isinstance(next_line, str):
                break

            #   Read "Same/Not Same" lines.
            crc_decision = self._read_crc_decision()

            match_dict["CRC_DECISION"] = str(crc_decision)
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
            return CrcReview.MATCH

        if not same_checked and different_checked:
            return CrcReview.NO_MATCH

        return None

    def read_file(self, report_filename: str = None) -> pandas.DataFrame:
        """Lets user specify we are to open a FILE.

        Parameters
        ----------
        """
        self._open_file(report_filename=report_filename)
        return self._read()

    def read_text(self, block_txt: str = None) -> pandas.DataFrame:
        """Lets user specify we are to open a BLOCK of TEXT."""
        self._open_text(block_txt=block_txt)
        return self._read()


if __name__ == "__main__":
    pass
